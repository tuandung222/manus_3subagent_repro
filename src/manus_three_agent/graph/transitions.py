from __future__ import annotations

from manus_three_agent.core.state import ManusState


def route_after_critic(state: ManusState) -> str:
    if state["done"]:
        return "end"

    decision = state.get("decision", "continue")
    if decision == "end":
        return "end"
    if decision == "replan" and state.get("dynamic_replanning", True):
        return "replan"
    return "continue"
