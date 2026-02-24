from __future__ import annotations

from typing import Any


def compute_episode_metrics(final_state: dict[str, Any]) -> dict[str, Any]:
    action_history = list(final_state.get("action_history", []))
    review_history = list(final_state.get("review_history", []))
    success = bool(final_state.get("success", False))
    step_count = int(final_state.get("step_count", 0))

    return {
        "success": success,
        "step_count": step_count,
        "actions": len(action_history),
        "reviews": len(review_history),
        "termination_reason": "success" if success else "stopped_or_failed",
    }
