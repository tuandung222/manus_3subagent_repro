from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TraceConfig(BaseModel):
    enabled: bool = False
    base_dir: str = "artifacts/traces"
    schema_version: str = "1.0.0"


class TraceSession(BaseModel):
    schema_version: str
    run_id: str
    goal: str
    environment: dict[str, Any]
    model_stack: dict[str, Any]
    runtime_config: dict[str, Any]
    metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: str = Field(default_factory=lambda: utc_now_iso())
    finished_at: str = ""
    status: str = "running"
    summary: dict[str, Any] = Field(default_factory=dict)


class TraceEvent(BaseModel):
    schema_version: str
    run_id: str
    step: int
    event_type: str
    payload: dict[str, Any]
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: utc_now_iso())


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
