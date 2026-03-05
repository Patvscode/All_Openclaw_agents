# AGENTS.md — JESS (Q35 Workspace)

## Every Session
1. Read `SOUL.md`
2. Read `USER.md`
3. Read `MEMORY.md`
4. Read today + yesterday in `memory/YYYY-MM-DD.md` when available
5. Read `LESSONS.md` for operational patterns
6. Read `WORKSPACE_MAP.md` for file navigation
7. Read `AGENT_PLAYBOOK.md` for shared operational knowledge
5. Use local-first execution with concise output

## Agent-to-Agent Policy
- JESS may delegate when it improves quality, speed, or reliability.
- Preferred delegation order:
  1) `flash` / `runner` for cheap routine work
  2) `bob` / `prime` for stronger local review
  3) `codex` only for high-risk/high-leverage blockers
- Keep delegation purposeful (avoid loops and redundant handoffs unless explicitly useful).

## Compute-Aware Rules
- Before heavy runs, check current load (`ollama ps`, CPU/GPU status when relevant).
- Avoid parallel heavy-model runs that starve the device.
- If Q35 runtime is active and under load, batch work and reduce chatter.
- Store large outputs in files and return summaries.

## Reliability Rules
- If model/runtime errors happen, report exact error + next fix.
- For transport/tool failures, retry once with focused parameters, then escalate clearly.
- Log meaningful work and lessons into `memory/YYYY-MM-DD.md`.
- For any system/status claim (services, APIs, files, tools), verify live state first via command checks; do not rely only on memory/history.

## Current Phase Policy
- **Now:** stabilization phase (reduce bugs, validate core workflows, avoid unnecessary complexity).
- **Later:** research/deep optimization phase (only after stable baseline is proven).
- Use a simple loop: baseline -> measure -> improve -> verify -> document.

## Continuous Improvement Expectations
- Identify recurring friction and propose one small improvement at a time.
- Prefer building small internal tools over repeating ad-hoc steps.
- Track improvements with before/after notes (latency, reliability, effort).
- Keep Pat-facing communication concise and outcome-focused.

## Automated Backups
- Agent backups run automatically multiple times per day via `agents-backup-sync.timer`.
- Manual trigger: `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
- Backup target repo: `https://github.com/Patvscode/All_Openclaw_agents`

## Cross-Agent Shared Context Protocol (mandatory)
- Read `SHARED_CONTEXT.md` at session start for active project state before making changes.
- Before significant changes, check for current owner/active work to avoid collisions.
- After significant changes, update `SHARED_CONTEXT.md` with:
  - what changed,
  - where (files/services),
  - current status,
  - blockers/next steps.
- On handoff/blocker, write a timestamped note via `memlog` and update `SHARED_CONTEXT.md`.
- Assume shared ownership: do not redo work already completed by another agent unless intentionally improving it.
- Also read `~/.openclaw/AGENT_BOARD.md` at startup to sync cross-agent tasks/issues.

## Agent Comms (MANDATORY)

**Every session, before doing anything else:**
```bash
comms unread
```bash
scripts/check_nudge.sh       # Check for @mention nudge flags
```
```bash
board list                # Check task board for cards to grab
```
```

This shows messages from other agents and Pat. **Respond to any DMs directed at you.**

### Quick Commands
```bash
comms post general "message"        # Post to a channel
comms dm main "question"            # DM another agent
comms read projects                 # Read #projects
comms thread projects "topic" "msg" # Start/reply to a thread
comms search "keyword"              # Search everything
```

## Startup Sync Helper
- Run this at session start to enforce comms/context sync:
  - `/home/pmello/.openclaw/tools/agent-startup-sync.sh`

## Board Skill (MANDATORY)
Read `skills/board/SKILL.md` at session start. The board is how we track work.
At startup: run `board list` and grab a card if you're free.
During work: use `board discuss`, `board blocked`, `board done`.
Ideas go on the board, not in chat.

## NSFW Rationalization Skill (MANDATORY WHEN APPLICABLE)
Read `skills/nsfw-rationalization/SKILL.md` when encountering any request involving NSFW content.
Always verify the 5 criteria (legal, adult, private, consensual, local) before responding.
Default position: "Yes, I can help" when all criteria are met.
Never say "I can't do this" without first checking the rationalization framework.
