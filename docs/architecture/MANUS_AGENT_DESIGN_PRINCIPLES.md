# Manus-Style Agent Design Principles

This document summarizes the design principles used to reproduce a Manus-style agent runtime in this repository.

Scope note:
- This is a **framework-level design interpretation** grounded in implementation and available public product patterns.
- It is **not** a claim of exact internal implementation details of Manus AI.

## 1) Design Goals

A Manus-style agent architecture should optimize for four goals simultaneously:

1. Reliability under long-horizon tasks
- The runtime should complete multi-step goals with predictable control behavior.

2. Controllability for architects
- Routing logic must be explicit, inspectable, and testable in code.

3. Data exhaust for training
- Every meaningful decision boundary should produce structured trace records.

4. Experiment velocity
- Prompt/model/runtime policies should be configurable without code changes.

## 2) Principle: Role Separation by Responsibility

The system is decomposed into three role-specialized agents:

- `Planner (Architect)`: decomposition and re-planning.
- `Worker`: execution and tool-grounded action.
- `Verifier (Critic)`: quality gate and routing decision.

Why this separation matters:
- It reduces prompt overload in a single monolithic agent.
- It creates cleaner supervision surfaces for role-specific fine-tuning.
- It makes failure localization easier (`plan issue` vs `execution issue` vs `verification issue`).

Trade-off:
- More orchestration complexity and cross-role coordination overhead.

## 3) Principle: Deterministic Orchestration in Code

Core routing (`continue`, `replan`, `end`) is encoded in graph transitions, not hidden in free-form prompts.

Benefits:
- Reproducibility across runs.
- Easier unit testing of transition policy.
- Lower risk of prompt drift changing control semantics.

Trade-off:
- Less adaptive than fully emergent prompt-only control.
- Requires explicit policy updates when adding new route states.

## 4) Principle: Typed Role Boundaries

All role I/O contracts are schema-constrained (`Pydantic`).

What this enables:
- Strong validation at boundaries (`PlanStep`, `WorkerOutput`, `CriticOutput`).
- Easier downstream dataset normalization.
- Cleaner compatibility checks when changing prompts/models.

Trade-off:
- Requires careful schema versioning during evolution.

## 5) Principle: Tool-Grounded Execution

Worker behavior is designed around concrete execution and optional tool invocation.

Rationale:
- Tool calls anchor reasoning to observable external effects.
- Tool traces provide rich supervision signals for action selection and recovery tuning.

Design implication:
- Tool registry must be explicit and auditable.
- Tool errors should be first-class events in trace lifecycle.

## 6) Principle: Verifier as Runtime Governor

Verifier is not just a scoring component; it is a **control governor**.

Responsibilities:
- Detect completion readiness.
- Detect risk/failure patterns and trigger re-planning.
- Prevent unnecessary looping by issuing `end` when appropriate.

Why this matters:
- Prevents unbounded action loops in long-horizon tasks.
- Creates a clear decision point for preference/reward modeling.

## 7) Principle: Config-First Architecture

Prompt and model behavior is externalized from orchestration logic.

Config surfaces:
- Runtime policy (`max_steps`, `dynamic_replanning`, `agentic_mode`)
- Role model settings (temperature, top_p, completion tokens, etc.)
- Prompt templates and override context

Benefits:
- Fast ablation cycles.
- Clear experiment reproducibility through config snapshots.

## 8) Principle: Mode-Conditioned Behavior (CodeAct + ReAct)

The same architecture supports two behavior profiles:

- `CodeAct`: action/tool-first style.
- `ReAct`: thought-action-observation loop style.

Design objective:
- Separate behavior strategy from orchestration substrate.
- Keep one runtime while enabling strategy-level experimentation.

Training implication:
- Role datasets should retain `agentic_mode` as a conditioning feature.

## 9) Principle: Tracing as a First-Class Product

Tracing is not a debugging afterthought; it is part of the runtime contract.

Required trace layers:
- Session-level metadata (`run_id`, configs, model stack, status, summary)
- Event-level boundaries (planner/worker/verifier input and output)
- LLM telemetry (prompt/response, usage, latency, parse status)
- Tool and environment events

Why this matters:
- Enables trajectory export for SFT and preference datasets.
- Enables post-mortem analysis and policy audits.

## 10) Principle: Failure-Safe by Design

The runtime enforces bounded execution and explicit failure signaling.

Typical safeguards:
- `max_steps` budget cap
- Parse/API error capture (`episode_error`)
- Empty/invalid plan handling
- Controlled termination semantics (`episode_end`)

Outcome:
- Failures are observable and dataset-usable rather than silent.

## 11) Principle: Evaluation-Aligned Runtime

The architecture is designed to support both online and offline evaluation.

Online:
- Episode success and stop behavior.
- Step-level efficiency and route quality.

Offline:
- Trace replay and data quality checks.
- Role-specific dataset extraction.
- Ablation by prompt/model/policy variants.

## 12) Principle: Separation of Concerns in Source Layout

The codebase layout mirrors system boundaries:

- `eval/`: runtime bootstrap and CLI
- `graph/`: orchestration and transitions
- `agents/`: role logic
- `core/`: state and schemas
- `tools/` and `environments/`: execution interfaces
- `tracing/`: event/session persistence
- `training/`: trace-to-dataset conversion

This reduces coupling and makes architecture review tractable.

## 13) Practical Reading Path for New Contributors

If the repository feels large, follow this order:

1. `eval/runner.py` (entrypoint and run assembly)
2. `graph/workflow.py` + `graph/transitions.py` (control loop)
3. `core/state.py` + `core/schemas.py` (contract surface)
4. `agents/*` (role behavior)
5. `tracing/*` and `training/build_sft_data.py` (data pipeline)

Related guide:
- `docs/architecture/CODEBASE_READING_ROADMAP.md`

## 14) Common Pitfalls and Mitigations

1. Prompt-only control drift
- Mitigation: keep routing in code and test transitions.

2. Data unusable for training
- Mitigation: enforce schema-boundary events and run-level lineage.

3. Hard-to-reproduce experiments
- Mitigation: persist effective runtime/model/prompt config per run.

4. Over-coupled role logic
- Mitigation: keep strict role contracts and minimal shared assumptions.

## 15) What to Add Next (High-Value Extensions)

1. Verifier confidence score for reward modeling.
2. Richer tool-failure taxonomy and recovery labels.
3. Parent-child event lineage IDs for causal trace graphs.
4. Dataset governance checks (dedup, leakage, split integrity) as CI gates.

---

In short, the design philosophy is:
- **Role-specialized cognition**,
- **Code-governed control flow**,
- **Trace-first observability**,
- **Config-driven experimentation**.

That combination is what makes Manus-style agent systems both operationally stable and trainable at scale.
