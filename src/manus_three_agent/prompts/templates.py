from __future__ import annotations

from pathlib import Path
from typing import Any

from manus_three_agent.utils.io import load_yaml


class PromptTemplates:
    def __init__(
        self,
        config_dir: str = "configs/prompts",
        role_overrides: dict[str, dict[str, Any]] | None = None,
        shared_context: dict[str, Any] | None = None,
    ) -> None:
        self.config_dir = Path(config_dir)
        self.role_overrides = role_overrides or {}
        self.shared_context = shared_context or {}

    def get(self, role: str) -> dict[str, str]:
        data = load_yaml(str(self.config_dir / f"{role}.yaml"))
        override = self.role_overrides.get(role, {})
        system = str(override.get("system", data.get("system", "")))
        user_template = str(override.get("user_template", data.get("user_template", "")))
        return {
            "system": system,
            "user_template": user_template,
        }

    def render(self, role: str, **kwargs: Any) -> tuple[str, str]:
        prompt_cfg = self.get(role)
        system_template = prompt_cfg["system"]
        user_template = prompt_cfg["user_template"]
        render_args = {
            **self.shared_context,
            **kwargs,
        }
        try:
            return system_template.format(**render_args), user_template.format(**render_args)
        except KeyError as exc:
            missing = str(exc).strip("'")
            raise ValueError(f"Missing prompt variable '{missing}' for role '{role}'") from exc
