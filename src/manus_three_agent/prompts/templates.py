from __future__ import annotations

from pathlib import Path
from typing import Any

from manus_three_agent.utils.io import load_yaml


class PromptTemplates:
    def __init__(self, config_dir: str = "configs/prompts") -> None:
        self.config_dir = Path(config_dir)

    def get(self, role: str) -> dict[str, str]:
        data = load_yaml(str(self.config_dir / f"{role}.yaml"))
        return {
            "system": str(data.get("system", "")),
            "user_template": str(data.get("user_template", "")),
        }

    def render(self, role: str, **kwargs: Any) -> tuple[str, str]:
        prompt_cfg = self.get(role)
        system_prompt = prompt_cfg["system"]
        user_template = prompt_cfg["user_template"]
        return system_prompt, user_template.format(**kwargs)
