from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    title: str
    rationale: str = ""


class PlanOutput(BaseModel):
    steps: list[PlanStep] = Field(default_factory=list)


class ToolRequest(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class WorkerOutput(BaseModel):
    summary: str
    output: str
    is_final: bool = False
    final_answer: str = ""
    tool_requests: list[ToolRequest] = Field(default_factory=list)


class CriticOutput(BaseModel):
    decision: Literal["continue", "replan", "end"]
    feedback: str = ""
    should_succeed: bool = False


class EpisodeArtifact(BaseModel):
    run_id: str
    goal: str
    success: bool
    step_count: int
    final_answer: str
    action_history: list[dict[str, Any]] = Field(default_factory=list)
    review_history: list[dict[str, Any]] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
