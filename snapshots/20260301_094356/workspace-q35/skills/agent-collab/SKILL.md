---
name: agent-collab
description: Cross-agent collaboration, knowledge sharing, task handoffs, and timestamped memory logging. Use when (1) working on a shared project with other agents, (2) handing off a task you can't complete, (3) picking up someone else's work, (4) logging progress on any task, (5) checking what other agents have been doing. Provides automatic timestamps and shared context.
---

# Agent Collaboration

Tools for multi-agent projects, handoffs, and shared knowledge.

## Logging (always use this)

```bash
memlog "Your note here"                    # auto-timestamps, logs to today's memory
memlog "Note" blockers.md                  # log to a specific file
```

Every call auto-adds: timestamp, timezone, agent name. No model overhead.

## Shared Files

| File | Purpose |
|------|---------|
| `~/.openclaw/SHARED_CONTEXT.md` | Active projects, blockers, handoff state — READ FIRST |
| `~/.openclaw/IDEAS.md` | Project ideas & backlog — any agent can add |
| `~/.openclaw/voice-prefs.json` | Shared voice preferences |
| Agent memory | `~/.openclaw/workspace-<agent>/memory/` |

## Before Starting Shared Work

```bash
# 1. Read shared context
cat ~/.openclaw/SHARED_CONTEXT.md

# 2. Check relevant agent's recent memory
ls ~/.openclaw/workspace-<agent>/memory/
cat ~/.openclaw/workspace-<agent>/memory/$(date +%Y-%m-%d).md

# 3. Log that you're starting
memlog "Starting work on [task]. Read context from [agent]'s memory."
```

## Handing Off a Task

When you're blocked (credits, model limits, errors, time):

```bash
# 1. Log detailed state
memlog "HANDOFF: [task]. Blocked: [reason]. Next: [what to do]. Files: [list]"

# 2. Update shared context
# Edit ~/.openclaw/SHARED_CONTEXT.md — update project status + blockers table
```

## Picking Up Someone Else's Task

```bash
# 1. Read shared context
cat ~/.openclaw/SHARED_CONTEXT.md

# 2. Read the handing-off agent's recent memory
cat ~/.openclaw/workspace-<agent>/memory/$(date +%Y-%m-%d).md

# 3. Read their long-term memory for deeper context
cat ~/.openclaw/workspace-<agent>/MEMORY.md

# 4. Log your pickup
memlog "PICKUP: Continuing [task] from [agent]. Current state: [summary]"
```

## Task Checklist Pattern

For multi-step projects, create a checklist in SHARED_CONTEXT.md:

```markdown
### Project Name
- [x] Step 1 — completed by Main (2026-02-28 15:30)
- [x] Step 2 — completed by Jess (2026-02-28 16:00)
- [ ] Step 3 — assigned to Flash
- [ ] Step 4 — unassigned
```

## Finding Knowledge

- **What's everyone working on?** → `SHARED_CONTEXT.md`
- **What happened today?** → `~/.openclaw/workspace-*/memory/$(date +%Y-%m-%d).md`
- **Project ideas?** → `IDEAS.md`
- **Agent-specific knowledge?** → `~/.openclaw/workspace-<agent>/MEMORY.md`
- **Voice setup?** → `skills/local-voice/references/SETUP_GUIDE.md`
- **System info?** → `TOOLS.md` in any workspace
