from __future__ import annotations

from typing import Any
from typing import Literal

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float | None = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, gt=0.0, le=1.0)
    max_completion_tokens: int | None = Field(default=None, ge=1)
    frequency_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    presence_penalty: float | None = Field(default=None, ge=-2.0, le=2.0)
    timeout_seconds: float | None = Field(default=60.0, gt=0.0)
    extra_params: dict[str, Any] = Field(default_factory=dict)

    def to_openai_chat_params(self) -> dict[str, Any]:
        params: dict[str, Any] = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_completion_tokens": self.max_completion_tokens,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "timeout": self.timeout_seconds,
        }
        cleaned = {k: v for k, v in params.items() if v is not None}
        for key, value in self.extra_params.items():
            if value is not None:
                cleaned[key] = value
        return cleaned


class RuntimeConfig(BaseModel):
    seed: int = 7
    max_steps: int = Field(default=8, ge=1)
    dynamic_replanning: bool = True
    use_cot: bool = False
    agentic_mode: Literal["codeact", "react"] = "codeact"
    save_artifacts: bool = True
    artifact_dir: str = "artifacts/reports"
