# Kế Hoạch Thu Thập Tài Liệu về Manus + Gap Analysis Reproduction

## 0) Nguyên tắc

- Ưu tiên nguồn chính thức (official docs/blog/API/help center).
- Mỗi nguồn phải có: URL, loại tài liệu, ngày truy cập, độ tin cậy, ghi chú.
- Tách rõ: `facts` (xác thực được) và `inference` (suy luận kiến trúc).

Ngày baseline kế hoạch: **24/02/2026**.

## 1) Nguồn cần thu thập (ưu tiên)

## 1.1 Tier-0: Official product/docs
- [Manus Docs](https://manus.im/docs)
- [Open Manus API Docs](https://open.manus.ai/docs)
- [Manus Help Center](https://help.manus.im)
- [Manus Trust Center](https://trust.manus.im/)

## 1.2 Tier-0: Official blog/updates
- [Manus Blog Index](https://manus.im/blog)

Các bài kỹ thuật nên track định kỳ:
- [Context Engineering for AI Agents](https://manus.im/blog/context-engineering-for-ai-agents)
- [Wide Research: Beyond Context Window Limitations](https://manus.im/blog/wide-research-beyond-context-window-limitations)
- [Sandbox Explanations and Security](https://manus.im/blog/how-manus-keeps-sandbox-safe-and-dynamic)
- [Manus Browser Operator](https://manus.im/features/manus-browser-operator)
- [Why Do AI Agents Need Concurrent Cloud Workspaces?](https://manus.im/blog/why-ai-agents-need-concurrent-cloud-workspaces)

## 1.3 Tier-1: API compatibility and ecosystem
- [OpenAI Compatibility (Manus API)](https://open.manus.ai/docs/openai-sdk-compatibility)
- [Task creation reference](https://open.manus.ai/docs/api-reference/tasks/create-a-task)
- [Webhooks overview](https://open.manus.ai/docs/webhooks/webhooks-overview)

## 1.4 Tier-2: Comparative/external analysis
- Research blogs và community reverse-engineering (gắn nhãn `non-official`).
- Dùng để tạo hypothesis, không dùng làm “ground truth”.

## 2) Quy trình thu thập tài liệu

### Bước A: Discovery
1. Crawl chỉ mục docs/blog theo tuần.
2. Gắn tag từng bài: `architecture`, `tooling`, `planner`, `safety`, `api`, `eval`.

### Bước B: Ingestion
1. Lưu snapshot HTML/PDF vào `references/raw/`.
2. Ghi metadata vào catalog CSV/JSONL:
- `source_url`, `source_type`, `collected_at_utc`, `version_hint`, `trust_tier`.

### Bước C: Extraction
1. Trích key claims theo template chuẩn.
2. Liên kết claim -> section -> evidence quote ngắn.
3. Đánh dấu claim có ảnh hưởng trực tiếp đến kiến trúc runtime/tracing.

### Bước D: Review
1. Weekly review: có gì mới ảnh hưởng roadmap.
2. Mở issue cho từng gap reproduce mới phát hiện.

## 3) Gap analysis: yếu tố chưa reproduce đầy đủ

Dựa trên docs/blog hiện có, các khoảng trống chính:

1. **Wide Research / concurrent workspaces**
- Hiện repro chưa có planner phân rã song song nhiều subagents + merge strategy.

2. **Context engineering nâng cao**
- Chưa có KV-cache-aware context serialization, tool masking có điều kiện, context layering.

3. **Cloud sandbox lifecycle**
- Chưa reproduce model workspace dạng sandbox lâu dài, isolation policy, persistence semantics.

4. **Project-level memory/instructions**
- Chưa có “Projects” abstraction: persistent instruction/profile/knowledge base theo project.

5. **Connector ecosystem + MCP orchestration**
- Chưa có connector manager, auth lifecycle, policy cho external systems.

6. **Task modes & agent profiles**
- Chưa map đầy đủ mode (`agent/chat/adaptive`) và profile switching (lite/max), cùng cost controls.

7. **Human-interactive task state**
- Chưa hỗ trợ pending-human-input state + resume flow.

8. **Production webhook/event bus**
- Chưa có webhook consumer chuẩn hóa signature verify + retry semantics.

9. **Planner quality controls**
- Chưa có explicit planner confidence scoring + plan risk model.

10. **Verifier robustness**
- Verifier hiện còn rule-based đơn giản, chưa có reward-supervised verifier model.

## 4) Kế hoạch bù gap (theo ưu tiên)

### Priority P0
- Tracing v2 + role-specific training datasets.
- Verifier tuning pipeline.

### Priority P1
- Parallel planning (Wide Research-lite) + branch merge.
- Project memory layer + instruction hierarchy.

### Priority P2
- Connector/MCP runtime + policy.
- Webhook event consumer + resume states.

### Priority P3
- Sandbox fidelity, cost/performance optimizer, profile switching.

## 5) Deliverables

1. `references/MANUS_SOURCES_CATALOG.csv` (nâng cấp từ registry hiện có).
2. `docs/analysis/MANUS_GAP_ANALYSIS.md` (liên tục cập nhật).
3. Issue board theo gap + milestone kỹ thuật.

## 6) Tần suất cập nhật

- Crawl snapshot: 2 lần/tuần.
- Gap review: 1 lần/tuần.
- Re-prioritization: 2 tuần/lần.
