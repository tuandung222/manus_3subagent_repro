# Reference Snapshot

Reference assets were downloaded on demand and frozen as HTML snapshots under [`raw/`](raw).

Refresh command:
```bash
./scripts/download_references.sh
```

Source registry:
- [`REFERENCE_SOURCES.csv`](REFERENCE_SOURCES.csv)

## Why these sources

- Manus official pages: product surface, capability framing, sandbox/browser operator context.
- OpenAI official SDK/docs: client integration and agent/tracing patterns.
- LangGraph docs/repo: deterministic orchestration graph for multi-subagent runtime.
- OpenTelemetry + Phoenix: vendor-neutral trace/observability path for dataset lineage.
