# Manus Document Collection and Reproduction Gap Analysis Plan

## 0) Principles

- Prioritize official sources (product docs, API docs, help center, trust/security posts).
- Record metadata for every source: URL, source type, retrieval date, trust tier, and notes.
- Separate validated **facts** from architectural **inferences**.

Baseline planning date: **February 24, 2026**.

## 1) Source Collection Priorities

## 1.1 Tier-0: Official Documentation and Product Surfaces
- [Manus Docs](https://manus.im/docs)
- [Open Manus API Docs](https://open.manus.ai/docs)
- [Manus Help Center](https://help.manus.im)
- [Manus Trust Center](https://trust.manus.im/)

## 1.2 Tier-0: Official Blog and Product Updates
- [Manus Blog Index](https://manus.im/blog)

High-value technical posts to track continuously:
- [Context Engineering for AI Agents](https://manus.im/blog/context-engineering-for-ai-agents)
- [Wide Research: Beyond Context Window Limitations](https://manus.im/blog/wide-research-beyond-context-window-limitations)
- [Sandbox Explanations and Security](https://manus.im/blog/how-manus-keeps-sandbox-safe-and-dynamic)
- [Manus Browser Operator](https://manus.im/features/manus-browser-operator)
- [Why Do AI Agents Need Concurrent Cloud Workspaces?](https://manus.im/blog/why-ai-agents-need-concurrent-cloud-workspaces)

## 1.3 Tier-1: API Compatibility and Integration Surfaces
- [OpenAI SDK Compatibility](https://open.manus.ai/docs/openai-sdk-compatibility)
- [Task Creation API](https://open.manus.ai/docs/api-reference/tasks/create-a-task)
- [Webhooks Overview](https://open.manus.ai/docs/webhooks/webhooks-overview)

## 1.4 Tier-2: External Comparative Analyses
- Community reverse-engineering and third-party blogs should be tagged as `non-official`.
- Use these sources for hypotheses and design exploration, not as ground truth.

## 2) Document Collection Workflow

## Step A: Discovery
1. Crawl docs/blog indexes weekly.
2. Tag each source with domain labels such as `architecture`, `planner`, `tooling`, `safety`, `api`, `evaluation`.

## Step B: Ingestion
1. Save HTML/PDF snapshots under `references/raw/`.
2. Append metadata to a catalog (CSV or JSONL):
- `source_url`, `source_type`, `collected_at_utc`, `version_hint`, `trust_tier`.

## Step C: Structured Extraction
1. Extract key claims using a standardized claim template.
2. Link each claim to section-level evidence and short supporting quotes.
3. Mark claims that directly affect orchestration, tooling, and tracing design.

## Step D: Weekly Review
1. Review newly collected material for roadmap impact.
2. Open one issue per newly identified reproduction gap.

## 3) Current Reproduction Gaps

Based on current source coverage, the largest unimplemented areas are:

1. **Wide Research / concurrent workspaces**
- Missing multi-branch planner decomposition with branch merge policy.

2. **Advanced context engineering**
- Missing KV-cache-aware context serialization, conditional tool masking, and layered context scopes.

3. **Cloud sandbox lifecycle fidelity**
- Missing persistent sandbox lifecycle modeling, isolation policy, and durability semantics.

4. **Project-scoped instruction and memory model**
- Missing long-lived "Project" abstraction for instructions, preferences, and knowledge.

5. **Connector ecosystem and MCP orchestration**
- Missing connector lifecycle management, authentication policy, and external system governance.

6. **Task modes and profile switching**
- Missing full mode mapping (`agent`, `chat`, `adaptive`) and profile switching (`lite`, `max`) with explicit cost controls.

7. **Human-interactive execution state**
- Missing `pending-human-input` and resume semantics.

8. **Production-grade webhook/event ingestion**
- Missing normalized signature verification, retries, and dead-letter handling.

9. **Planner quality controls**
- Missing explicit planner confidence scoring and plan-risk scoring.

10. **Verifier robustness and supervision depth**
- Current verifier remains primarily rule-based; no reward-supervised verifier model yet.

## 4) Gap Closure Priorities

## Priority P0
- Tracing v2 schema and role-specific dataset generation.
- Verifier tuning and evaluation pipeline.

## Priority P1
- Parallel planning (Wide Research-lite) with merge strategy.
- Project memory layer and instruction hierarchy.

## Priority P2
- Connector/MCP runtime and policy controls.
- Webhook event consumer with resume flow support.

## Priority P3
- Sandbox fidelity improvements and profile-based cost/performance optimization.

## 5) Deliverables

1. `references/MANUS_SOURCES_CATALOG.csv` (expanded from the current source registry).
2. `docs/analysis/MANUS_GAP_ANALYSIS.md` (continuously updated synthesis).
3. Issue board linked to each gap with milestones and owners.

## 6) Update Cadence

- Snapshot crawl: twice per week.
- Gap review: once per week.
- Priority re-alignment: every two weeks.

## 7) Acceptance Criteria

- Source catalog is complete, versioned, and reproducible.
- Every major architecture decision links to explicit evidence.
- Gap register maps directly to implementation tasks and milestones.
