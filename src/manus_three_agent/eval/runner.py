from __future__ import annotations

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
from manus_three_agent.prompts import PromptTemplates
from manus_three_agent.tools import build_default_tool_registry
from manus_three_agent.tracing import TraceCollector, TraceConfig
from manus_three_agent.training import build_trajectory_dataset
from manus_three_agent.utils import load_yaml, set_seed, write_json

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Run Manus-style 3-subagent experiments and data export."""


def _load_runtime_config(path: str) -> RuntimeConfig:
    return RuntimeConfig.model_validate(load_yaml(path))


def _load_model_configs(path: str) -> dict[str, ModelConfig]:
    data = load_yaml(path)
    return {
        "architect": ModelConfig.model_validate(data.get("architect", {})),
        "worker": ModelConfig.model_validate(data.get("worker", {})),
        "critic": ModelConfig.model_validate(data.get("critic", {})),
    }


def _load_trace_config(path: str) -> TraceConfig:
    return TraceConfig.model_validate(load_yaml(path))


@app.command("run-episode")
def run_episode(
    goal: str = typer.Option(..., help="User goal/instruction."),
    base_config: str = typer.Option("configs/base.yaml", help="Path to base runtime config."),
    model_config: str = typer.Option("configs/models.yaml", help="Path to model config."),
    trace_config: str = typer.Option("configs/tracing.yaml", help="Path to tracing config."),
    trace: bool = typer.Option(False, help="Enable runtime trace logging for this run."),
    mock: bool = typer.Option(False, help="Force mock subagent outputs and skip model calls."),
    environment: str = typer.Option("simulator", help="Environment adapter: simulator"),
    dynamic_replanning: bool = typer.Option(True, help="Enable replan route from critic."),
    use_cot: bool = typer.Option(False, help="Enable CoT hints in prompts."),
) -> None:
    load_dotenv()

    runtime_cfg = _load_runtime_config(base_config)
    model_cfgs = _load_model_configs(model_config)
    trace_cfg = _load_trace_config(trace_config)

    if trace:
        trace_cfg.enabled = True

    runtime_cfg = runtime_cfg.model_copy(
        update={
            "dynamic_replanning": dynamic_replanning,
            "use_cot": use_cot,
        }
    )

    set_seed(runtime_cfg.seed)

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tracer = TraceCollector(config=trace_cfg, run_id=run_id)
    env_adapter = build_environment(environment)

    prompts = PromptTemplates(config_dir="configs/prompts")
    tools = build_default_tool_registry()

    architect = ArchitectAgent(model_cfgs["architect"], prompts, tracer=tracer, force_mock=mock)
    worker = WorkerAgent(model_cfgs["worker"], prompts, tools, tracer=tracer, force_mock=mock)
    critic = CriticAgent(model_cfgs["critic"], prompts, tracer=tracer, force_mock=mock)

    tracer.start_session(
        goal=goal,
        environment={"kind": environment, "name": env_adapter.name},
        model_stack={
            "architect": model_cfgs["architect"].model_dump(),
            "worker": model_cfgs["worker"].model_dump(),
            "critic": model_cfgs["critic"].model_dump(),
        },
        runtime_config=runtime_cfg.model_dump(),
        metadata={
            "mock": mock,
            "framework": "langgraph",
            "architecture": "3-subagent-architect-worker-critic",
        },
    )

    workflow = build_workflow(architect, worker, critic, env_adapter, tracer)

    initial_state = build_initial_state(
        goal=goal,
        max_steps=runtime_cfg.max_steps,
        dynamic_replanning=runtime_cfg.dynamic_replanning,
        use_cot=runtime_cfg.use_cot,
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
                "model": {
                    "architect": model_cfgs["architect"].model_dump(),
                    "worker": model_cfgs["worker"].model_dump(),
                    "critic": model_cfgs["critic"].model_dump(),
                },
                "environment": {
                    "name": env_adapter.name,
                    "kind": environment,
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
