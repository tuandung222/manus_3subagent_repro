from pathlib import Path

import orjson

from manus_three_agent.training.build_sft_data import build_trajectory_dataset


def test_build_trajectory_dataset_from_llm_events(tmp_path: Path) -> None:
    run_dir = tmp_path / "traces" / "runA"
    run_dir.mkdir(parents=True)

    llm_event = {
        "run_id": "runA",
        "step": 1,
        "event_type": "llm_call",
        "payload": {
            "agent": "architect",
            "system_prompt": "sys",
            "user_prompt": "usr",
            "parsed_output": {"steps": [{"title": "A", "rationale": "B"}]},
        },
    }
    worker_input_event = {
        "run_id": "runA",
        "step": 1,
        "event_type": "worker_input",
        "payload": {"current_step_idx": 0},
    }
    worker_output_event = {
        "run_id": "runA",
        "step": 1,
        "event_type": "worker_output",
        "payload": {"action": {"summary": "done"}},
    }

    with open(run_dir / "events.jsonl", "wb") as f:
        f.write(orjson.dumps(llm_event))
        f.write(b"\n")
        f.write(orjson.dumps(worker_input_event))
        f.write(b"\n")
        f.write(orjson.dumps(worker_output_event))
        f.write(b"\n")

    out_path = tmp_path / "dataset" / "train.jsonl"
    summary = build_trajectory_dataset(str(tmp_path / "traces"), str(out_path))

    assert summary["num_records"] == 2
    assert out_path.exists()
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    row = orjson.loads(lines[0].encode("utf-8"))
    assert row["role"] == "architect"
    assert len(row["messages"]) == 3
