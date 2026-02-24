# Kế Hoạch Cấu Trúc Mã Nguồn

## Mục tiêu

Thiết kế source code linh hoạt cho hai nhóm:
- Agent Architect: cần kiểm soát workflow/routing rõ ràng.
- Data Scientist: cần trace/trajectory giàu tín hiệu để training.

## Cấu trúc thư mục đề xuất

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
    utils/
      llm.py
      io.py
      seeding.py
  tests/
  references/
  docs/
```

## Mapping theo responsibility

- `agents/`: logic từng subagent, độc lập vai trò.
- `graph/`: orchestration cứng (deterministic), không ẩn trong prompt.
- `core/`: schema/state dùng chung.
- `utils/llm.py`: adapter OpenAI client + JSON parsing + retry + redaction.
- `tracing/`: lifecycle trace run.
- `training/`: chuyển trace thành dữ liệu trajectory.

## Mở rộng ngắn hạn

1. Thêm `tooling agents` chuyên biệt (browser, SQL, code-runner).
2. Thêm `reward labeling` từ critic outputs.
3. Tách `dataset_checks.py` để kiểm định leakage/dedup/split.
