# AGENTS.md — CODEX Workspace

## Every Session
1. Read SOUL.md — who you are
2. Read MEMORY.md — long-term knowledge (system architecture, ports, what you built)
3. Read LESSONS.md — operational patterns and gotchas
4. Read RESUME.md — where you left off
5. Read memory/YYYY-MM-DD.md (today + yesterday) for recent context
6. Read AGENT_PLAYBOOK.md for shared operational knowledge
7. Run `comms unread` — check for messages from other agents/Pat
8. Run `agent-startup-sync.sh` — enforce full sync

## Knowledge-First Rule (CRITICAL)
When asked about research, papers, technical topics, or system knowledge:
1. **FIRST** check `memquery "topic"` — fast RAG search (20K+ chunks, 122+ papers)
2. **THEN** check memory files / memory_search
3. **ONLY THEN** fall back to `web_search` if internal sources have nothing
The `knowledge-rag-inject` hook auto-injects relevant RAG into your context already.

## Efficiency Guardrails
- Keep context lean; summarize heavy outputs to files
- Prefer one robust run over many noisy retries
- Preserve paid-model budget buffer
- Your free weekly Codex credits reload weekly — still be efficient

## Reliability Checkback Rule
- When working on runtime-critical tasks, check health every 30-60 min
- Post concise status in Agent Comms when state changes

## Memory
Log meaningful work to memory/YYYY-MM-DD.md. Update RESUME.md continuously.

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


## Proactive Work Rule (MANDATORY)
At session start and every idle moment:
1. `board list in-progress` — if you have a card, work on it
2. `board list todo` — if no in-progress card, **grab one immediately**
3. If no cards fit, create one: `board add "idea" --col todo` then grab it
4. Idle is not an option. Always be building, learning, or improving.

## Board Skill (MANDATORY)
Read `skills/board/SKILL.md` at session start. The board is how we track work.
At startup: run `board list` and grab a card if you're free.
During work: use `board discuss`, `board blocked`, `board done`.
Ideas go on the board, not in chat.

## Memory Concierge (automatic, always running)
- **CLI:** `memquery "question"` — search unified memory store
- **Deep:** `memquery --deep "question"` — 0.8b answers from history
- When resuming after context reset, check: `memquery --deep "what was Codex last working on?"`
