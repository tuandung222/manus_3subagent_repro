from __future__ import annotations

from manus_three_agent.environments.base import EnvironmentAdapter
from manus_three_agent.environments.simulator import GenericSimulatorEnvironment


def build_environment(kind: str) -> EnvironmentAdapter:
    normalized = kind.strip().lower()
    if normalized in {"sim", "simulator", "generic"}:
        return GenericSimulatorEnvironment()
    raise ValueError(f"Unsupported environment: {kind}")
