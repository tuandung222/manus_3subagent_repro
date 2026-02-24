from __future__ import annotations

from typing import Any

from manus_three_agent.core.schemas import CriticOutput
from manus_three_agent.core.types import ModelConfig
from manus_three_agent.prompts import PromptTemplates
from manus_three_agent.tracing import TraceCollector
from manus_three_agent.utils.llm import LLMClient


class CriticAgent:
    def __init__(
        self,
        model_config: ModelConfig,
        prompts: PromptTemplates,
        tracer: TraceCollector | None = None,
        force_mock: bool = False,
        agentic_mode: str = "codeact",
    ) -> None:
        self.model_config = model_config
        self.prompts = prompts
        self.tracer = tracer
        self.force_mock = force_mock
        self.agentic_mode = agentic_mode
        self.llm = LLMClient(trace_hook=self._on_llm_trace)

    def review(
        self,
        *,
        goal: str,
        observation: str,
        action_history: list[dict[str, Any]],
        current_step_idx: int,
        plan_length: int,
        step: int,
    ) -> CriticOutput:
        if self.force_mock or not self.llm.enabled:
            return self._mock_review(observation, action_history, current_step_idx, plan_length)

        system_prompt, user_prompt = self.prompts.render(
            "critic",
            goal=goal,
            observation=observation,
            action_history=action_history,
            current_step_idx=current_step_idx,
            plan_length=plan_length,
            agentic_mode=self.agentic_mode,
            mode_guideline=self._mode_guideline(),
        )
        raw = self.llm.chat_json(
            model=self.model_config.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            generation_config=self.model_config.to_openai_chat_params(),
            trace_context={"agent": "critic", "step": step, "agentic_mode": self.agentic_mode},
        )
        return CriticOutput.model_validate(raw)

    def _mock_review(
        self,
        observation: str,
        action_history: list[dict[str, Any]],
        current_step_idx: int,
        plan_length: int,
    ) -> CriticOutput:
        obs = observation.lower()
        if "error" in obs or "failed" in obs:
            return CriticOutput(
                decision="replan",
                feedback="Detected possible failure signal in observation.",
                should_succeed=False,
            )
        if current_step_idx >= plan_length:
            return CriticOutput(
                decision="end",
                feedback="All planned steps completed.",
                should_succeed=len(action_history) > 0,
            )
        return CriticOutput(
            decision="continue",
            feedback="Proceed to next step.",
            should_succeed=False,
        )

    def _on_llm_trace(self, payload: dict[str, Any]) -> None:
        if not self.tracer:
            return
        self.tracer.log_event(
            event_type="llm_call",
            step=int(payload.get("step", 0)),
            payload={"agent": "critic", **payload},
        )

    def _mode_guideline(self) -> str:
        if self.agentic_mode == "react":
            return "Prefer thought-action-observation loops with concise rationale."
        return "Prefer executable, tool-grounded, testable actions."
