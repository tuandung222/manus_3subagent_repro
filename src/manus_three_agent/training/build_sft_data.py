from __future__ import annotations

from pathlib import Path
from typing import Any

import orjson


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    with open(path, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(orjson.loads(line))
    return rows


def iter_run_dirs(trace_dir: Path) -> list[Path]:
    if not trace_dir.exists():
        return []
    return sorted([p for p in trace_dir.iterdir() if p.is_dir()])


def build_sft_records(trace_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for run_dir in iter_run_dirs(trace_dir):
        events = load_jsonl(run_dir / "events.jsonl")
        role_inputs: dict[tuple[str, int], dict[str, Any]] = {}

        for event in events:
            event_type = str(event.get("event_type", ""))
            payload = event.get("payload", {})
            run_id = str(event.get("run_id", ""))
            step = int(event.get("step", 0))

            if event_type == "llm_call":
                system_prompt = str(payload.get("system_prompt", "")).strip()
                user_prompt = str(payload.get("user_prompt", "")).strip()
                parsed_output = payload.get("parsed_output")
                role = str(payload.get("agent", "unknown"))
                if not system_prompt or not user_prompt or parsed_output is None:
                    continue

                records.append(
                    {
                        "run_id": run_id,
                        "step": step,
                        "role": role,
                        "source_event": "llm_call",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                            {
                                "role": "assistant",
                                "content": orjson.dumps(parsed_output).decode("utf-8"),
                            },
                        ],
                    }
                )
                continue

            if event_type.endswith("_input"):
                role = event_type.replace("_input", "")
                role_inputs[(role, step)] = payload
                continue

            if event_type.endswith("_output"):
                role = event_type.replace("_output", "")
                input_payload = role_inputs.get((role, step), {})
                records.append(
                    {
                        "run_id": run_id,
                        "step": step,
                        "role": role,
                        "source_event": event_type,
                        "messages": [
                            {"role": "system", "content": f"{role} role boundary trace"},
                            {
                                "role": "user",
                                "content": orjson.dumps(input_payload).decode("utf-8"),
                            },
                            {
                                "role": "assistant",
                                "content": orjson.dumps(payload).decode("utf-8"),
                            },
                        ],
                    }
                )

    return records


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        for row in rows:
            f.write(orjson.dumps(row))
            f.write(b"\n")


def build_trajectory_dataset(trace_dir: str, output_path: str) -> dict[str, Any]:
    trace_path = Path(trace_dir)
    out_path = Path(output_path)

    records = build_sft_records(trace_path)
    write_jsonl(out_path, records)

    return {
        "trace_dir": str(trace_path),
        "output_path": str(out_path),
        "num_records": len(records),
    }
