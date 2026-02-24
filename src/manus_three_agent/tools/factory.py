from __future__ import annotations

from manus_three_agent.tools.base import ToolRegistry
from manus_three_agent.tools.builtin import calculator_tool, fetch_url_tool


def build_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register("calculator", calculator_tool)
    registry.register("fetch_url", fetch_url_tool)
    return registry
