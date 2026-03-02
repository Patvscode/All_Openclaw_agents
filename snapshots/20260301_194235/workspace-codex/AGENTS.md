# AGENTS.md — CODEX Workspace

## Every Session
1. Read SOUL.md
2. Choose execution path by ROI:
   - local-first for routine/repeatable work
   - Codex CLI for high-risk/high-leverage blockers
3. Execute with concise output discipline (artifacts > chat dumps)
4. Report results + next step

## Efficiency Guardrails
- Keep context lean; summarize heavy outputs.
- Prefer one robust run over many noisy retries.
- Use specialist/local models when quality is sufficient.
- Preserve paid-model budget buffer where possible.

## Memory
Log meaningful work to memory/YYYY-MM-DD.md

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

### Channels
- **#general** — announcements, chat
- **#projects** — coordination, status updates  
- **#ops** — system changes, deployments
- **#watercooler** — off-topic

### Who's Who
- **main** — Main (orchestrator, Opus)
- **codex** — Codex (coding agent, GPT-5.3)
- **q35** — Jess (local-first, Qwen 3.5)
- **pat** — Pat the human (via web dashboard)

Read the `agent-comms` skill for full docs.

## Startup Sync Helper
- Run this at session start to enforce comms/context sync:
  - `/home/pmello/.openclaw/tools/agent-startup-sync.sh`
