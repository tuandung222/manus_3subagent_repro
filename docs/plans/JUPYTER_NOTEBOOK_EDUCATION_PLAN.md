# Kế Hoạch Bộ Jupyter Notebook Đào Tạo (Planning & Orchestration cho Agentic LLM)

## 0) Mục tiêu chương trình

Xây bộ notebook chạy được end-to-end cho 2 nhóm:
- `Agent Architect`: tập trung orchestration, state machine, failure routing.
- `Data Scientist`: tập trung trace quality, dataset curation, tuning loops.

Nguyên tắc: mỗi notebook phải chạy được độc lập, có checkpoint output rõ ràng.

## 1) Thiết kế curriculum

## Track A: Foundation (bắt buộc)
1. `01_agent_baseline_architecture.ipynb`
- Mục tiêu: hiểu runtime 3 vai trò Planner/Worker/Verifier.
- Output: 1 run trace hoàn chỉnh.

2. `02_prompt_and_hyperparameter_control.ipynb`
- Mục tiêu: override prompt/model config, đo ảnh hưởng lên quality.
- Output: bảng so sánh nhiều cấu hình.

3. `03_tracing_and_trajectory_export.ipynb`
- Mục tiêu: đọc trace thô, build role-specific datasets.
- Output: `planner_sft`, `worker_sft`, `verifier_sft` samples.

## Track B: Architect-focused
4. `04_orchestration_transitions_and_replanning.ipynb`
- Mục tiêu: visualize state transitions, detect loop/degenerate routing.
- Output: transition heatmap + stop/replan diagnostics.

5. `05_parallel_planning_wide_research_lite.ipynb`
- Mục tiêu: prototype multi-branch planning và merge strategy.
- Output: comparative run (`single-plan` vs `parallel-plan`).

## Track C: Data Scientist-focused
6. `06_dataset_quality_and_leakage_checks.ipynb`
- Mục tiêu: dedup, lineage checks, split hygiene.
- Output: quality report markdown + json artifact.

7. `07_role_specific_tuning_baseline.ipynb`
- Mục tiêu: tuning baseline nhỏ cho planner/worker/verifier.
- Output: before/after metric table.

8. `08_evaluation_and_ablation.ipynb`
- Mục tiêu: ablation prompt/hyperparam/transition policies.
- Output: leaderboard + recommendation summary.

## 2) Chuẩn cấu trúc cho mỗi notebook

Mọi notebook phải có 7 phần:
1. `Context & learning goals`
2. `Environment setup`
3. `Load configs/data`
4. `Core experiment`
5. `Analysis & visualization`
6. `Failure cases`
7. `Takeaways + next steps`

## 3) Chuẩn runtime/reproducibility

- Python 3.11+
- `pip install -e .[dev]`
- deterministic seed cho notebook demo
- notebook dùng đường dẫn tương đối ổn định từ repo root
- export artifact vào `artifacts/reports/notebooks/`

## 4) Dữ liệu thực hành đề xuất

1. Synthetic task suite (ít tốn chi phí, dễ tái lập).
2. Real-tool mini suite (fetch_url/calculator).
3. Failure-injected suite (tool timeout, malformed output).

## 5) Tiêu chí “chạy được” cho notebook

1. Run-all thành công từ đầu đến cuối.
2. Không có hidden state phụ thuộc session cũ.
3. Có cell “Expected output” để người học đối chiếu.
4. Sinh artifact tại đường dẫn xác định.

## 6) Kế hoạch triển khai notebook (theo skill jupyter-notebook)

### Phase 1 (2 ngày)
- Scaffold 3 notebook foundation bằng template tutorial.
- Tạo dữ liệu demo nhỏ đi kèm.

### Phase 2 (3 ngày)
- Hoàn thiện 2 notebook Architect track.
- Thêm visualization transitions và replanning diagnostics.

### Phase 3 (3 ngày)
- Hoàn thiện 3 notebook Data Scientist track.
- Bổ sung dataset checks + tuning baseline.

### Phase 4 (1 ngày)
- QA toàn bộ “run all” + checklist chất lượng.
- Viết guide điều hướng học theo vai trò.

## 7) Deliverables

1. Bộ `8` notebook trong `notebooks/education/`.
2. `notebooks/education/README.md` (learning path theo vai trò).
3. Script smoke test notebook (chạy CI mức tối thiểu).

## 8) Rủi ro và giảm thiểu

1. Runtime dài, tốn token:
- Dùng mock-first path + small batch settings cho demo.

2. Notebook khó bảo trì:
- Chuẩn hóa helper utils, tránh lặp code qua nhiều notebook.

3. Drift môi trường local:
- Pin dependencies + check script trước khi workshop.
