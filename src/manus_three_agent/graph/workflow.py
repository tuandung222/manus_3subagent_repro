from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from manus_three_agent.agents.architect import ArchitectAgent
from manus_three_agent.agents.critic import CriticAgent
from manus_three_agent.agents.worker import WorkerAgent
from manus_three_agent.core.schemas import PlanStep
from manus_three_agent.core.state import ManusState
from manus_three_agent.environments.base import EnvironmentAdapter
from manus_three_agent.environments.simulator import GenericSimulatorEnvironment
from manus_three_agent.graph.transitions import route_after_critic
from manus_three_agent.tracing import TraceCollector


def architect_node(
    state: ManusState,
    architect: ArchitectAgent,
    tracer: TraceCollector | None = None,
) -> dict[str, Any]:
    if tracer:
        tracer.log_event(
            event_type="architect_input",
            step=state["step_count"],
            payload={
                "goal": state["goal"],
                "observation": state["observation"],
                "action_history": state["action_history"],
            },
        )

    plan = architect.plan(
        goal=state["goal"],
        observation=state["observation"],
        action_history=state["action_history"],
        use_cot=state["use_cot"],
        step=state["step_count"],
    )
    steps = [step.model_dump() for step in plan.steps]

    if tracer:
        tracer.log_event(
            event_type="architect_output",
            step=state["step_count"],
            payload={"steps": steps},
        )

    return {
        "plan": steps,
        "current_step_idx": 0,
        "decision": "continue",
        "notes": state["notes"] + ["Architect created/replaced execution plan."],
    }


def worker_node(
    state: ManusState,
    worker: WorkerAgent,
    environment: EnvironmentAdapter,
    tracer: TraceCollector | None = None,
) -> dict[str, Any]:
    if state["done"]:
        return {}

    step_count = state["step_count"]
    max_steps = state["max_steps"]
    current_idx = state["current_step_idx"]
    plan = state["plan"]

    if step_count >= max_steps:
        if tracer:
            tracer.log_event(
                event_type="episode_stop",
                step=step_count,
                payload={"reason": "max_steps_reached", "max_steps": max_steps},
            )
        return {
            "done": True,
            "success": False,
            "decision": "end",
            "final_answer": "Stopped: max steps reached.",
            "notes": state["notes"] + ["Reached max steps budget."],
        }

    if not plan:
        decision = "replan" if state["dynamic_replanning"] else "end"
        return {
            "decision": decision,
            "done": decision == "end",
            "success": False,
            "final_answer": "No plan available." if decision == "end" else state["final_answer"],
            "notes": state["notes"] + ["Worker found empty plan."],
        }

    if current_idx >= len(plan):
        return {
            "done": True,
            "success": len(state["action_history"]) > 0,
            "decision": "end",
            "final_answer": state["final_answer"] or "Plan completed.",
            "notes": state["notes"] + ["Worker exhausted plan steps."],
        }

    current_step = PlanStep.model_validate(plan[current_idx])
    if tracer:
        tracer.log_event(
            event_type="worker_input",
            step=step_count,
            payload={
                "current_step_idx": current_idx,
                "current_step": current_step.model_dump(),
                "observation": state["observation"],
            },
        )

    action = worker.execute(
        goal=state["goal"],
        plan_step=current_step,
        observation=state["observation"],
        step_index=current_idx,
        total_steps=len(plan),
        use_cot=state["use_cot"],
        step=step_count,
    )

    new_step_count = step_count + 1
    new_action_history = state["action_history"] + [action.model_dump()]

    if tracer:
        tracer.log_event(
            event_type="worker_output",
            step=new_step_count,
            payload={"action": action.model_dump()},
        )

    env_result = environment.step(action=action, step_count=new_step_count)

    if tracer:
        tracer.log_event(
            event_type="environment_step",
            step=new_step_count,
            payload={
                "observation": env_result.observation,
                "done": env_result.done,
                "success": env_result.success,
                "final_answer": env_result.final_answer,
                "notes": env_result.notes,
            },
        )

    done = bool(action.is_final or env_result.done)
    success = bool(action.is_final or env_result.success)
    final_answer = action.final_answer or env_result.final_answer or state["final_answer"]

    return {
        "latest_action": action.model_dump(),
        "action_history": new_action_history,
        "observation": env_result.observation,
        "step_count": new_step_count,
        "current_step_idx": current_idx + 1,
        "done": done,
        "success": success,
        "final_answer": final_answer,
        "decision": "end" if done else "continue",
        "notes": state["notes"] + env_result.notes,
    }


def critic_node(
    state: ManusState,
    critic: CriticAgent,
    tracer: TraceCollector | None = None,
) -> dict[str, Any]:
    if tracer:
        tracer.log_event(
            event_type="critic_input",
            step=state["step_count"],
            payload={
                "observation": state["observation"],
                "current_step_idx": state["current_step_idx"],
                "plan_length": len(state["plan"]),
                "done": state["done"],
            },
        )

    if state["done"]:
        out_decision = "end"
        out_feedback = "Episode already marked done by worker/environment."
        should_succeed = state["success"]
    elif state.get("decision") == "replan":
        out_decision = "replan"
        out_feedback = "Worker requested replanning."
        should_succeed = False
    else:
        review = critic.review(
            goal=state["goal"],
            observation=state["observation"],
            action_history=state["action_history"],
            current_step_idx=state["current_step_idx"],
            plan_length=len(state["plan"]),
            step=state["step_count"],
        )
        out_decision = review.decision
        out_feedback = review.feedback
        should_succeed = review.should_succeed

    review_event = {
        "decision": out_decision,
        "feedback": out_feedback,
        "should_succeed": should_succeed,
    }

    if tracer:
        tracer.log_event(
            event_type="critic_output",
            step=state["step_count"],
            payload=review_event,
        )

    if out_decision == "end" and not state["done"]:
        final_answer = state["final_answer"] or "Critic decided to end run."
        return {
            "decision": "end",
            "done": True,
            "success": should_succeed,
            "final_answer": final_answer,
            "review_history": state["review_history"] + [review_event],
            "notes": state["notes"] + [out_feedback],
        }

    return {
        "decision": out_decision,
        "review_history": state["review_history"] + [review_event],
        "notes": state["notes"] + [out_feedback],
    }


def build_workflow(
    architect: ArchitectAgent,
    worker: WorkerAgent,
    critic: CriticAgent,
    environment: EnvironmentAdapter | None = None,
    tracer: TraceCollector | None = None,
):
    environment_adapter = environment or GenericSimulatorEnvironment()
    trace_collector = tracer

    graph = StateGraph(ManusState)
    graph.add_node("architect", lambda s: architect_node(s, architect, trace_collector))
    graph.add_node("worker", lambda s: worker_node(s, worker, environment_adapter, trace_collector))
    graph.add_node("critic", lambda s: critic_node(s, critic, trace_collector))

    graph.add_edge(START, "architect")
    graph.add_edge("architect", "worker")
    graph.add_edge("worker", "critic")
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "end": END,
            "replan": "architect",
            "continue": "worker",
        },
    )

    return graph.compile()
