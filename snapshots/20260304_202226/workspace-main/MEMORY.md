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

## Knowledge Management Process (2026-03-02)

### The 3-Tier System (all agents)
- **Tier 1 (startup):** MEMORY.md, LESSONS.md, TOOLS.md — curated, always read
- **Tier 2 (reference):** OPERATIONS_PLAN, SHARED_CONTEXT, etc. — read when relevant
- **Tier 3 (raw):** memory/YYYY-MM-DD.md, logs/, memlog/ — ephemeral, mine for curation

### The Curation Rule
Daily logs are raw material. Agents must promote important things to Tier 1 at session end.
If it's not in Tier 1, it effectively doesn't exist next session.

### Files Added to All Agent Workspaces
- WORKSPACE_MAP.md — navigation map with tier system and curation rule
- LESSONS.md — operational patterns (created or expanded for each agent)
- AGENTS.md updated to read LESSONS.md + WORKSPACE_MAP.md at startup

### Codex Knowledge Gaps Fixed
- MEMORY.md was 3 lines → populated with system architecture, agent topology, build history
- TOOLS.md was empty template → populated with ports, services, file paths, CLI tools
- LESSONS.md created with UI patterns, CSS gotchas, testing discipline, collaboration rules
- Had scattered reference files (OPERATIONS_PLAN, LEVERAGE_BACKLOG, USAGE_LEDGER) but nothing in startup sequence

### Jess Status
- Runtime healthy (llama.cpp responding, watchdog + memory manager active)
- Needs to complete timed board lifecycle proof (card-dcfb01)
- LESSONS.md expanded from 5 lines to full operational guide

## Agent Live Status System (2026-03-04)
- Status API on port 8094 (systemd: dgx-agent-status.service)
- qwen3.5:0.8b narration — MUST use `"think": false` in Ollama API or it wastes all tokens on thinking
- OpenClaw hook `agent-status-tracker` auto-tracks all agents via message:received/sent events
- Dashboard at hub/16-agent-status/
- Status files at /tmp/agent-status/<agent>.json

## Roadmap Active (2026-03-04)
- Phase 1 DONE: Agent Live Status Dashboard
- Phase 2 NEXT: Vision + Computer Use Pipeline (Playwright → qwen3.5:4b vision → action executor)
- Pat wants: self-growing tool/skill ecosystem — agents create niche tools during computer use, share them universally
- RESUME.md has full continuation briefing — read it after any /new or /reset

## Qwen 3.5 Model Inventory
- 0.8b, 2b, 4b: all in Ollama (small enough to run concurrently, ~7GB total)
- 35b-a3b-q8: runs via raw llama.cpp on port 18080 (Jess)
- 4b is the vision model — key for computer use pipeline

## Computer Use Pipeline (2026-03-04)
- Full browser (Playwright) + desktop (X11/xdotool) computer use
- Vision: qwen3.5:4b analyzes screenshots (~7s browser, ~22s desktop)
- Agent modes: autonomous 4b, agent-model-as-planner, direct action API, mixed
- API on port 8095 (dgx-computer-use.service)
- Self-growing skill ecosystem: learns from successful tasks, saves to skills/discovered/
- Training pipeline: auto-saves observation→action pairs, export as JSONL/OpenAI/pairs
- Dashboard: hub/22-computer-use/ (live sessions, training, library, skills)
- Desktop: DISPLAY=:1, 2560x1440 GNOME, screenshots resized to 1280x720 for vision

## Agent Eval System (2026-03-04)
- 16 tests, 6 categories: Reasoning, Coding, Instructions, Knowledge, JSON, Speed
- API on port 8093 (dgx-agent-eval.service)
- Dashboard: hub/23-agent-eval/
- Results: 4b=94.4%, 2b=82.6%, 0.8b=82.6%
- Key: 4b is the clear best local model. 0.8b is excellent value (same score as 2b for 1/3 the size)

## Model Hub (2026-03-04)
- hub/24-model-hub/: Unified model management + eval integration
- Pull models from Ollama, evaluate from card, leaderboard, routing recommendations
- All new dashboards are mobile-responsive

## Service Port Map (current)
| Service | Port | SystemD |
|---------|------|---------|
| Gateway | 18789 | openclaw-gateway |
| Hub | 8090 | max-web-gallery |
| Comms | 8096 | dgx-comms |
| Status API | 8094 | dgx-agent-status |
| Computer Use | 8095 | dgx-computer-use |
| Eval API | 8093 | dgx-agent-eval |
| Jess llama.cpp | 18080 | jess-watchdog |
| Ollama | 11434 | system |
