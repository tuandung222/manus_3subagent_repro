# Education Notebooks

Bộ notebook này phục vụ 2 nhóm:
- Agent Architect: hiểu và kiểm chứng orchestration loop.
- Data Scientist: inspect role I/O và tool trajectories để phục vụ tuning.

## Notebook List

1. `01_inspect_planner_worker_verifier_io.ipynb`
- Inspect input/output contracts của Planner, Worker, Verifier.
- So sánh hành vi theo `codeact` và `react`.

2. `02_orchestration_loop_live.ipynb`
- Hiện thực orchestration loop thủ công ngay trong notebook.
- So sánh kết quả loop thủ công với LangGraph workflow chính thức.

3. `03_tool_use_search_summary_agentic_task.ipynb`
- Demo agentic task `search + summary` với tool pipeline.
- Có verifier decision và tool trace để audit.

## Run Order

Khuyến nghị chạy theo thứ tự `01 -> 02 -> 03`.

## Run Requirements

- Đang đứng ở repo root: `manus_3subagent_repro/`
- Environment đã cài:
```bash
source /Users/admin/TuanDung/paper_implementation/.venv/bin/activate
pip install -e .[dev]
```

## Smoke Test (non-Jupyter)

Chạy kiểm tra toàn bộ code cells của 3 notebook:
```bash
./scripts/run_education_notebooks.sh
```

Script này không phụ thuộc `nbconvert`; nó parse `.ipynb` và thực thi tuần tự các code cells.

## Optional: Open in Jupyter

Nếu muốn mở notebook UI:
```bash
jupyter notebook notebooks/education
```
