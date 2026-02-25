# Manus-Style Agent Reproduction (3 Subagents, CodeAct + ReAct)

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![Orchestration](https://img.shields.io/badge/Orchestration-LangGraph-1F6FEB)
![Provider](https://img.shields.io/badge/Provider-HF%20Inference%20(default)-f97316)
![API](https://img.shields.io/badge/API-OpenAI%20compatible-412991)
![Tests](https://img.shields.io/badge/pytest-13%20passed-brightgreen)
![Notebook Smoke](https://img.shields.io/badge/notebooks-3%2F3%20smoke%20pass-success)

This repository implements a production-oriented reproduction of a Manus-inspired agent runtime with three explicit subagents:

1. `Planner` (`ArchitectAgent`)
2. `Worker` (`WorkerAgent`)
3. `Verifier` (`CriticAgent`)

The project is built for two audiences:
- **Agent Architects** who need deterministic orchestration, explicit routing, and strong runtime contracts.
- **Data Scientists** who need trace lineage and role-specific trajectory datasets for supervised fine-tuning and evaluation.

## Objectives

- Deliver an end-to-end runnable multi-agent runtime with OpenAI client integration.
- Support both `CodeAct` and `ReAct` behavior profiles in one codebase.
- Enable configurable prompts and model hyperparameters without code edits.
- Produce high-quality trace data that can be exported into training trajectories.

## Source Code Reading Quickstart

If you are new to this repository and want the fastest route:

1. Entrypoint: `pyproject.toml` (`manus3-run`) -> `src/manus_three_agent/eval/runner.py` (`run_episode`)
2. Orchestration loop: `src/manus_three_agent/graph/workflow.py`
3. Routing policy: `src/manus_three_agent/graph/transitions.py`
4. Role loops: `src/manus_three_agent/agents/architect.py`, `worker.py`, `critic.py`
5. State/contracts: `src/manus_three_agent/core/state.py`, `schemas.py`, `types.py`
6. Tracing and training export: `src/manus_three_agent/tracing/`, `src/manus_three_agent/training/build_sft_data.py`

Detailed guide:
- [`docs/architecture/CODEBASE_READING_ROADMAP.md`](docs/architecture/CODEBASE_READING_ROADMAP.md)

## Implementation Workflow (How the Codebase Was Built)

The implementation follows a clear engineering workflow from architecture to validation:

1. Scope and architecture definition
- Defined a Manus-style role split: `Planner` -> `Worker` -> `Verifier`.
- Locked deterministic routing in code (`continue/replan/end`) using `LangGraph`.

2. Contract-first runtime implementation
- Implemented typed interfaces and runtime state with `Pydantic`.
- Added modular role agents, environment adapters, and tool registry.

3. OpenAI integration and execution modes
- Integrated official OpenAI client adapter with retry, JSON parsing, and redaction.
- Added dual behavior profiles: `CodeAct` and `ReAct`.

4. Configurability for research workflows
- Externalized prompt templates and model/hyperparameter configs.
- Added CLI-level overrides for rapid experiments.

5. Tracing and dataset pipeline
- Implemented run/session tracing (`session.json`, `events.jsonl`) at role boundaries.
- Implemented trace-to-trajectory export for SFT data construction.

6. Education and reproducibility layer
- Added runnable notebooks for role I/O inspection, orchestration loop, and tool-use tasks.
- Added notebook smoke execution scripts for non-interactive validation.

7. Validation gates
- Unit tests validate workflow, tracing, config layering, and dataset export.
- Notebook smoke tests verify end-to-end educational examples remain executable.

## Documentation Index

- Docs home: [`docs/README.md`](docs/README.md)
- Reading guide: [`docs/READING_GUIDE.md`](docs/READING_GUIDE.md)
- Reproduction plan: [`docs/plans/REPRODUCTION_PLAN.md`](docs/plans/REPRODUCTION_PLAN.md)
- Code structure plan: [`docs/plans/CODE_STRUCTURE_PLAN.md`](docs/plans/CODE_STRUCTURE_PLAN.md)
- Tracing/data plan: [`docs/plans/TRAINING_DATA_TRACING_PLAN.md`](docs/plans/TRAINING_DATA_TRACING_PLAN.md)
- Tracing implementation for tuning: [`docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md`](docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md)
- Manus document collection + gap analysis plan: [`docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md`](docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md)
- Notebook education plan: [`docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md`](docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md)
- Architecture overview: [`docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md`](docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md)
- Design principles: [`docs/architecture/MANUS_AGENT_DESIGN_PRINCIPLES.md`](docs/architecture/MANUS_AGENT_DESIGN_PRINCIPLES.md)
- Codebase reading roadmap: [`docs/architecture/CODEBASE_READING_ROADMAP.md`](docs/architecture/CODEBASE_READING_ROADMAP.md)
- CodeAct/ReAct design: [`docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md`](docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md)
- Orchestration deep dive: [`docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md`](docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md)
- Planner pseudocode: [`docs/architecture/MANUS_PLANNER_PSEUDOCODE.md`](docs/architecture/MANUS_PLANNER_PSEUDOCODE.md)
- Education notebooks: [`notebooks/education/README.md`](notebooks/education/README.md)
- Reference snapshots: [`references/README.md`](references/README.md)

## Implemented Features

## 1) Runtime Architecture

- Deterministic orchestration via a `LangGraph` state machine.
- Three subagents with typed role boundaries (`Pydantic` schemas).
- Explicit routing decisions in code: `continue`, `replan`, `end`.

Primary source files:
- Graph workflow: `src/manus_three_agent/graph/workflow.py`
- Router transitions: `src/manus_three_agent/graph/transitions.py`
- Shared state/types/schemas: `src/manus_three_agent/core/`

## 2) Hybrid Agentic Profiles (`CodeAct` + `ReAct`)

- Single runtime supports:
  - `codeact`: action-first and tool-grounded execution.
  - `react`: thought-action-observation loop behavior.
- `agentic_mode` is propagated through runtime state, prompts, and trace payloads.
- Mode defaults can be overridden by user prompt files and context variables.

Primary source files:
- Mode prompt profiles: `src/manus_three_agent/prompts/modes.py`
- Runtime mode types: `src/manus_three_agent/core/types.py`
- CLI override plumbing: `src/manus_three_agent/eval/runner.py`

## 3) Provider Integration (OpenAI-Compatible)

- Uses official `openai` Python SDK through a dedicated adapter for OpenAI-compatible providers.
- Structured JSON parsing with retry (`tenacity`) and redaction support.
- Default provider profile is Hugging Face Inference Router.
- Supports flexible env fallback:
  - `LLM_PROVIDER` (`huggingface` or `openai`)
  - `HF_TOKEN` / `HF_BASE_URL`
  - `OPENAI_API_KEY` / `OPENAI_BASE_URL`

Primary source file:
- LLM wrapper: `src/manus_three_agent/utils/llm.py`

## 4) Prompt Configuration

- Role prompts are defined in `configs/prompts/*.yaml`.
- Runtime supports:
  - `--prompt-override` for custom prompt templates.
  - `--prompt-context` for shared context variables.
  - `--prompts-dir` for custom prompt directory resolution.
- Merge precedence is explicit and stable:
  1. Mode profile defaults
  2. Prompt override file
  3. Prompt context variables

Config examples:
- Prompt overrides: `configs/prompt_overrides.example.yaml`
- Prompt context: `configs/prompt_context.example.yaml`

## 5) Hyperparameter Configuration

- Base model stack by role in `configs/models.yaml`.
- Supports both file-level and CLI-level overrides.
- Role-specific CLI controls include:
  - `model`
  - `temperature`
  - `top_p`
  - `max_completion_tokens`
- Advanced fields supported:
  - `frequency_penalty`
  - `presence_penalty`
  - `timeout_seconds`
  - `extra_params`

Config example:
- `configs/model_overrides.example.yaml`

## 6) Tooling Layer

- Extensible tool registry abstraction.
- Built-in tools:
  - `calculator`
  - `fetch_url`
- Notebook demonstrations include:
  - `wiki_search`
  - `wiki_summary`

Primary source files:
- Registry contracts: `src/manus_three_agent/tools/base.py`
- Built-ins: `src/manus_three_agent/tools/builtin.py`

## 7) Tracing and Trajectory Data

Each run can produce:
- `session.json`
- `events.jsonl`

Trace stream includes:
- Role boundary events (`planner/worker/verifier` input/output)
- LLM/tool telemetry
- Episode lifecycle events (`episode_end`, `episode_error`)

Training export:
- `trace -> trajectory JSONL` conversion is implemented for SFT workflows.

Primary source files:
- Tracing subsystem: `src/manus_three_agent/tracing/`
- SFT exporter: `src/manus_three_agent/training/build_sft_data.py`

## 8) Evaluation CLI

Commands:
- `run-episode`: execute one episode with full runtime overrides.
- `build-trajectories`: convert traces into training datasets.
- `print-effective-config`: inspect merged runtime/model/prompt configuration.

CLI entrypoint:
- `src/manus_three_agent/eval/runner.py`

## 9) Education Notebooks

Three runnable notebooks are included:

1. `01_inspect_planner_worker_verifier_io.ipynb`
- Inspects role contracts for planner, worker, verifier.
- Compares behavior between `codeact` and `react`.

2. `02_orchestration_loop_live.ipynb`
- Implements a manual orchestration loop in notebook cells.
- Compares manual transitions against the production LangGraph workflow.

3. `03_tool_use_search_summary_agentic_task.ipynb`
- Demonstrates a realistic tool-use pipeline (`search -> summarize`).
- Includes verifier gating and tool trace visibility.

Notebook smoke scripts:
- `scripts/execute_notebook_cells.py`
- `scripts/run_education_notebooks.sh`

## 10) Test Coverage and Quality Gates

Implemented tests cover:
- Mock orchestration behavior
- Tracing infrastructure
- Training export paths
- Configuration flexibility

Latest validation snapshot (local, February 24, 2026):
- `pytest -q` -> **13 passed**
- `./scripts/run_education_notebooks.sh` -> **3/3 notebooks passed**

Representative tests:
- `tests/test_mock_workflow.py`
- `tests/test_tracing_infra.py`
- `tests/test_training_export.py`
- `tests/test_config_flexibility.py`

## Quick Start

1. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2. Configure environment
```bash
cp .env.example .env
# default path: set HF_TOKEN (HF Inference Router)
# optional: use OPENAI_API_KEY for OpenAI
```

Provider switch examples:
```bash
# Hugging Face (default)
export LLM_PROVIDER=huggingface
export HF_TOKEN=hf_xxx
export HF_BASE_URL=https://router.huggingface.co/v1

# OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-xxx
unset HF_TOKEN
```

3. Run mock episode
```bash
manus3-run run-episode --goal "Build an agent evaluation checklist" --mock
```

4. Run CodeAct mode
```bash
manus3-run run-episode --goal "Evaluate planning quality" --agentic-mode codeact --trace
```

5. Run ReAct mode
```bash
manus3-run run-episode --goal "Evaluate planning quality" --agentic-mode react --trace
```

6. Run with prompt/model overrides
```bash
manus3-run run-episode \
  --goal "Design a benchmark for planner reliability" \
  --agentic-mode codeact \
  --model-override configs/model_overrides.example.yaml \
  --prompt-override configs/prompt_overrides.example.yaml \
  --prompt-context configs/prompt_context.example.yaml \
  --architect-temperature 0.1 \
  --print-effective-config
```

7. Build trajectories
```bash
manus3-run build-trajectories --trace-dir artifacts/traces --output data/processed/trajectory_sft.jsonl
```

8. Run notebook smoke test
```bash
./scripts/run_education_notebooks.sh
```

## Repository Layout

```text
manus_3subagent_repro/
  configs/
  docs/
  notebooks/education/
  references/
  scripts/
  src/manus_three_agent/
  tests/
```

## Security Notes

- `.env` is ignored by git.
- Do not commit API keys or secrets.
- LLM tracing includes OpenAI-style key redaction patterns.

## Reference Refresh

To refresh reference snapshots:
```bash
./scripts/download_references.sh
```
