#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${PYTHON_BIN:-}" ]]; then
  PYTHON_EXE="$PYTHON_BIN"
elif [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_EXE="$ROOT_DIR/.venv/bin/python"
elif [[ -x "$ROOT_DIR/../.venv/bin/python" ]]; then
  PYTHON_EXE="$ROOT_DIR/../.venv/bin/python"
else
  PYTHON_EXE="python3"
fi

"$PYTHON_EXE" "$ROOT_DIR/scripts/execute_notebook_cells.py" \
  "$ROOT_DIR/notebooks/education/01_inspect_planner_worker_verifier_io.ipynb" \
  "$ROOT_DIR/notebooks/education/02_orchestration_loop_live.ipynb" \
  "$ROOT_DIR/notebooks/education/03_tool_use_search_summary_agentic_task.ipynb"
