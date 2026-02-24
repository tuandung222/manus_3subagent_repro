# CodeAct + ReAct Hybrid Design

## Mục tiêu

Một codebase duy nhất chạy được cả hai phong cách:
- `CodeAct`: ưu tiên hành động thực thi và tool-grounded execution.
- `ReAct`: ưu tiên loop suy luận - hành động - quan sát.

## Cách bật mode

- CLI flag: `--agentic-mode codeact|react`
- Runtime config: `configs/base.yaml -> agentic_mode`

CLI override luôn có ưu tiên cao hơn file config.

## Wiring trong mã nguồn

- Runtime mode: `core/types.py` (`RuntimeConfig.agentic_mode`)
- State propagation: `core/state.py` (`ManusState.agentic_mode`)
- Prompt profile theo mode: `prompts/modes.py`
- Planner/Worker/Verifier mode-aware:
  - `agents/architect.py`
  - `agents/worker.py`
  - `agents/critic.py`
- Orchestration trace payload mang `agentic_mode`: `graph/workflow.py`

## Hành vi hiện tại theo mode

### CodeAct
- Prompt profile hướng tới action/tool concretization.
- Mock worker có tool request minh họa ở bước đầu.
- Thích hợp benchmark về tool-use reliability.

### ReAct
- Prompt profile hướng tới thought-action-observation loop.
- Mock planner/worker đổi style summary theo ReAct.
- Thích hợp benchmark về iterative reasoning control.

## Prompt precedence

1. Mode prompt profile (mặc định theo `agentic_mode`)
2. User `--prompt-override`
3. User `--prompt-context`

=> Cho phép vừa giữ behavior mặc định theo mode, vừa custom sâu theo use case.

## Khuyến nghị tuning

- Tune Planner riêng cho từng mode để tránh trộn tín hiệu decomposition.
- Worker dataset nên split theo mode vì khác distribution tool usage.
- Verifier (Critic) nên học thêm feature `agentic_mode` để tránh bias routing.
