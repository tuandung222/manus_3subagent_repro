from manus_three_agent.agents import ArchitectAgent, CriticAgent, WorkerAgent
from manus_three_agent.core import ModelConfig, build_initial_state
from manus_three_agent.environments.simulator import GenericSimulatorEnvironment
from manus_three_agent.graph import build_workflow
from manus_three_agent.prompts import PromptTemplates
from manus_three_agent.tools import build_default_tool_registry
from manus_three_agent.tracing import TraceCollector


def test_mock_workflow_reaches_terminal_state() -> None:
    prompts = PromptTemplates(config_dir="configs/prompts")
    model_cfg = ModelConfig(model="mock")

    tracer = TraceCollector.disabled()
    architect = ArchitectAgent(model_cfg, prompts, tracer=tracer, force_mock=True)
    worker = WorkerAgent(model_cfg, prompts, build_default_tool_registry(), tracer=tracer, force_mock=True)
    critic = CriticAgent(model_cfg, prompts, tracer=tracer, force_mock=True)

    workflow = build_workflow(architect, worker, critic, GenericSimulatorEnvironment(), tracer)

    initial_state = build_initial_state(
        goal="Draft a reproducibility checklist",
        observation="Environment ready.",
        max_steps=6,
        dynamic_replanning=True,
        use_cot=False,
    )

    final_state = workflow.invoke(initial_state)

    assert final_state["done"] is True
    assert final_state["success"] is True
    assert final_state["step_count"] >= 1
    assert final_state["final_answer"] != ""
