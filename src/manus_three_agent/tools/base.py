from __future__ import annotations

from collections.abc import Callable
from typing import Any

ToolFn = Callable[[dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        self._tools[name] = fn

    def has(self, name: str) -> bool:
        return name in self._tools

    def call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if name not in self._tools:
            return {
                "ok": False,
                "error": f"tool_not_found:{name}",
                "name": name,
                "arguments": arguments,
            }
        try:
            out = self._tools[name](arguments)
            return {
                "ok": True,
                "name": name,
                "arguments": arguments,
                "output": out,
            }
        except Exception as exc:
            return {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
                "name": name,
                "arguments": arguments,
            }
