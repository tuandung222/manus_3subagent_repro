# Code Structure Plan

## Objective

Define a code structure that remains practical for both:

- **Agent Architects** who need deterministic control flow and explicit routing.
- **Data Scientists** who need clean role boundaries and high-signal trace data for training.

## Proposed Repository Structure

```text
manus_3subagent_repro/
  configs/
    base.yaml
    models.yaml
    tracing.yaml
    prompts/
  src/manus_three_agent/
    agents/
      architect.py
      worker.py
      critic.py
    graph/
      workflow.py
      transitions.py
    environments/
      base.py
      simulator.py
      factory.py
    tools/
      base.py
      builtin.py
      factory.py
    tracing/
      schemas.py
      collector.py
      writer.py
    training/
      build_sft_data.py
    eval/
      runner.py
      metrics.py
    core/
      schemas.py
      state.py
      types.py
    prompts/
      templates.py
      modes.py
    utils/
      llm.py
      io.py
      seeding.py
  notebooks/education/
  tests/
  references/
  docs/
```

## Responsibility Mapping

- `agents/`: role-specific logic for Planner, Worker, Verifier.
- `graph/`: deterministic orchestration and transition policy.
- `core/`: shared state schemas and runtime types.
- `utils/llm.py`: OpenAI adapter, JSON parsing, retry, secret redaction.
- `tracing/`: lifecycle telemetry and event persistence.
- `training/`: trace-to-trajectory dataset construction.
- `eval/`: runnable CLI and offline metrics entrypoints.

## Design Constraints

1. Keep transition logic in code, not in prompts.
2. Keep role I/O contracts strongly typed.
3. Keep runtime config externalized and override-friendly.
4. Keep trace schema stable and versioned.
5. Keep every run reproducible through config and seed controls.

## Short-Term Extension Plan

1. Add specialized tooling agents (browser, SQL, code runner).
2. Add reward-label generation from verifier outputs.
3. Add `dataset_checks.py` for leakage, deduplication, and split integrity.
4. Add benchmark harnesses for CodeAct vs ReAct ablation.

## Acceptance Criteria

- New contributors can map architecture responsibilities from the folder layout alone.
- Each runtime subsystem has focused tests and clear ownership.
- Dataset extraction logic is isolated from orchestration logic.
- Prompt/model changes do not require source edits.
