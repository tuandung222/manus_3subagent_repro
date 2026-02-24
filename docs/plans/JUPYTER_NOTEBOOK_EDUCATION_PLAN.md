# Education Notebook Program Plan (Planning and Orchestration for LLM Agent Systems)

## 0) Program Goals

Build an end-to-end runnable notebook curriculum for two audiences:

- `Agent Architects`: orchestration design, state-machine reasoning, routing/failure control.
- `Data Scientists`: trace quality analysis, dataset curation, and tuning pipelines.

Guiding rule: each notebook must run independently and produce explicit outputs.

## 1) Curriculum Design

## Track A: Foundation (Required)

1. `01_agent_baseline_architecture.ipynb`
- Goal: understand the three-role runtime (Planner/Worker/Verifier).
- Output: one complete run trace with role transitions.

2. `02_prompt_and_hyperparameter_control.ipynb`
- Goal: override prompts/model config and evaluate behavior changes.
- Output: comparative table across configurations.

3. `03_tracing_and_trajectory_export.ipynb`
- Goal: inspect raw traces and construct role-specific datasets.
- Output: sample records for `planner_sft`, `worker_sft`, `verifier_sft`.

## Track B: Architect-Focused

4. `04_orchestration_transitions_and_replanning.ipynb`
- Goal: visualize transitions and detect loop/degenerate routing patterns.
- Output: transition heatmap and replan diagnostics.

5. `05_parallel_planning_wide_research_lite.ipynb`
- Goal: prototype multi-branch planning and branch merge strategies.
- Output: side-by-side comparison (`single-plan` vs `parallel-plan`).

## Track C: Data Scientist-Focused

6. `06_dataset_quality_and_leakage_checks.ipynb`
- Goal: verify deduplication, lineage consistency, and split hygiene.
- Output: markdown + JSON quality report.

7. `07_role_specific_tuning_baseline.ipynb`
- Goal: establish baseline tuning for planner/worker/verifier.
- Output: before/after metric tables.

8. `08_evaluation_and_ablation.ipynb`
- Goal: run ablations across prompt, hyperparameter, and routing policies.
- Output: leaderboard and recommendation summary.

## 2) Standard Notebook Structure

Every notebook should include seven sections:

1. `Context and learning goals`
2. `Environment setup`
3. `Configuration/data loading`
4. `Core experiment`
5. `Analysis and visualization`
6. `Failure cases`
7. `Takeaways and next steps`

## 3) Runtime and Reproducibility Standards

- Python 3.11+
- `pip install -e .[dev]`
- Deterministic seed for demo paths
- Stable paths relative to repository root
- Artifact export to `artifacts/reports/notebooks/`

## 4) Recommended Practice Datasets

1. Synthetic task suite (low cost, high reproducibility).
2. Real-tool mini suite (`fetch_url`, `calculator`).
3. Failure-injected suite (timeouts, malformed outputs, missing context).

## 5) Notebook "Runnable" Criteria

1. Run-all succeeds end to end.
2. No hidden dependency on previous notebook state.
3. Includes an explicit `Expected output` checkpoint cell.
4. Emits artifacts to deterministic paths.

## 6) Implementation Timeline

## Phase 1 (2 days)
- Scaffold three foundation notebooks from tutorial template.
- Create minimal demo data for all examples.

## Phase 2 (3 days)
- Complete two architect-focused notebooks.
- Add transition visualizations and replanning diagnostics.

## Phase 3 (3 days)
- Complete three data-science notebooks.
- Add dataset-quality checks and tuning baseline workflow.

## Phase 4 (1 day)
- Perform run-all QA across notebooks.
- Publish role-based navigation guide.

## 7) Deliverables

1. Eight notebooks in `notebooks/education/`.
2. `notebooks/education/README.md` with role-based learning paths.
3. Notebook smoke-test script suitable for lightweight CI.

## 8) Risks and Mitigations

1. Long runtime and token costs.
- Mitigation: mock-first defaults and small-batch settings.

2. Notebook maintenance complexity.
- Mitigation: shared helper utilities and reduced code duplication.

3. Local environment drift.
- Mitigation: pinned dependencies and pre-workshop smoke checks.
