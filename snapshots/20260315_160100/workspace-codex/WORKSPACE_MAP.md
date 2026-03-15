# WORKSPACE_MAP.md — CODEX

Canonical navigation map for CODEX.

## Read Order (Main Session)
1. `SOUL.md`
2. `USER.md`
3. `MEMORY.md`
4. `RESUME.md`
5. `LESSONS.md`
6. `CODEX_RUNBOOK.md`
7. `WORKSPACE_MAP.md`

## Core Files
- `AGENTS.md` — operating rules and behavior contract
- `SOUL.md` — persona / execution style
- `IDENTITY.md` — agent identity
- `USER.md` — who Pat is and how to help well
- `MEMORY.md` — long-term curated memory
- `memory/YYYY-MM-DD.md` — daily working log
- `RESUME.md` — live continuity snapshot
- `TOOLS.md` — local commands + environment notes
- `LESSONS.md` — distilled operational lessons
- `SHARED_CONTEXT.md` — current shared project state
- `AGENT_PLAYBOOK.md` — shared team playbook

## High-Value Work Areas
- `AI-Scientist-jess/` — Jess AI-Scientist environment setup and smoke tests
- `tools/` — platform services, scripts, and backend components
- `skills/` — local skills and related references
- `memory/` — daily notes / durable continuity

## Ops Toolkit
Main toolkit lives in `workspace-main/tools/agent_ops/`:
- `run_triage.sh`
- `file_preflight.sh`
- `budget_router.py`
- `snapshot_openclaw_usage.py`

## External Control Points
- OpenClaw config: `~/.openclaw/openclaw.json`
- Agent configs: `~/.openclaw/agents/<name>/agent/`
- Gateway status: `openclaw status`
- Hub root: `~/.openclaw/hub/`
- Comms backend: `~/.openclaw/comms/web/server.py`
- RAG DB: `~/.openclaw/arena/knowledge/rag.db`

## Service / Platform Anchors
- Hub / Clawboard: `:8090`
- Comms: `:8096`
- Research Lab: `:8097`
- Watchdog: `:8098`
- Perception Engine: `:8099`
- Memory Concierge: `:8102`
- Knowledge Engine: `:8110`
- llama.cpp: `:18080`
- Gateway: `:18789`

## Quick Sanity Checklist
- Is the target service reachable / healthy?
- Is someone else already working this area? (`SHARED_CONTEXT.md`, board)
- Is there a current card to grab or continue?
- Do I need file preflight before reading a large file?
- Should heavy output go to a file instead of chat?
- Did I update `RESUME.md` before/after meaningful work?
