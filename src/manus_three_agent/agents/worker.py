from __future__ import annotations

from typing import Any

from manus_three_agent.core.schemas import PlanStep, ToolRequest, WorkerOutput
from manus_three_agent.core.types import ModelConfig
from manus_three_agent.prompts import PromptTemplates
from manus_three_agent.tools.base import ToolRegistry
from manus_three_agent.tracing import TraceCollector
from manus_three_agent.utils.llm import LLMClient


class WorkerAgent:
    def __init__(
        self,
        model_config: ModelConfig,
        prompts: PromptTemplates,
        tools: ToolRegistry,
        tracer: TraceCollector | None = None,
        force_mock: bool = False,
        agentic_mode: str = "codeact",
    ) -> None:
        self.model_config = model_config
        self.prompts = prompts
        self.tools = tools
        self.tracer = tracer
        self.force_mock = force_mock
        self.agentic_mode = agentic_mode
        self.llm = LLMClient(trace_hook=self._on_llm_trace)

    def execute(
        self,
        *,
        goal: str,
        plan_step: PlanStep,
        observation: str,
        step_index: int,
        total_steps: int,
        use_cot: bool,
        step: int,
    ) -> WorkerOutput:
        if self.force_mock or not self.llm.enabled:
            return self._mock_execute(plan_step, step_index, total_steps)

        system_prompt, user_prompt = self.prompts.render(
            "worker",
            goal=goal,
            plan_step=plan_step.model_dump(),
            observation=observation,
            step_index=step_index,
            total_steps=total_steps,
            use_cot=use_cot,
            agentic_mode=self.agentic_mode,
            mode_guideline=self._mode_guideline(),
        )
        raw = self.llm.chat_json(
            model=self.model_config.model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            generation_config=self.model_config.to_openai_chat_params(),
            trace_context={"agent": "worker", "step": step, "agentic_mode": self.agentic_mode},
        )
        candidate = WorkerOutput.model_validate(raw)
        return self._run_tools(candidate, step=step)

    def _mock_execute(self, plan_step: PlanStep, step_index: int, total_steps: int) -> WorkerOutput:
        is_last = step_index >= total_steps - 1
        tool_requests: list[ToolRequest] = []
        if self.agentic_mode == "codeact" and not is_last and step_index == 0:
            tool_requests = [ToolRequest(name="calculator", arguments={"expression": "42 + 8"})]

        summary_prefix = "ReAct iteration" if self.agentic_mode == "react" else "Executed"
        output = WorkerOutput(
            summary=f"{summary_prefix}: {plan_step.title}",
            output=f"Completed work item {step_index + 1}/{total_steps}.",
            is_final=is_last,
            final_answer="Delivered a compact final report." if is_last else "",
            tool_requests=tool_requests,
        )
        return self._run_tools(output, step=step_index + 1)

    def _run_tools(self, output: WorkerOutput, *, step: int) -> WorkerOutput:
        if not output.tool_requests:
            return output

        tool_results: list[dict[str, Any]] = []
        for req in output.tool_requests:
            req_obj = ToolRequest.model_validate(req)
            result = self.tools.call(req_obj.name, req_obj.arguments)
            tool_results.append(result)
            if self.tracer:
                self.tracer.log_event(
                    event_type="tool_call",
                    step=step,
                    payload={
                        "name": req_obj.name,
                        "arguments": req_obj.arguments,
                        "result": result,
                    },
                )

        suffix = f" Tool results: {tool_results}" if tool_results else ""
        return output.model_copy(update={"output": f"{output.output}{suffix}"})

    def _on_llm_trace(self, payload: dict[str, Any]) -> None:
        if not self.tracer:
            return
        self.tracer.log_event(
            event_type="llm_call",
            step=int(payload.get("step", 0)),
            payload={"agent": "worker", **payload},
        )

    def _mode_guideline(self) -> str:
        if self.agentic_mode == "react":
            return "Prefer thought-action-observation loops with concise rationale."
        return "Prefer executable, tool-grounded, testable actions."
