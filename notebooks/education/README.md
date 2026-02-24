# Education Notebooks

This notebook suite is designed for two core audiences:

- **Agent Architects**: understand and validate orchestration behavior.
- **Data Scientists**: inspect role I/O and tool trajectories for tuning workflows.

## Notebook List

1. `01_inspect_planner_worker_verifier_io.ipynb`
- Inspects Planner, Worker, and Verifier input/output contracts.
- Compares behavior across `codeact` and `react` modes.

2. `02_orchestration_loop_live.ipynb`
- Implements a manual orchestration loop directly in notebook cells.
- Compares manual loop behavior with the production LangGraph workflow.

3. `03_tool_use_search_summary_agentic_task.ipynb`
- Demonstrates an agentic `search + summary` tool pipeline.
- Includes verifier decisions and tool traces for auditability.

## Recommended Run Order

Run in sequence: `01 -> 02 -> 03`.

## Runtime Requirements

- Run from repository root: `manus_3subagent_repro/`
- Activate environment and install dependencies:

```bash
source /Users/admin/TuanDung/paper_implementation/.venv/bin/activate
pip install -e .[dev]
```

## Smoke Test (Non-Jupyter Execution)

Execute all code cells in all three notebooks:

```bash
./scripts/run_education_notebooks.sh
```

This script does not require `nbconvert`; it parses `.ipynb` files and executes code cells sequentially.

## Optional: Open in Jupyter UI

```bash
jupyter notebook notebooks/education
```
