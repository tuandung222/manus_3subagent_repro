from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import typer
from dotenv import load_dotenv
from rich import print

from manus_three_agent.agents import ArchitectAgent, CriticAgent, WorkerAgent
from manus_three_agent.core import EpisodeArtifact, ModelConfig, RuntimeConfig, build_initial_state
from manus_three_agent.environments import build_environment
from manus_three_agent.eval.metrics import compute_episode_metrics
from manus_three_agent.graph import build_workflow
from manus_three_agent.prompts import PromptTemplates, get_mode_prompt_profile
from manus_three_agent.tools import build_default_tool_registry
from manus_three_agent.tracing import TraceCollector, TraceConfig
from manus_three_agent.training import build_trajectory_dataset
from manus_three_agent.utils import load_yaml, set_seed, write_json

app = typer.Typer(no_args_is_help=True)
ROLE_NAMES = ("architect", "worker", "critic")


@app.callback()
def main() -> None:
    """Run Manus-style 3-subagent experiments and data export."""


def _load_runtime_config(path: str) -> RuntimeConfig:
    return RuntimeConfig.model_validate(load_yaml(path))


def _load_trace_config(path: str) -> TraceConfig:
    return TraceConfig.model_validate(load_yaml(path))


def _load_optional_yaml(path: str) -> dict[str, Any]:
    if not path.strip():
        return {}

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    payload = load_yaml(str(file_path))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in file: {path}")
    return payload


