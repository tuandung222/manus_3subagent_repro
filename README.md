# Manus 3-Subagent Reproduction Scaffold

Navigation:
- Docs home: [`docs/README.md`](docs/README.md)
- Reading guide: [`docs/READING_GUIDE.md`](docs/READING_GUIDE.md)
- Reproduction plan: [`docs/plans/REPRODUCTION_PLAN.md`](docs/plans/REPRODUCTION_PLAN.md)
- Code structure plan: [`docs/plans/CODE_STRUCTURE_PLAN.md`](docs/plans/CODE_STRUCTURE_PLAN.md)
- Tracing/data plan: [`docs/plans/TRAINING_DATA_TRACING_PLAN.md`](docs/plans/TRAINING_DATA_TRACING_PLAN.md)
- Tracing implementation for tuning: [`docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md`](docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md)
- Manus source collection + gap plan: [`docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md`](docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md)
- Notebook education plan: [`docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md`](docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md)
- Architecture: [`docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md`](docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md)
- CodeAct + ReAct hybrid design: [`docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md`](docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md)
- Orchestration deep dive: [`docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md`](docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md)
- Planner pseudocode: [`docs/architecture/MANUS_PLANNER_PSEUDOCODE.md`](docs/architecture/MANUS_PLANNER_PSEUDOCODE.md)
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

4. Run in `CodeAct` mode:
```bash
manus3-run run-episode --goal "Find a robust plan for evaluating model drift" --trace --agentic-mode codeact
```

5. Run in `ReAct` mode:
```bash
manus3-run run-episode --goal "Find a robust plan for evaluating model drift" --trace --agentic-mode react
```

6. Run with prompt + hyperparameter overrides:
```bash
manus3-run run-episode \
  --goal "Thiết kế benchmark cho agent planner" \
  --agentic-mode codeact \
  --model-override configs/model_overrides.example.yaml \
  --prompt-override configs/prompt_overrides.example.yaml \
  --prompt-context configs/prompt_context.example.yaml \
  --architect-temperature 0.1 \
  --worker-max-completion-tokens 1200 \
  --print-effective-config
```

7. Build SFT-ready trajectory dataset from traces:
```bash
manus3-run build-trajectories --trace-dir artifacts/traces --output data/processed/trajectory_sft.jsonl
```

## Config Surfaces

### Prompt configuration
- Base prompt templates: `configs/prompts/*.yaml`
- Role override file: `configs/prompt_overrides.example.yaml`
- Shared variables file: `configs/prompt_context.example.yaml`
- Runtime flags:
  - `--prompts-dir`
  - `--prompt-override`
  - `--prompt-context`

### Hyperparameters configuration
- Base model settings: `configs/models.yaml`
- File override: `configs/model_overrides.example.yaml`
- Quick CLI overrides:
  - `--architect-model`, `--worker-model`, `--critic-model`
  - `--architect-temperature`, `--worker-temperature`, `--critic-temperature`
  - `--architect-top-p`, `--worker-top-p`, `--critic-top-p`
  - `--architect-max-completion-tokens`, `--worker-max-completion-tokens`, `--critic-max-completion-tokens`

### Agentic mode configuration
- Runtime config: `configs/base.yaml -> agentic_mode: codeact|react`
- CLI override: `--agentic-mode codeact|react`
- Mode determines default prompt profile for planner/worker/verifier.

## Reference Download

Refresh reference snapshots:
```bash
./scripts/download_references.sh
```

## Notes

- Runtime tracing writes per-run `session.json` and `events.jsonl`.
- OpenAI integration uses `openai` Python client.
- Architecture keeps schema-first interfaces for subagent boundaries.
