# Manus Planner (Architect) Pseudocode and Design Notes

## 1) Planner Responsibilities

The Planner (`ArchitectAgent`) is responsible for:

1. Decomposing a goal into finite, executable steps.
2. Producing steps with enough specificity for Worker execution.
3. Regenerating plans when the Verifier requests replanning.

Expected output contract:

```json
{
  "steps": [
    {"title": "...", "rationale": "..."}
  ]
}
```

## 2) Input Contract

Planner input includes:
- `goal`
- `observation` (latest environment state snapshot)
- `action_history` (what the worker already attempted)
- `use_cot` (reasoning-depth hint)
- `step` (trace step index)

## 3) Planner Inference Pseudocode

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

## 4) Replanning Pseudocode

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

## 5) Planner Quality Heuristics

1. `Step granularity`: each step should have observable completion criteria.
2. `Dependency ordering`: later steps should depend only on prior outputs.
3. `Termination readiness`: plan must contain a clear path to final answer synthesis.
4. `Fallback readiness`: plan should include alternatives when tools fail.

## 6) Planner-Specific Tracing Requirements

At minimum, trace:
- `architect_input`
  - goal
  - observation summary
  - action history length
- `llm_call`
  - model
  - generation config
  - prompts
  - parsed output
- `architect_output`
  - step count
  - full step list

## 7) Prompting Strategy for Planner

Planner prompts should include:
1. Final objective and constraints.
2. Condensed current state.
3. Strict output schema (JSON only).
4. Step-quality criteria (specific, measurable, sequential).

Example skeleton:

```text
System: You are ArchitectAgent. Output strict JSON only.
User:
  Goal: ...
  Observation: ...
  Action history: ...
  Return JSON: {"steps": [{"title":..., "rationale":...}]}
```

## 8) Failure Handling Strategy

- JSON parse failure: retry with `tenacity` and log parse error metadata.
- Schema validation failure: reject output, fallback to safe mock plan, or trigger replan.
- Hallucinated or non-executable steps: detected by Verifier and routed back to replanning.
