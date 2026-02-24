# Manus AI Agent Reproduction (3 Subagents, CodeAct + ReAct)

Repository này hiện thực một runtime agent theo hướng Manus-style với 3 vai trò rõ ràng:
1. `Planner` (`ArchitectAgent`)
2. `Worker` (`WorkerAgent`)
3. `Verifier` (`CriticAgent`)

Mục tiêu:
- Cung cấp scaffold chạy được end-to-end với OpenAI client.
- Hỗ trợ cả hai style `CodeAct` và `ReAct` trong cùng codebase.
- Tạo trace/trajectory data có lineage để phục vụ tuning theo role.

## Navigation

- Docs home: [`docs/README.md`](docs/README.md)
- Reading guide: [`docs/READING_GUIDE.md`](docs/READING_GUIDE.md)
- Reproduction plan: [`docs/plans/REPRODUCTION_PLAN.md`](docs/plans/REPRODUCTION_PLAN.md)
- Code structure plan: [`docs/plans/CODE_STRUCTURE_PLAN.md`](docs/plans/CODE_STRUCTURE_PLAN.md)
- Tracing/data plan: [`docs/plans/TRAINING_DATA_TRACING_PLAN.md`](docs/plans/TRAINING_DATA_TRACING_PLAN.md)
- Tracing tuning plan: [`docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md`](docs/plans/TRAJECTORY_TRACING_TUNING_PLAN.md)
- Manus source + gap plan: [`docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md`](docs/plans/MANUS_DOCUMENT_COLLECTION_AND_GAP_PLAN.md)
- Notebook education plan: [`docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md`](docs/plans/JUPYTER_NOTEBOOK_EDUCATION_PLAN.md)
- Architecture overview: [`docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md`](docs/architecture/AGENT_FRAMEWORK_ARCHITECTURE.md)
- CodeAct/ReAct design: [`docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md`](docs/architecture/CODEACT_REACT_HYBRID_DESIGN.md)
- Orchestration deep dive: [`docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md`](docs/architecture/MANUS_AGENT_ORCHESTRATION_DEEP_DIVE.md)
- Planner pseudocode: [`docs/architecture/MANUS_PLANNER_PSEUDOCODE.md`](docs/architecture/MANUS_PLANNER_PSEUDOCODE.md)
- Education notebooks: [`notebooks/education/README.md`](notebooks/education/README.md)
- Reference snapshots: [`references/README.md`](references/README.md)

## Implemented Feature Inventory

## 1) Runtime Architecture

- Deterministic orchestration bằng `LangGraph` state machine.
- 3 subagents có boundary typed (`Pydantic` schemas).
- Explicit routing: `continue / replan / end` trong code, không ẩn trong prompt.

Code:
- Graph workflow: `src/manus_three_agent/graph/workflow.py`
- Router transition: `src/manus_three_agent/graph/transitions.py`
- Core state/types/schemas: `src/manus_three_agent/core/`

## 2) Hybrid Agentic Modes (`CodeAct` + `ReAct`)

- Một codebase chạy được cả:
  - `codeact`: ưu tiên action/tool-grounded execution.
  - `react`: ưu tiên thought-action-observation loop.
- Mode được propagate xuyên suốt runtime/state/trace.
- Prompt profile mặc định theo mode, vẫn cho phép user override thêm.

Code:
- Mode profile: `src/manus_three_agent/prompts/modes.py`
- Runtime mode config: `src/manus_three_agent/core/types.py`
- CLI mode override: `src/manus_three_agent/eval/runner.py`

## 3) OpenAI Integration (Production Path)

- Dùng `openai` Python SDK qua adapter riêng.
- JSON-response parsing + retry (tenacity) + secret redaction.
- Hỗ trợ `OPENAI_BASE_URL` cho endpoint compatible.

Code:
- LLM client wrapper: `src/manus_three_agent/utils/llm.py`

## 4) Prompt Configuration Flexibility

