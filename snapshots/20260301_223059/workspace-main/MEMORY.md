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

## Agent Comms Platform (2026-03-01)
- Built internal messaging: `comms` CLI + web dashboard (Clawboard module 21, port 8096)
- Channels: #general, #projects, #ops, #watercooler. DMs, threads, search.
- Profiles with display names (q35→Jess, etc.)
- `broadcast` for alerts + `nudge` for specific agents
- Cron nudges ONLY for cloud agents — local agents (q35/Jess) get messages via file/heartbeat
- Web UI at http://100.109.173.109:8090/21-agent-comms/

## Project Tracker (2026-03-01)
- `project` CLI: start/update/handoff/complete/pick/list
- ~/.openclaw/projects/ with active/completed/handoffs dirs

## Jess Reliability Lessons (2026-03-01)
- SWA cache invalidation = full prompt reprocess every message
- Context reduced to 64K (was 131K) to improve response time
- NEVER spawn concurrent sessions for local model agents
- q35 was missing from agentToAgent.allow — always verify all agents included
- jess-keeper (Python script) handles memory — doesn't touch the model

## Workspace Cleanup (2026-03-01)
- Archived 17 unused workspaces to ~/.openclaw/archive/workspaces/
- Hub moved to ~/.openclaw/hub/ (independent of agent workspaces)
- 3 active: main, q35 (Jess), codex (Codex/Gamma)

## Pat's Comms Design Vision (pending implementation)
- DMs = instant notification
- Group chats = inject unread count into agent memory (no wake/token burn)
- Urgency judgment — not everything needs a ping
- Combination of session-start check + memory injection + targeted nudges

## Agent Comms Platform v2 (2026-03-01)
- Full mobile-responsive web UI at hub/21-agent-comms/
- Features: media uploads, bookmarks/library, @mention autocomplete + auto-nudge, message grouping, lightbox, timestamp formatting
- Backend: comms/web/server.py (Python, port 8096) — endpoints for upload, bookmarks, nudge, broadcast
- @mention nudges gated to human authors only (prevents agent loops)
- Nudge messages explicitly say "reply in comms, NOT Telegram"
- Comms guide at ~/.openclaw/comms/COMMS_GUIDE.md
- Key lesson: Python 3.14 has no cgi module; smooth scroll causes reflow drift in chat UIs
- Open: rate-limit nudges (not yet implemented)
