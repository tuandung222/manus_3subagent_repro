from pathlib import Path

import yaml

from manus_three_agent.core.types import ModelConfig
from manus_three_agent.eval.runner import _build_inline_model_overrides, _load_model_configs, _load_prompt_overrides
from manus_three_agent.prompts import PromptTemplates, get_mode_prompt_profile


def _write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload), encoding="utf-8")


def test_model_config_to_openai_chat_params_filters_none() -> None:
    cfg = ModelConfig(
        model="gpt-4.1-mini",
        temperature=0.3,
        top_p=None,
        max_completion_tokens=500,
        frequency_penalty=0.1,
        presence_penalty=None,
        timeout_seconds=30,
        extra_params={"parallel_tool_calls": False, "unused": None},
    )

    out = cfg.to_openai_chat_params()
    assert out["temperature"] == 0.3
    assert out["max_completion_tokens"] == 500
    assert out["frequency_penalty"] == 0.1
    assert out["timeout"] == 30
    assert out["parallel_tool_calls"] is False
    assert "top_p" not in out
    assert "presence_penalty" not in out
    assert "unused" not in out


def test_load_model_configs_with_file_and_inline_overrides(tmp_path: Path) -> None:
    base_path = tmp_path / "models.yaml"
    override_path = tmp_path / "override.yaml"

    _write_yaml(
        base_path,
        {
            "architect": {"model": "gpt-4.1-mini", "temperature": 0.2},
            "worker": {"model": "gpt-4.1-mini", "temperature": 0.1},
            "critic": {"model": "gpt-4.1-mini", "temperature": 0.0},
        },
    )
    _write_yaml(
        override_path,
        {
            "architect": {"top_p": 0.8},
            "worker": {"max_completion_tokens": 900},
        },
    )

    inline = _build_inline_model_overrides(
        architect_model="gpt-4.1",
        worker_model="",
        critic_model="",
        architect_temperature=0.15,
        worker_temperature=None,
        critic_temperature=None,
        architect_top_p=None,
        worker_top_p=None,
        critic_top_p=None,
        architect_max_completion_tokens=None,
        worker_max_completion_tokens=None,
        critic_max_completion_tokens=400,
    )

    cfgs = _load_model_configs(str(base_path), model_override=str(override_path), inline_overrides=inline)

    assert cfgs["architect"].model == "gpt-4.1"
    assert cfgs["architect"].temperature == 0.15
    assert cfgs["architect"].top_p == 0.8
    assert cfgs["worker"].max_completion_tokens == 900
    assert cfgs["critic"].max_completion_tokens == 400


def test_prompt_templates_support_overrides_and_shared_context(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompts"

    _write_yaml(
        prompts_dir / "architect.yaml",
        {
            "system": "BASE {company}",
            "user_template": "Goal: {goal}",
        },
    )

    prompts = PromptTemplates(
        config_dir=str(prompts_dir),
        role_overrides={
            "architect": {
                "system": "OVERRIDE {company}",
                "user_template": "Goal: {goal} / Lang: {lang}",
            }
        },
        shared_context={
            "company": "ACME",
            "lang": "vi",
        },
    )

    system, user = prompts.render("architect", goal="Test")

    assert system == "OVERRIDE ACME"
    assert user == "Goal: Test / Lang: vi"


def test_prompt_templates_missing_variable_raises(tmp_path: Path) -> None:
    prompts_dir = tmp_path / "prompts"

    _write_yaml(
        prompts_dir / "critic.yaml",
        {
            "system": "Critic",
            "user_template": "Need: {missing_key}",
        },
    )

    prompts = PromptTemplates(config_dir=str(prompts_dir))

    try:
        prompts.render("critic", goal="x")
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "missing_key" in str(exc)


def test_prompt_overrides_support_root_style_file(tmp_path: Path) -> None:
    override_path = tmp_path / "prompt_override.yaml"
    _write_yaml(
        override_path,
        {
            "shared": {"lang": "vi"},
            "architect": {"system": "A", "user_template": "B"},
        },
    )

    role_overrides, shared_context = _load_prompt_overrides(str(override_path))

    assert "architect" in role_overrides
    assert role_overrides["architect"]["system"] == "A"
    assert shared_context["lang"] == "vi"


def test_mode_prompt_profile_supports_codeact_and_react() -> None:
    codeact_overrides, codeact_shared = get_mode_prompt_profile("codeact")
    react_overrides, react_shared = get_mode_prompt_profile("react")

    assert codeact_shared["agentic_mode"] == "codeact"
    assert react_shared["agentic_mode"] == "react"
    assert "worker" in codeact_overrides
    assert "worker" in react_overrides
