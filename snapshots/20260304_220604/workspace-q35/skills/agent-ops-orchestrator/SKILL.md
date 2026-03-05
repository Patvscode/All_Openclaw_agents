---
name: agent-ops-orchestrator
description: Orchestrate efficient local agent operations in workspace-codex with scripts for device inventory, model capability scanning, failure-point detection, file preflight sizing, and structured memory logging. Use when building resilient multi-model workflows, diagnosing failures, selecting the right local model/tool path, and controlling context/cost before reading files.
---

## Workflow
Use this skill when you need fast local agent operations in `workspace-codex`: environment triage, local Ollama model selection, recent failure scanning, safe file inspection, and memory logging.

## What it provides
- `tools/agent_ops/run_triage.sh`: one-command orchestrator for inventory + failure summary + Ollama scan + markdown report + memory append + routing recommendation
- `tools/agent_ops/device_inventory.sh`: host/device inventory snapshot
- `tools/agent_ops/ollama_model_capability_scan.sh`: heuristic tags for local Ollama models (`coding`, `reasoning`, `vision`, `embedding`, `tool_likelihood`)
- `tools/agent_ops/failure_monitor_summary.sh`: grep-based recent failure summary across logs/text files
- `tools/agent_ops/file_preflight.sh`: file size/type/line estimate before reading
- `tools/agent_ops/memory_append.sh`: structured daily memory append with lock support
- `tools/agent_ops/snapshot_openclaw_usage.py`: passive OpenClaw usage snapshots to `logs/usage/openclaw_status.jsonl` (prefers `openclaw status --json`, falls back to text parse)
- `tools/agent_ops/log_local_model_activity.py`: passive local model activity samples (`ollama ps`) plus recent triage metadata to `logs/usage/local_model_activity.jsonl`
- `tools/agent_ops/usage_daily_summary.py`: daily markdown metrics/trends/cost-driver summary under `reports/usage/`
- `tools/agent_ops/budget_router.py`: budget-aware routing recommendation from `logs/usage/*.jsonl` with configurable conserve/hard-conserve thresholds
- `tools/agent_ops/summarize_heavy_output.py`: compact summaries for heavy tool outputs (errors/counts/sections/tail examples)
- `tools/agent_ops/install_usage_cron.sh`: idempotent cron installer (15m capture + nightly summary; dry-run by default)

## Recommended flow
1. Default path: run `tools/agent_ops/run_triage.sh` for a single-shot triage report and routing recommendation.
2. Use `tools/agent_ops/run_triage.sh --failure-path <logs_dir> --failure-hours <N> --mode conserve|normal|sprint --budget-hint "<hint>"` to tune scope and routing.
3. Add `--report-summary-only` when triage report size matters and you only need condensed command output sections.
4. Use `python3 tools/agent_ops/budget_router.py [--conserve-threshold N --hard-threshold N]` to get a telemetry-driven `normal|conserve|hard-conserve` recommendation.
5. Run `tools/agent_ops/file_preflight.sh <path>` before opening large files if you need deeper manual inspection.
6. For passive decision telemetry, run:
   - `python3 tools/agent_ops/snapshot_openclaw_usage.py`
   - `python3 tools/agent_ops/log_local_model_activity.py`
   - `python3 tools/agent_ops/usage_daily_summary.py --date today|yesterday`
   - `python3 tools/agent_ops/budget_router.py --print-markdown` (for appending into reports)
7. Install scheduled telemetry safely with `tools/agent_ops/install_usage_cron.sh` (preview) and `tools/agent_ops/install_usage_cron.sh --apply` (write crontab).
8. Run individual scripts directly when you only need one signal (inventory, failures, model scan, memory append, usage telemetry, or report output summarization).

## Notes
- Scripts are shell-based and safe to run without optional tools; they print fallbacks instead of failing hard where practical.
- Keep entries concise and include commands used + high-signal outputs in memory.
- The usage telemetry scripts are Python stdlib executables and append structured JSONL logs for summaries/trends; nightly summary cron also appends a budget-router recommendation section.
