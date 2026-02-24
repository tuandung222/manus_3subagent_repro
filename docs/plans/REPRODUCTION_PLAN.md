# Reproduction Plan: Manus-Style 3 Subagents

## Scope

Reproduce a Manus-inspired agent runtime with 3 explicit subagents:
1. `Architect`: planning/decomposition.
2. `Worker`: tool-enabled execution.
3. `Critic`: quality control + route decision (`continue/replan/end`).

Target is framework-level reproduction, not claim of exact internal Manus implementation.

## Chosen Framework Stack

- Orchestration: `LangGraph` (state graph + deterministic transitions).
- Model client: `openai` Python SDK.
- Contracts: `Pydantic` schemas.
- Runtime CLI: `Typer`.
- Trace storage: `session.json` + `events.jsonl`.
- Training export: JSONL SFT converter from trace events.

## Why this stack for Agent Architect + Data Scientist

- Clear graph boundaries simplify architecture reviews.
- Typed schemas reduce runtime drift and improve testability.
- Trace events preserve lineage for downstream dataset curation.
- Works in both `mock` mode (no key) and real OpenAI mode.

## Milestones

1. References acquisition and local snapshots.
2. 3-subagent orchestration scaffold.
3. OpenAI client integration and fallback mock path.
4. Tracing instrumentation at every role boundary.
5. Trace-to-trajectory export pipeline.
6. Unit tests + runnable CLI demonstration.

## Success Criteria

1. `manus3-run run-episode --mock` completes successfully.
2. `manus3-run run-episode --trace` writes `session.json` + `events.jsonl`.
3. `manus3-run build-trajectories` creates `trajectory_sft.jsonl`.
4. Unit tests pass.