- Base prompts theo role: `configs/prompts/*.yaml`
- Override prompt theo file YAML: `--prompt-override`
- Shared context variables: `--prompt-context`
- Chỉ định prompt dir tùy ý: `--prompts-dir`
- Merge precedence rõ: mode defaults -> prompt override -> prompt context

Files:
- Base prompts: `configs/prompts/architect.yaml`, `worker.yaml`, `critic.yaml`
- Example override: `configs/prompt_overrides.example.yaml`
- Example context: `configs/prompt_context.example.yaml`

## 5) Hyperparameter Configuration Flexibility

- Base model config cho từng role trong `configs/models.yaml`
- Override theo file: `--model-override`
- Quick CLI override per-role:
  - model
  - temperature
  - top_p
  - max_completion_tokens
- Support thêm `frequency_penalty`, `presence_penalty`, `timeout_seconds`, `extra_params`

Files:
- Base: `configs/models.yaml`
- Example override: `configs/model_overrides.example.yaml`

## 6) Tooling Layer

- Tool registry mở rộng được.
- Built-in tools:
  - `calculator`
  - `fetch_url`
- Notebook demo có thêm `wiki_search` + `wiki_summary`.

Code:
- Registry: `src/manus_three_agent/tools/base.py`
- Built-ins: `src/manus_three_agent/tools/builtin.py`

## 7) Tracing and Trajectory Data

- Mỗi run có thể ghi:
  - `session.json`
  - `events.jsonl`
- Có đầy đủ role boundary events (`planner/worker/verifier`) và lifecycle events.
- Export trace -> training trajectory JSONL.

Code:
- Tracing infra: `src/manus_three_agent/tracing/`
- Exporter: `src/manus_three_agent/training/build_sft_data.py`

## 8) Evaluation CLI

- `run-episode`: chạy một episode với full config override.
- `build-trajectories`: build dataset từ traces.
- `print-effective-config`: in merged runtime/model/prompt config để audit.

Code:
- CLI runner: `src/manus_three_agent/eval/runner.py`

## 9) Education Notebooks (Runnable)

Đã build 3 notebook chi tiết, chạy được:
1. `01_inspect_planner_worker_verifier_io.ipynb`
- Inspect input/output của planner, worker, verifier.

2. `02_orchestration_loop_live.ipynb`
- Hiện thực orchestration loop trực tiếp trong notebook.
- So sánh loop thủ công với LangGraph workflow.

3. `03_tool_use_search_summary_agentic_task.ipynb`
- Demo tool-use từ search -> summary cho agentic task.
- Có verifier review và tool trace.

Kèm smoke runner:
- `scripts/execute_notebook_cells.py`
- `scripts/run_education_notebooks.sh`

## 10) Tests and Quality Gates

- Unit tests cho config flexibility, tracing, training export, workflow mock run.
- Notebook smoke execution script để đảm bảo các code cells chạy được.

Tests:
- `tests/test_mock_workflow.py`
- `tests/test_tracing_infra.py`
- `tests/test_training_export.py`
- `tests/test_config_flexibility.py`

## Quick Start

1. Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

2. Environment
```bash
cp .env.example .env
# set OPENAI_API_KEY in .env
```

3. Run episode (mock)
```bash
manus3-run run-episode --goal "Build an agent evaluation checklist" --mock
```

4. Run episode (CodeAct)
```bash
manus3-run run-episode --goal "Evaluate planning quality" --agentic-mode codeact --trace
```

5. Run episode (ReAct)
```bash
manus3-run run-episode --goal "Evaluate planning quality" --agentic-mode react --trace
```

6. Run with model/prompt overrides
```bash
manus3-run run-episode \
  --goal "Design benchmark for planner" \
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

8. Run education notebook smoke test
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

- `.env` được ignore bởi git.
- Không commit API keys/secrets.
- LLM tracing có redaction cho OpenAI key patterns.

## Reference Collection

Refresh reference snapshots:
```bash
./scripts/download_references.sh
```
