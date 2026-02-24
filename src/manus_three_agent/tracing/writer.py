from __future__ import annotations

from pathlib import Path
from typing import Any

from manus_three_agent.utils.io import append_jsonl, write_json


class TraceWriter:
    def __init__(self, *, base_dir: str, run_id: str) -> None:
        self.run_dir = Path(base_dir) / run_id
        self.session_path = self.run_dir / "session.json"
        self.events_path = self.run_dir / "events.jsonl"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def write_session(self, payload: dict[str, Any]) -> None:
        write_json(self.session_path, payload)

    def append_event(self, payload: dict[str, Any]) -> None:
        append_jsonl(self.events_path, payload)
