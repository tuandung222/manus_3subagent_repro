from __future__ import annotations

from typing import Any, TypedDict


class ManusState(TypedDict):
    goal: str
    observation: str
    plan: list[dict[str, Any]]
    current_step_idx: int
    action_history: list[dict[str, Any]]
    review_history: list[dict[str, Any]]
    latest_action: dict[str, Any]
    step_count: int
    max_steps: int
    done: bool
    success: bool
    final_answer: str
    decision: str
    notes: list[str]
    dynamic_replanning: bool
    use_cot: bool
    agentic_mode: str


def build_initial_state(
    *,
    goal: str,
    observation: str,
    max_steps: int,
    dynamic_replanning: bool,
    use_cot: bool,
    agentic_mode: str,
) -> ManusState:
    return ManusState(
        goal=goal,
        observation=observation,
        plan=[],
        current_step_idx=0,
        action_history=[],
        review_history=[],
        latest_action={},
        step_count=0,
        max_steps=max_steps,
        done=False,
        success=False,
        final_answer="",
        decision="continue",
        notes=[],
        dynamic_replanning=dynamic_replanning,
        use_cot=use_cot,
        agentic_mode=agentic_mode,
    )
