# Current Agent Architecture and Runtime Flow (Reading Roadmap)

This document gives you both:

1. A visual map of the **current implementation architecture**.
2. A practical roadmap for **where to start reading code**.

## 1) Architecture Diagram (Current Implementation)

```mermaid
flowchart LR
  U["User / CLI"] --> C["manus3-run"]
  C --> R["runner.py::run_episode"]
  R --> G["LangGraph workflow"]

  G --> A["ArchitectAgent"]
  G --> W["WorkerAgent"]
  G --> V["CriticAgent"]

  W --> T["Tool Registry"]
  W --> E["Environment Adapter"]

  A --> L["LLMClient"]
  W --> L
  V --> L

  A --> P["PromptTemplates"]
  W --> P
  V --> P

  G --> TR["TraceCollector"]
  TR --> TS["session.json + events.jsonl"]
  TS --> D["build_sft_data.py"]
  D --> O["trajectory_sft.jsonl"]
```

## 2) Runtime Orchestration Flow (Single Episode)

```mermaid
sequenceDiagram
  autonumber
  participant CLI as CLI
  participant Runner as run_episode
  participant Graph as LangGraph
  participant Architect as ArchitectAgent
  participant Worker as WorkerAgent
  participant Env as Environment
  participant Critic as CriticAgent
  participant Router as route_after_critic
  participant Trace as TraceCollector

  CLI->>Runner: manus3-run run-episode
  Runner->>Trace: start_session(...)
  Runner->>Graph: workflow.invoke(initial_state)

  loop Until end
    Graph->>Architect: architect_node(state)
    Architect->>Trace: architect_input / llm_call / architect_output
    Architect-->>Graph: plan

    Graph->>Worker: worker_node(state)
    Worker->>Trace: worker_input / llm_call / worker_output
    Worker->>Env: step(action)
    Env-->>Worker: observation, done, success
    Worker->>Trace: environment_step (+ tool_call if any)
    Worker-->>Graph: updated state

    Graph->>Critic: critic_node(state)
    Critic->>Trace: critic_input / llm_call / critic_output
    Critic-->>Graph: decision

    Graph->>Router: route_after_critic(state)
    Router-->>Graph: continue | replan | end
  end

  Runner->>Trace: episode_end / close(session)
  Runner-->>CLI: artifact summary
```

## 3) State Transition Graph (Deterministic)

```mermaid
flowchart TD
  S["START"] --> A["architect"]
  A --> W["worker"]
  W --> C["critic"]

  C -->|"continue"| W
  C -->|"replan + dynamic_replanning=true"| A
  C -->|"end or done=true"| END["END"]
```

## 4) Trace and Training Data Flow

```mermaid
flowchart LR
  N1["graph nodes"] --> N2["TraceCollector.log_event"]
  N2 --> N3["artifacts/traces/<run_id>/events.jsonl"]
  N2 --> N4["artifacts/traces/<run_id>/session.json"]
  N3 --> N5["build_sft_data.py"]
  N4 --> N5
  N5 --> N6["data/processed/trajectory_sft.jsonl"]
```

## 5) Source-of-Truth Files

If you need exact implementation details, prioritize these files:

1. Entrypoint and runtime bootstrap
- `pyproject.toml` (`manus3-run` script)
- `src/manus_three_agent/eval/runner.py`

2. Orchestration loop and routing policy
- `src/manus_three_agent/graph/workflow.py`
- `src/manus_three_agent/graph/transitions.py`

3. Role loops (Planner / Worker / Verifier)
- `src/manus_three_agent/agents/architect.py`
- `src/manus_three_agent/agents/worker.py`
- `src/manus_three_agent/agents/critic.py`

4. State and typed contracts
- `src/manus_three_agent/core/state.py`
- `src/manus_three_agent/core/schemas.py`
- `src/manus_three_agent/core/types.py`

5. Tracing and trajectory export
- `src/manus_three_agent/tracing/collector.py`
- `src/manus_three_agent/tracing/schemas.py`
- `src/manus_three_agent/utils/llm.py`
- `src/manus_three_agent/training/build_sft_data.py`

## 6) Recommended Reading Order

1. `pyproject.toml`
2. `src/manus_three_agent/eval/runner.py`
3. `src/manus_three_agent/graph/workflow.py`
4. `src/manus_three_agent/graph/transitions.py`
5. `src/manus_three_agent/core/state.py`
6. `src/manus_three_agent/core/schemas.py`
7. `src/manus_three_agent/core/types.py`
8. `src/manus_three_agent/agents/architect.py`
9. `src/manus_three_agent/agents/worker.py`
10. `src/manus_three_agent/agents/critic.py`
11. `src/manus_three_agent/tracing/collector.py`
12. `src/manus_three_agent/training/build_sft_data.py`
13. `tests/`

## 7) Quick Commands While Reading

```bash
manus3-run run-episode --goal "Explain current architecture" --mock --print-effective-config
manus3-run run-episode --goal "Emit trace sample" --mock --trace
manus3-run build-trajectories --trace-dir artifacts/traces --output data/processed/trajectory_sft.jsonl
```
