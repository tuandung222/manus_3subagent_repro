# Tracing Implementation Plan for Trajectory Data Collection (Planner, Worker, Verifier)

## 0) Objectives

Build a tracing foundation that can:

1. Capture role-specific trajectory signals for tuning `Planner`, `Worker`, and `Verifier`.
2. Preserve full lineage from `run -> step -> event -> dataset row`.
3. Support both SFT workflows and preference/reward-modeling pipelines.

## 1) Required Data Scope

## 1.1 Planner (Architect)

- Inputs: goal, observation snapshot, condensed history, tool-availability mask.
- Outputs: plan steps, rationale, confidence, planning metadata.
- Auxiliary labels: verifier verdict per cycle (`continue/replan/end`), final success/failure.

## 1.2 Worker

- Inputs: current step, environment state, allowed tools, prior failures.
- Outputs: action/tool request, tool args, intermediate reasoning summary.
- Outcomes: tool result, environment response, error taxonomy, retry behavior.

## 1.3 Verifier (Critic)

- Inputs: local execution state (plan progress, action traces, evidence).
- Outputs: verdict (`continue/replan/end`), feedback, risk flags.
- Auxiliary labels: verdict mismatch against eventual outcome (ex-post correctness).

## 2) Tracing Schema v2 Design

## 2.1 Session-Level (`session.json`)

- `schema_version`, `run_id`, `goal`, `started_at`, `finished_at`
- `model_stack` (planner/worker/verifier models + hyperparameters)
- `runtime_config` (max steps, prompt sources, tool mode)
- `data_governance` (redaction policy, PII scan status)
- `summary` (success, step count, token/cost estimate, failure class)

## 2.2 Event-Level (`events.jsonl`)

Required event types:

- `planner_input`, `planner_output`
- `worker_input`, `worker_action`, `worker_tool_call`, `worker_tool_result`, `worker_output`
- `verifier_input`, `verifier_output`
- `orchestrator_transition` (`from_state`, `to_state`, `reason`)
- `env_observation`
- `episode_error`, `episode_end`

Mandatory event fields:

- `run_id`, `step`, `event_id`, `event_type`, `timestamp`
- `parent_event_id` (for causal graph reconstruction)
- typed `payload` (not raw free text only)

## 2.3 Derived Training Views

Generate these views automatically:

- `planner_sft.jsonl`
- `worker_sft.jsonl`
- `verifier_sft.jsonl`
- `verifier_pref_pairs.jsonl` (good vs bad verdicts)
- `worker_recovery_cases.jsonl` (failure-to-recovery trajectories)

## 3) Data Collection Pipeline

## Phase A: Instrumentation

1. Standardize event emitters across graph nodes and tool runtime.
2. Record explicit transition reasons at router level.
3. Persist rendered prompts and config hashes per LLM call.

## Phase B: Collection

1. Run benchmark suites (synthetic + real-tool tasks) with matrix coverage.
2. Collect traces using both fixed seeds and random seeds.
3. Keep raw traces immutable (append-only, no in-place edits).

## Phase C: Curation

1. Apply redaction and PII scanning.
2. Run quality checks (missing keys, broken lineage, schema drift).
3. Deduplicate with tuple fingerprinting:
- `(goal_hash, key_steps_hash, final_outcome)`.

## Phase D: Export

1. Export role-specific SFT datasets.
2. Build preference data for Verifier (and selected Planner scenarios).
3. Split train/validation/test by `goal family` to reduce leakage.

## 4) Role-Specific Tuning Plan

## 4.1 Planner

- SFT objective: decomposition and ordering quality.
- Preference objective: favor plans with high completion rate and low replan loops.
- Metrics: plan validity rate, replan rate, downstream success uplift.

## 4.2 Worker

- SFT objective: action selection and argument grounding.
- Preference objective: prioritize strong failure-recovery trajectories.
- Metrics: tool success rate, action efficiency, error recurrence.

## 4.3 Verifier

- SFT objective: grounded `stop/continue/replan` decisions.
- Preference/reward objective: align verdicts with ex-post outcomes.
- Metrics: stop precision/recall, false-stop rate, unnecessary-replan rate.

## 5) Acceptance Criteria

1. 100% of runs produce schema-valid `session.json` and `events.jsonl`.
2. At least 98% of events have valid lineage (`parent_event_id` or root marker).
3. All five derived dataset views export without parse errors.
4. Dataset reports include leakage, deduplication, and class-balance checks.
5. Tuning loops publish role-specific dashboards and summary metrics.

## 6) Two-Week Execution Milestones

- Day 1-2: finalize schema v2 and update emitters.
- Day 3-5: run batch collection and quality checks (v1).
- Day 6-8: implement role-specific exporter and preference builder.
- Day 9-11: run baseline tuning for planner/worker/verifier.
- Day 12-14: run ablations and publish technical report.

## 7) Key Risks and Mitigation

1. Prompt/config drift causes heterogeneous data.
- Mitigation: attach `config_hash`, `prompt_hash`, and `toolset_hash` per run.

2. Sensitive data leakage in traces.
- Mitigation: enforce redaction during collection and post-processing (double pass).

3. Class imbalance (verifier mostly `continue`).
- Mitigation: generate hard cases and inject controlled failure scenarios.

4. Overfitting to synthetic tasks.
- Mitigation: mix real-tool traces with human-corrected trajectories.
