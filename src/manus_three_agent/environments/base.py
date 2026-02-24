from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, Field

from manus_three_agent.core.schemas import WorkerOutput


class EnvironmentStepResult(BaseModel):
    observation: str
    done: bool = False
    success: bool = False
    final_answer: str = ""
    notes: list[str] = Field(default_factory=list)


class EnvironmentAdapter(Protocol):
    name: str

    def reset(self, *, goal: str) -> str:
        ...

    def step(self, *, action: WorkerOutput, step_count: int) -> EnvironmentStepResult:
        ...
