from pathlib import Path

import orjson

from manus_three_agent.tracing import TraceCollector, TraceConfig


def test_trace_collector_writes_session_and_events(tmp_path: Path) -> None:
    tracer = TraceCollector(
        config=TraceConfig(enabled=True, base_dir=str(tmp_path), schema_version="1.0.0"),
        run_id="run123",
    )
    tracer.start_session(
        goal="test",
        environment={"kind": "simulator"},
        model_stack={"architect": {"model": "mock"}},
        runtime_config={"max_steps": 3},
        metadata={"unit_test": True},
    )
    tracer.log_event(event_type="unit", step=0, payload={"ok": True})
    tracer.close(status="completed", summary={"ok": True})

    session_path = tmp_path / "run123" / "session.json"
    events_path = tmp_path / "run123" / "events.jsonl"

    assert session_path.exists()
    assert events_path.exists()

    session = orjson.loads(session_path.read_bytes())
    assert session["status"] == "completed"
    assert session["summary"]["event_count"] == 1

    lines = events_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
