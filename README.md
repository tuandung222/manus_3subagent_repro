# Manus 3-Subagent Reproduction Scaffold

Navigation:
- Docs home: [`docs/README.md`](docs/README.md)
- Reading guide: [`docs/READING_GUIDE.md`](docs/READING_GUIDE.md)
- Reproduction plan: [`docs/plans/REPRODUCTION_PLAN.md`](docs/plans/REPRODUCTION_PLAN.md)
- Code structure plan: [`docs/plans/CODE_STRUCTURE_PLAN.md`](docs/plans/CODE_STRUCTURE_PLAN.md)
- Tracing/data plan: [`docs/plans/TRAINING_DATA_TRACING_PLAN.md`](docs/plans/TRAINING_DATA_TRACING_PLAN.md)
- Architecture: [`docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md`](docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md)
- References: [`references/README.md`](references/README.md)

This project implements a Manus-inspired 3-subagent runtime:
1. `Architect` (planning/decomposition)
2. `Worker` (tool-enabled execution)
3. `Critic` (review and routing: continue/replan/end)

The scaffold is designed for:
- Agent Architects who need deterministic orchestration boundaries.
- Data Scientists who need trajectory traces for training datasets.

## Quick Start

1. Install:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2. Configure environment:
```bash
cp .env.example .env
# set OPENAI_API_KEY to run with real model calls
```

3. Run with deterministic mock mode (no API key required):
```bash
manus3-run run-episode --goal "Build a data collection plan for churn modeling" --mock
```

4. Run with OpenAI client enabled:
```bash
manus3-run run-episode --goal "Find a robust plan for evaluating model drift" --trace
```

5. Build SFT-ready trajectory dataset from traces:
```bash
manus3-run build-trajectories --trace-dir artifacts/traces --output data/processed/trajectory_sft.jsonl
```

## Reference Download

Refresh reference snapshots:
```bash
./scripts/download_references.sh
```

## Notes

- Runtime tracing writes per-run `session.json` and `events.jsonl`.
- OpenAI integration uses `openai` Python client.
- Architecture keeps schema-first interfaces for subagent boundaries.
