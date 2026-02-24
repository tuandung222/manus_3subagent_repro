# Manus Planner (Architect) - Pseudocode and Design Notes

## 1. Vai trò Planner

Planner (`ArchitectAgent`) chịu trách nhiệm:
1. Phân rã goal thành `steps` hữu hạn.
2. Đảm bảo step đủ cụ thể cho Worker.
3. Hỗ trợ replanning khi Critic yêu cầu.

Contract output:
```json
{
  "steps": [
    {"title": "...", "rationale": "..."}
  ]
}
```

## 2. Input contract

Planner nhận:
- `goal`
- `observation` (state mới nhất từ environment)
- `action_history` (những gì worker đã làm)
- `use_cot` (gợi ý reasoning depth)
- `step` (index để trace)

## 3. Planner inference pseudocode

```text
FUNCTION PLAN(goal, observation, action_history, use_cot, step):
  IF force_mock OR openai_key_missing:
    RETURN MOCK_PLAN(goal)

  (system_prompt, user_prompt) = RENDER_PROMPT(
    role="architect",
    goal=goal,
    observation=observation,
    action_history=action_history,
    use_cot=use_cot
  )

  raw_json = OPENAI_CHAT_JSON(
    model=model_config.model,
    generation_config=model_config.to_openai_chat_params(),
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    trace_context={agent:"architect", step:step}
  )

  steps = VALIDATE_LIST(raw_json["steps"], PlanStepSchema)

  IF steps is empty:
    RETURN MOCK_PLAN(goal)

  RETURN PlanOutput(steps)
```

## 4. Replanning pseudocode

```text
FUNCTION REPLAN_IF_NEEDED(state):
  IF state.decision != "replan":
    RETURN state.plan

  new_plan = PLAN(
    goal=state.goal,
    observation=state.observation,
    action_history=state.action_history,
    use_cot=state.use_cot,
    step=state.step_count
  )

  state.plan = new_plan.steps
  state.current_step_idx = 0
  state.notes += ["Architect created/replaced execution plan."]
  RETURN state.plan
```

## 5. Planner quality heuristics (đề xuất)

1. `Step granularity`: mỗi step nên có mục tiêu quan sát được.
2. `Dependency ordering`: step sau chỉ phụ thuộc output step trước.
3. `Termination readiness`: plan phải có đường dẫn ra final answer.
4. `Fallback readiness`: nếu tool fail, có nhánh thay thế.

## 6. Planner-specific tracing

Nên log ít nhất:
- `architect_input`:
  - goal, observation summary, action_history_len
- `llm_call`:
  - model, generation_config, prompts, parsed_output
- `architect_output`:
  - step_count và list steps

## 7. Prompting strategy cho Planner

Prompt nên chứa:
1. Mục tiêu cuối cùng và ràng buộc.
2. State hiện tại ngắn gọn.
3. Output schema cứng (strict JSON).
4. Tiêu chí đánh giá step tốt (cụ thể, đo được, tuần tự).

Ví dụ skeleton:
```text
System: You are ArchitectAgent. Output strict JSON only.
User:
  Goal: ...
  Observation: ...
  Action history: ...
  Return JSON: {"steps": [{"title":..., "rationale":...}]}
```

## 8. Failure handling cho Planner

- JSON parse fail: retry (tenacity) và log parse_error.
- Schema fail: reject output, fallback mock plan hoặc trigger replan.
- Hallucinated step: Critic phát hiện mismatch và route về replanning.
