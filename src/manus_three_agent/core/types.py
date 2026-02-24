from __future__ import annotations

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    temperature: float = 0.2


class RuntimeConfig(BaseModel):
    seed: int = 7
    max_steps: int = Field(default=8, ge=1)
    dynamic_replanning: bool = True
    use_cot: bool = False
    save_artifacts: bool = True
    artifact_dir: str = "artifacts/reports"