def _deep_merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _merge_role_overrides(
    base: dict[str, dict[str, Any]],
    override: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {role: dict(values) for role, values in base.items()}
    for role, values in override.items():
        if role in merged:
            merged[role] = _deep_merge_dict(merged[role], values)
        else:
            merged[role] = dict(values)
    return merged


def _build_inline_model_overrides(
    *,
    architect_model: str,
    worker_model: str,
    critic_model: str,
    architect_temperature: float | None,
    worker_temperature: float | None,
    critic_temperature: float | None,
    architect_top_p: float | None,
    worker_top_p: float | None,
    critic_top_p: float | None,
    architect_max_completion_tokens: int | None,
    worker_max_completion_tokens: int | None,
    critic_max_completion_tokens: int | None,
) -> dict[str, Any]:
    overrides: dict[str, dict[str, Any]] = {
        "architect": {},
        "worker": {},
        "critic": {},
    }

    def _set(role: str, key: str, value: Any) -> None:
        if value is None:
            return
        if isinstance(value, str) and not value.strip():
            return
        overrides[role][key] = value

    _set("architect", "model", architect_model)
    _set("worker", "model", worker_model)
    _set("critic", "model", critic_model)

    _set("architect", "temperature", architect_temperature)
    _set("worker", "temperature", worker_temperature)
    _set("critic", "temperature", critic_temperature)

    _set("architect", "top_p", architect_top_p)
    _set("worker", "top_p", worker_top_p)
    _set("critic", "top_p", critic_top_p)

    _set("architect", "max_completion_tokens", architect_max_completion_tokens)
    _set("worker", "max_completion_tokens", worker_max_completion_tokens)
    _set("critic", "max_completion_tokens", critic_max_completion_tokens)

    return {role: values for role, values in overrides.items() if values}


def _load_model_configs(
    path: str,
    model_override: str = "",
    inline_overrides: dict[str, Any] | None = None,
) -> dict[str, ModelConfig]:
    payload = load_yaml(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in model config: {path}")

    if model_override.strip():
        payload = _deep_merge_dict(payload, _load_optional_yaml(model_override))

    if inline_overrides:
        payload = _deep_merge_dict(payload, inline_overrides)

    return {
        role: ModelConfig.model_validate(payload.get(role, {}))
        for role in ROLE_NAMES
    }


def _load_prompt_overrides(path: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if not path.strip():
        return {}, {}

    payload = _load_optional_yaml(path)
    role_overrides: dict[str, dict[str, Any]] = {}
    shared_context: dict[str, Any] = {}

    shared = payload.get("shared", {})
    if isinstance(shared, dict):
        shared_context = dict(shared)

    if "roles" in payload and isinstance(payload.get("roles"), dict):
        roles_block = payload.get("roles", {})
        for role in ROLE_NAMES:
            role_payload = roles_block.get(role)
            if isinstance(role_payload, dict):
                role_overrides[role] = role_payload
    else:
        for role in ROLE_NAMES:
            role_payload = payload.get(role)
            if isinstance(role_payload, dict):
                role_overrides[role] = role_payload

    return role_overrides, shared_context


@app.command("run-episode")
def run_episode(
    goal: str = typer.Option(..., help="User goal/instruction."),
    base_config: str = typer.Option("configs/base.yaml", help="Path to base runtime config."),
    model_config: str = typer.Option("configs/models.yaml", help="Path to base model config."),
    model_override: str = typer.Option("", help="Optional YAML overrides for model hyperparameters."),
    prompts_dir: str = typer.Option("configs/prompts", help="Prompt template directory."),
    prompt_override: str = typer.Option("", help="Optional YAML overrides for prompts."),
    prompt_context: str = typer.Option("", help="Optional YAML with extra prompt variables."),
    trace_config: str = typer.Option("configs/tracing.yaml", help="Path to tracing config."),
    trace: bool = typer.Option(False, help="Enable runtime trace logging for this run."),
    mock: bool = typer.Option(False, help="Force mock subagent outputs and skip model calls."),
    environment: str = typer.Option("simulator", help="Environment adapter: simulator"),
    dynamic_replanning: bool = typer.Option(True, help="Enable replan route from critic."),
    use_cot: bool = typer.Option(False, help="Enable CoT hints in prompts."),
    agentic_mode: str = typer.Option("", help="Agentic execution mode: codeact|react."),
    seed: int | None = typer.Option(None, help="Optional runtime seed override."),
    max_steps: int | None = typer.Option(None, help="Optional max-steps override."),
    architect_model: str = typer.Option("", help="Quick override for architect model name."),
    worker_model: str = typer.Option("", help="Quick override for worker model name."),
    critic_model: str = typer.Option("", help="Quick override for critic model name."),
    architect_temperature: float | None = typer.Option(None, help="Quick override for architect temperature."),
    worker_temperature: float | None = typer.Option(None, help="Quick override for worker temperature."),
    critic_temperature: float | None = typer.Option(None, help="Quick override for critic temperature."),
    architect_top_p: float | None = typer.Option(None, help="Quick override for architect top_p."),
    worker_top_p: float | None = typer.Option(None, help="Quick override for worker top_p."),
    critic_top_p: float | None = typer.Option(None, help="Quick override for critic top_p."),
    architect_max_completion_tokens: int | None = typer.Option(None, help="Quick override for architect max_completion_tokens."),
    worker_max_completion_tokens: int | None = typer.Option(None, help="Quick override for worker max_completion_tokens."),
    critic_max_completion_tokens: int | None = typer.Option(None, help="Quick override for critic max_completion_tokens."),
    print_effective_config: bool = typer.Option(False, help="Print merged runtime/model/prompt config before execution."),
) -> None:
    load_dotenv()

    runtime_cfg = _load_runtime_config(base_config)
    trace_cfg = _load_trace_config(trace_config)

    mode_override = agentic_mode.strip().lower()
    effective_mode = mode_override or runtime_cfg.agentic_mode
    if effective_mode not in {"codeact", "react"}:
        raise ValueError(f"Unsupported agentic_mode '{effective_mode}'. Use codeact or react.")

    inline_model_overrides = _build_inline_model_overrides(
        architect_model=architect_model,
        worker_model=worker_model,
        critic_model=critic_model,
        architect_temperature=architect_temperature,
        worker_temperature=worker_temperature,
        critic_temperature=critic_temperature,
        architect_top_p=architect_top_p,
        worker_top_p=worker_top_p,
        critic_top_p=critic_top_p,
        architect_max_completion_tokens=architect_max_completion_tokens,
        worker_max_completion_tokens=worker_max_completion_tokens,
        critic_max_completion_tokens=critic_max_completion_tokens,
    )
    model_cfgs = _load_model_configs(
        model_config,
        model_override=model_override,
        inline_overrides=inline_model_overrides,
    )

    mode_role_overrides, mode_shared_prompt_context = get_mode_prompt_profile(effective_mode)
    user_role_prompt_overrides, user_shared_prompt_context = _load_prompt_overrides(prompt_override)
    extra_prompt_context = _load_optional_yaml(prompt_context) if prompt_context.strip() else {}
    merged_role_prompt_overrides = _merge_role_overrides(mode_role_overrides, user_role_prompt_overrides)
    merged_shared_prompt_context = _deep_merge_dict(mode_shared_prompt_context, user_shared_prompt_context)
    merged_shared_prompt_context = _deep_merge_dict(merged_shared_prompt_context, extra_prompt_context)

    if trace:
        trace_cfg.enabled = True

    runtime_updates: dict[str, Any] = {
        "dynamic_replanning": dynamic_replanning,
        "use_cot": use_cot,
        "agentic_mode": effective_mode,
    }
    if seed is not None:
        runtime_updates["seed"] = seed
    if max_steps is not None:
        runtime_updates["max_steps"] = max_steps
    runtime_cfg = runtime_cfg.model_copy(update=runtime_updates)

    if print_effective_config:
        print(
            {
                "runtime": runtime_cfg.model_dump(),
                "models": {role: model_cfgs[role].model_dump() for role in ROLE_NAMES},
                "prompts": {
                    "agentic_mode": runtime_cfg.agentic_mode,
                    "prompts_dir": prompts_dir,
                    "prompt_override": prompt_override,
                    "prompt_context": prompt_context,
                    "roles_with_override": sorted(merged_role_prompt_overrides.keys()),
                },
            }
        )

    set_seed(runtime_cfg.seed)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tracer = TraceCollector(config=trace_cfg, run_id=run_id)
    env_adapter = build_environment(environment)

    prompts = PromptTemplates(
        config_dir=prompts_dir,
        role_overrides=merged_role_prompt_overrides,
        shared_context=merged_shared_prompt_context,
    )
    tools = build_default_tool_registry()

    architect = ArchitectAgent(
        model_cfgs["architect"],
        prompts,
        tracer=tracer,
        force_mock=mock,
        agentic_mode=runtime_cfg.agentic_mode,
    )
    worker = WorkerAgent(
        model_cfgs["worker"],
        prompts,
        tools,
        tracer=tracer,
        force_mock=mock,
        agentic_mode=runtime_cfg.agentic_mode,
    )
    critic = CriticAgent(
        model_cfgs["critic"],
        prompts,
        tracer=tracer,
        force_mock=mock,
        agentic_mode=runtime_cfg.agentic_mode,
    )

    tracer.start_session(
        goal=goal,
        environment={"kind": environment, "name": env_adapter.name},
        model_stack={role: model_cfgs[role].model_dump() for role in ROLE_NAMES},
        runtime_config=runtime_cfg.model_dump(),
        metadata={
            "mock": mock,
            "agentic_mode": runtime_cfg.agentic_mode,
            "framework": "langgraph",
            "architecture": "3-subagent-architect-worker-critic",
            "prompts_dir": prompts_dir,
            "prompt_override": prompt_override,
            "prompt_context": prompt_context,
            "model_override": model_override,
            "inline_model_overrides": inline_model_overrides,
        },
    )

    workflow = build_workflow(architect, worker, critic, env_adapter, tracer)

    initial_state = build_initial_state(
        goal=goal,
        max_steps=runtime_cfg.max_steps,
        dynamic_replanning=runtime_cfg.dynamic_replanning,
        use_cot=runtime_cfg.use_cot,
        agentic_mode=runtime_cfg.agentic_mode,
        observation=env_adapter.reset(goal=goal),
    )

    try:
        final_state: dict[str, Any] = workflow.invoke(initial_state)
    except Exception as exc:
        tracer.log_event(
            event_type="episode_error",
            step=initial_state["step_count"],
            payload={"error_type": type(exc).__name__, "error_message": str(exc)},
        )
        tracer.close(
            status="failed",
            summary={"error_type": type(exc).__name__, "error_message": str(exc)},
        )
        raise

    metrics = compute_episode_metrics(final_state)
    tracer.log_event(
        event_type="episode_end",
        step=int(final_state.get("step_count", 0)),
        payload={
            "success": bool(final_state.get("success", False)),
            "final_answer": str(final_state.get("final_answer", "")),
            "metrics": metrics,
        },
    )
    tracer.close(
        status="completed",
        summary={
            "success": bool(final_state.get("success", False)),
            "step_count": int(final_state.get("step_count", 0)),
            "metrics": metrics,
        },
    )

    artifact = EpisodeArtifact(
        run_id=run_id,
        goal=goal,
        success=bool(final_state.get("success", False)),
        step_count=int(final_state.get("step_count", 0)),
        final_answer=str(final_state.get("final_answer", "")),
        action_history=list(final_state.get("action_history", [])),
        review_history=list(final_state.get("review_history", [])),
        notes=list(final_state.get("notes", [])),
    )

    if runtime_cfg.save_artifacts:
        out_dir = Path(runtime_cfg.artifact_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            out_dir / f"episode_{run_id}.json",
            {
                "config": runtime_cfg.model_dump(),
                "model": {role: model_cfgs[role].model_dump() for role in ROLE_NAMES},
                "environment": {
                    "name": env_adapter.name,
                    "kind": environment,
                },
                "prompts": {
                    "agentic_mode": runtime_cfg.agentic_mode,
                    "prompts_dir": prompts_dir,
                    "prompt_override": prompt_override,
                    "prompt_context": prompt_context,
                },
                "metrics": metrics,
                "final_state": final_state,
                "artifact": artifact.model_dump(),
            },
        )

    print("[bold green]Episode finished[/bold green]")
    print(
        {
            "success": artifact.success,
            "step_count": artifact.step_count,
            "final_answer": artifact.final_answer,
            "metrics": metrics,
            "environment": env_adapter.name,
            "trace_enabled": trace_cfg.enabled,
            "trace_run_id": run_id if trace_cfg.enabled else "",
            "mock_mode": mock,
            "agentic_mode": runtime_cfg.agentic_mode,
        }
    )


@app.command("build-trajectories")
def build_trajectories(
    trace_dir: str = typer.Option("artifacts/traces", help="Trace directory root."),
    output: str = typer.Option("data/processed/trajectory_sft.jsonl", help="Output jsonl path."),
) -> None:
    summary = build_trajectory_dataset(trace_dir=trace_dir, output_path=output)
    print("[bold green]Trajectory dataset built[/bold green]")
    print(summary)


def run_cli() -> None:
    app()


if __name__ == "__main__":
    run_cli()
