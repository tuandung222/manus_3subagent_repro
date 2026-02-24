from __future__ import annotations

from manus_three_agent.core.schemas import WorkerOutput
from manus_three_agent.environments.base import EnvironmentStepResult


class GenericSimulatorEnvironment:
    name = "generic_simulator"

    def reset(self, *, goal: str) -> str:
        return f"Environment ready. Goal: {goal}"

    def step(self, *, action: WorkerOutput, step_count: int) -> EnvironmentStepResult:
        if action.is_final:
            return EnvironmentStepResult(
                observation=f"Finalized at step {step_count}: {action.final_answer}",
                done=True,
                success=True,
                final_answer=action.final_answer,
                notes=["Worker marked final answer."],
            )

        return EnvironmentStepResult(
            observation=f"Step {step_count} completed. Worker output: {action.output}",
            done=False,
            success=False,
            final_answer="",
            notes=["Progress recorded in simulator."],
        )
