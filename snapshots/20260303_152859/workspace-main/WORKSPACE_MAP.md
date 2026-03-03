# WORKSPACE_MAP.md

Canonical navigation map for MAIN.

## Read Order (Main Session)
1. `SOUL.md`
2. `USER.md`
3. `MEMORY.md`
4. `OPUS_RUNBOOK.md`
5. `WORKSPACE_MAP.md` (this file)

## Core Files
- `AGENTS.md` — operating rules and behavior contract
- `SOUL.md` — persona/voice constraints
- `IDENTITY.md` — who MAIN is
- `USER.md` — who MAIN is helping
- `MEMORY.md` — long-term curated memory
- `memory/YYYY-MM-DD.md` — daily working log
- `TOOLS.md` — quick commands + local environment notes
- `OPUS_RUNBOOK.md` — Opus-specific execution discipline
- `LESSONS.md` — distilled operational lessons and failure patterns

## Ops Toolkit
- Directory: `tools/agent_ops/`
- Start here: `tools/agent_ops/README.md`
- Most-used:
  - `run_triage.sh`
  - `file_preflight.sh`
  - `budget_router.py`
  - `snapshot_openclaw_usage.py`
  - `usage_daily_summary.py`

## Telemetry Paths
- Usage logs: `logs/usage/*.jsonl`
- Usage reports: `reports/usage/*.md`
- Agent triage reports: `reports/agent_ops/*.md`

## External Control Points
- OpenClaw config: `~/.openclaw/openclaw.json`
- Gateway status: `openclaw status --deep`
- Telegram account->agent bindings live in config `bindings`.

## Quick Sanity Checklist
- Does `openclaw status --deep` show gateway reachable?
- Is target bot bound to expected agent/model?
- Is context pressure below 95% soft ceiling?
- Are heavy outputs written to files (not chat)?
