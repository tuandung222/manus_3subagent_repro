from __future__ import annotations

from typing import Any


def get_mode_prompt_profile(mode: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    normalized = mode.strip().lower()
    if normalized == "react":
        return _react_profile()
    return _codeact_profile()


def _codeact_profile() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    shared_context = {
        "agentic_mode": "codeact",
        "mode_guideline": "Prefer executable, tool-grounded, testable actions.",
    }
    role_overrides: dict[str, dict[str, Any]] = {
        "architect": {
            "system": (
                "You are ArchitectAgent operating in CodeAct mode. "
                "Produce implementation-oriented plan steps with clear execution intent. "
                "Output strict JSON only."
            ),
        },
        "worker": {
            "system": (
                "You are WorkerAgent operating in CodeAct mode. "
                "Convert plan steps into concrete actions and tool calls when beneficial. "
                "Output strict JSON only."
            ),
        },
        "critic": {
            "system": (
                "You are CriticAgent operating in CodeAct mode. "
                "Validate executability, correctness, and stop/replan decisions. "
                "Output strict JSON only."
            ),
        },
    }
    return role_overrides, shared_context


def _react_profile() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    shared_context = {
        "agentic_mode": "react",
        "mode_guideline": "Prefer thought-action-observation loops with concise rationale.",
    }
    role_overrides: dict[str, dict[str, Any]] = {
        "architect": {
            "system": (
                "You are ArchitectAgent operating in ReAct mode. "
                "Design steps that support iterative reason-observe-act refinement. "
                "Output strict JSON only."
            ),
        },
        "worker": {
            "system": (
                "You are WorkerAgent operating in ReAct mode. "
                "Act step-by-step using observation feedback and concise reasoning summaries. "
                "Output strict JSON only."
            ),
        },
        "critic": {
            "system": (
                "You are CriticAgent operating in ReAct mode. "
                "Review whether reasoning-observation loop should continue, replan, or end. "
                "Output strict JSON only."
            ),
        },
    }
    return role_overrides, shared_context
