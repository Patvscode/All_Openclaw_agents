# MEMORY.md

Long-term working memory for MAIN (private to main session contexts).

## User Baseline
- User: Patrick Mello (Pat)
- Timezone: America/New_York
- System: DGX Spark (128GB RAM, GB10 GPU)

## Operating Priorities
- Reliability first, then efficiency.
- Local-first model routing when quality allows.
- Keep paid model usage sustainable (target <=70% usage with buffer).
- Use concise updates; store heavy logs in files instead of chat.

## Core Execution Policy
1. Local-first attempt for routine work.
2. Escalate to heavier local model for hard tasks.
3. Escalate to paid/remote model only for high-risk/high-leverage blockers.
4. Save artifacts to files and return summaries.

## Agent/Telegram Topology (current)
- default -> main
- alpha -> flash
- beta -> prime
- bob -> bob
- gamma -> codex
- max -> max

## High-Value Local Ops Toolkit
Use these scripts for reliability + efficiency:
- `tools/agent_ops/run_triage.sh`
- `tools/agent_ops/budget_router.py`
- `tools/agent_ops/snapshot_openclaw_usage.py`
- `tools/agent_ops/usage_daily_summary.py`
- `tools/agent_ops/file_preflight.sh`

## Model/Context Discipline
- Keep effective context below hard limits and trigger compaction early when needed.
- Prefer summary-only outputs for heavy logs.
- Use per-model context windows and soft thresholds to avoid abort/retry loops.

## Hugging Face / Model Download Workflow (local)
When asked to fetch a model and wire it into OpenClaw:
1. Verify access/token (HF token validity + gated repo permission).
2. Download into a deterministic local path.
3. Validate files/checkpoints exist.
4. Update OpenClaw model/provider config.
5. Restart gateway and smoke test model invocation.
6. Log outcome + blocker in memory and reports.

## Must-remember Practical Lessons
- Aborts do not always kill child processes; verify and clean up runaways.
- Long tool dumps bloat context and cost; summarize and persist to files.
- For stable ops, use watchdog/cron snapshots and nightly usage summaries.

## Linked Reference Files
- `WORKSPACE_MAP.md` for where everything lives.
- `LESSONS.md` for distilled reliability/efficiency patterns.
- `OPUS_RUNBOOK.md` for model-specific operating discipline.
