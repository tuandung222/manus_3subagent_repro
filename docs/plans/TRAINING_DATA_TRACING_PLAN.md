# Training Data and Tracing Plan

## Trace Contracts

Each run emits:
- `artifacts/traces/<run_id>/session.json`
- `artifacts/traces/<run_id>/events.jsonl`

Mandatory role-boundary events:
- `architect_input` / `architect_output`
- `worker_input` / `worker_output`
- `critic_input` / `critic_output`
- `tool_call` (when present)
- `llm_call` (OpenAI request/response telemetry)
- `episode_end` / `episode_error`

## Trajectory Export

Exporter reads all trace runs and converts `llm_call` events to SFT-style records:
- `run_id`
- `step`
- `role` (`architect`, `worker`, `critic`)
- `messages` (`system`, `user`, `assistant-json`)

Output:
- `data/processed/trajectory_sft.jsonl`

## Quality Checks

1. Non-empty prompts and parsed outputs only.
2. Every record carries `run_id` and `step` lineage.
3. Redacted secrets in traced prompt/response content.

## Extension Path

- Add preference/critique pairs by mapping `critic_output` to reward labels.
- Add OTLP exporter for centralized tracing backend.
