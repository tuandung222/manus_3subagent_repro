# CodeAct + ReAct Hybrid Design

## Objective

This project intentionally supports two distinct agent behavior profiles in the same runtime:

- `CodeAct`: action-forward, tool-grounded execution style.
- `ReAct`: thought-action-observation loop style.

The design goal is to enable controlled benchmarking and training-data collection across both behaviors without forking architecture.

## How to Enable a Mode

- CLI flag: `--agentic-mode codeact|react`
- Runtime config: `configs/base.yaml -> agentic_mode`

CLI options always take precedence over static configuration files.

## Source Wiring

Mode is propagated through all critical boundaries:

- Runtime configuration: `core/types.py` (`RuntimeConfig.agentic_mode`)
- State propagation: `core/state.py` (`ManusState.agentic_mode`)
- Prompt defaults by mode: `prompts/modes.py`
- Role agents (mode-aware):
  - `agents/architect.py`
  - `agents/worker.py`
  - `agents/critic.py`
- Trace payload propagation: `graph/workflow.py`

## Current Runtime Behavior by Mode

## `codeact`

- Prompt profile emphasizes concrete tool decisions and action execution.
- Mock worker demonstrates tool requests early in the episode.
- Best used when evaluating tool reliability and execution grounding.

## `react`

- Prompt profile emphasizes iterative reasoning summaries between actions.
- Mock planner/worker produce response style aligned with ReAct loops.
- Best used when evaluating iterative planning and reasoning control.

## Prompt Resolution Precedence

Prompt composition is deterministic and auditable:

1. Mode prompt profile defaults (from `agentic_mode`)
2. User prompt override (`--prompt-override`)
3. User prompt context variables (`--prompt-context`)

This layering preserves stable defaults while still allowing deep customization.

## Recommended Tuning Strategy

- Train Planner separately per mode to avoid decomposition-signal mixing.
- Split Worker datasets by mode due to different tool-usage distributions.
- Include `agentic_mode` as an input feature for Verifier training to reduce routing bias.

## Evaluation Recommendations

- Keep the same benchmark tasks across modes for fair comparison.
- Record `agentic_mode` in every trace event for clean ablation analysis.
- Report at least:
  - task success rate
  - average steps to completion
  - replan frequency
  - tool-call success ratio
