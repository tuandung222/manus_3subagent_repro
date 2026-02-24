# Kế Hoạch Hiện Thực Tracing để Thu Thập Trajectory Data (Planner/Worker/Verifier)

## 0) Mục tiêu

Xây dựng hạ tầng tracing có thể:
1. Thu thập trajectory đủ giàu tín hiệu để tuning riêng cho `Planner`, `Worker`, `Verifier`.
2. Giữ lineage đầy đủ từ `run -> step -> event -> dataset row`.
3. Hỗ trợ cả huấn luyện SFT lẫn preference/reward modeling.

## 1) Phạm vi dữ liệu cần thu

### 1.1 Planner (Architect)
- Input: goal, observation snapshot, condensed history, tool availability mask.
- Output: plan steps + rationale + confidence + planning metadata.
- Label phụ trợ: critic verdict sau mỗi cycle (`continue/replan/end`), final success/fail.

### 1.2 Worker
- Input: current step, env state, allowed tools, previous failures.
- Output: action/tool request, tool args, intermediate reasoning summary.
- Outcome: tool result, env response, error taxonomy, retry behavior.

### 1.3 Verifier (Critic)
- Input: full local state (plan progress + action trace + outcome evidence).
- Output: verdict (`continue/replan/end`), feedback, risk flags.
- Label phụ trợ: mismatch giữa verdict và outcome thực tế (ex-post correctness).

## 2) Thiết kế schema tracing v2

## 2.1 Session-level (`session.json`)
- `schema_version`, `run_id`, `goal`, `started_at`, `finished_at`
- `model_stack` (planner/worker/verifier + hyperparameters)
- `runtime_config` (max_steps, prompt sources, tool mode)
- `data_governance` (redaction policy, pii_scan status)
- `summary` (success, step_count, cost/tokens, failure class)

## 2.2 Event-level (`events.jsonl`)
Bắt buộc bổ sung các event chuẩn:
- `planner_input`, `planner_output`
- `worker_input`, `worker_action`, `worker_tool_call`, `worker_tool_result`, `worker_output`
- `verifier_input`, `verifier_output`
- `orchestrator_transition` (from_state, to_state, reason)
- `env_observation`
- `episode_error`, `episode_end`

Mỗi event phải có:
- `run_id`, `step`, `event_id`, `event_type`, `timestamp`
- `parent_event_id` (để dựng graph nhân-quả)
- `payload` typed (không chỉ free text)

## 2.3 Derived views cho training
Sinh tự động 3 view:
- `planner_sft.jsonl`
- `worker_sft.jsonl`
- `verifier_sft.jsonl`

Và 2 view nâng cao:
- `verifier_pref_pairs.jsonl` (good vs bad verdict)
- `worker_recovery_cases.jsonl` (episodes có lỗi + recovery thành công)

## 3) Pipeline thu thập dữ liệu

### Giai đoạn A: Instrumentation
1. Chuẩn hóa event emitters cho cả graph node + tool runtime.
2. Gắn `transition reason` rõ ở router level.
3. Ghi prompt thực tế sau khi render + config hash.

### Giai đoạn B: Collection
1. Chạy benchmark suite (synthetic + real-tool) theo ma trận task.
2. Thu trace theo batch với seed cố định + seed ngẫu nhiên.
3. Lưu raw trace immutable, không sửa tại chỗ.

### Giai đoạn C: Curation
1. Redaction + PII scan.
2. Data quality checks: missing keys, broken lineage, schema drift.
3. Dedup theo `(goal_hash, key_steps_hash, final_outcome)`.

### Giai đoạn D: Export
1. Export role-specific SFT sets.
2. Sinh preference data cho Verifier (và một phần Planner).
3. Split train/val/test theo `goal family` để tránh leakage.

## 4) Kế hoạch tuning theo role

### 4.1 Planner
- SFT: học decomposition + ordering quality.
- Preference: ưu tiên plan có completion rate cao và ít replan loop.
- Metrics: plan validity rate, replan rate, downstream success uplift.

### 4.2 Worker
- SFT: action selection + tool argument grounding.
- Preference: ưu tiên trajectories phục hồi lỗi tốt.
- Metrics: tool success rate, action efficiency, error recurrence.

### 4.3 Verifier
- SFT: quyết định stop/continue/replan có căn cứ.
- Preference/Reward: so verdict với outcome ex-post.
- Metrics: stop precision/recall, false-stop rate, unnecessary-replan rate.

## 5) Đánh giá và acceptance criteria

1. 100% run có `session.json` + `events.jsonl` hợp lệ schema.
2. >= 98% events có lineage hợp lệ (`parent_event_id` hoặc root marker).
3. Sinh được đủ 5 dataset views không lỗi parse.
4. Datasets có report chất lượng: leakage, dedup, class balance.
5. Tuning loop có dashboard metric theo từng role.

## 6) Milestone thực thi (2 tuần)

- Ngày 1-2: chốt schema v2 + cập nhật emitters.
- Ngày 3-5: batch collection + quality checks v1.
- Ngày 6-8: exporter role-specific + preference builder.
- Ngày 9-11: baseline tuning (planner/worker/verifier).
- Ngày 12-14: ablation + báo cáo kết quả.

## 7) Rủi ro chính và giảm thiểu

1. Drift prompt/config làm dữ liệu không đồng nhất:
- Gắn `config_hash`, `prompt_hash`, `toolset_hash` cho mỗi run.

2. Lộ dữ liệu nhạy cảm:
- Redaction ở collector và post-processing (double pass).

3. Mất cân bằng class (verifier mostly continue):
- Chủ động generate hard cases, inject failure scenarios.

4. Overfit vào synthetic:
- Trộn real tool traces + human-in-the-loop correction data.
