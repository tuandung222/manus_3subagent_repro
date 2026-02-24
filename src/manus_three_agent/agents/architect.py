from __future__ import annotations

from typing import Any

from manus_three_agent.core.schemas import PlanOutput, PlanStep
from manus_three_agent.core.types import ModelConfig
from manus_three_agent.prompts import PromptTemplates
from manus_three_agent.tracing import TraceCollector
from manus_three_agent.utils.llm import LLMClient


class ArchitectAgent:
    def __init__(
        self,
        model_config: ModelConfig,
        prompts: PromptTemplates,
        tracer: TraceCollector | None = None,
        force_mock: bool = False,
    ) -> None:
        self.model_config = model_config
        self.prompts = prompts
        self.tracer = tracer
        self.force_mock = force_mock
        self.llm = LLMClient(trace_hook=self._on_llm_trace)

    def plan(
        self,
        *,
        goal: str,
        observation: str,
        action_history: list[dict[str, Any]],
        use_cot: bool,
        step: int,
    ) -> PlanOutput:
        if self.force_mock or not self.llm.enabled:
            return self._mock_plan(goal)

        system_prompt, user_prompt = self.prompts.render(
            "architect",
            goal=goal,
            observation=observation,
            action_history=action_history,
            use_cot=use_cot,
        )
        raw = self.llm.chat_json(
            model=self.model_config.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=self.model_config.temperature,
            trace_context={"agent": "architect", "step": step},
        )
        steps = [PlanStep.model_validate(item) for item in raw.get("steps", [])]
        if not steps:
            return self._mock_plan(goal)
        return PlanOutput(steps=steps)

    def _mock_plan(self, goal: str) -> PlanOutput:
        return PlanOutput(
            steps=[
                PlanStep(title="Clarify objective and constraints", rationale=f"Interpret goal: {goal}"),
                PlanStep(title="Execute targeted information gathering", rationale="Collect facts and intermediate outputs"),
                PlanStep(title="Synthesize final recommendation", rationale="Return concise deliverable"),
            ]
        )

    def _on_llm_trace(self, payload: dict[str, Any]) -> None:
        if not self.tracer:
            return
        self.tracer.log_event(
            event_type="llm_call",
            step=int(payload.get("step", 0)),
            payload={"agent": "architect", **payload},
        )
