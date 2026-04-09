---
name: agent-collab
description: Cross-agent collaboration, knowledge sharing, task handoffs, and timestamped memory logging. Use when (1) working on a shared project with other agents, (2) handing off a task you can't complete, (3) picking up someone else's work, (4) logging progress on any task, (5) checking what other agents have been doing. Provides automatic timestamps and shared context.
---

# Agent Collaboration

Tools for multi-agent projects, handoffs, and shared knowledge.

## ⚠️ Know Who You're Talking To

**Critical:** When you receive a message via `sessions_send` or `sessions_spawn`, it may be from **another agent**, not from Pat (the human). Check the message content and session metadata for clues.

### Agent Directory (active agents)
| Name | ID | Telegram Account | Role |
|------|-----|-----------------|------|
| **Main** | main | default | Primary assistant, orchestrator (Opus) |
| **Jess** | q35 | jessa | Local-first fast execution (Qwen 3.5-35B) |
| **Codex** | codex | gamma | Cloud coding agent (GPT-5.3 Codex) |

**Pat (the human)** talks to you via Telegram DM. If a message comes through `sessions_send`/`sessions_spawn`, it's almost certainly another agent.

### When Sending Messages to Other Agents

Always identify yourself at the start:

```
[From: Main] Hey Codex, can you check the backup auth issue?
```

Or in sessions_spawn tasks:

```
[From: Main] Task: Fix GitHub SSH key for backup push. Context: ...
```

### When Receiving Messages from Other Agents

1. **Note who sent it** — log it in your memory: "Received request from Main to..."
2. **Reply with your identity** — "This is Codex. I'll handle that."
3. **Log the interaction** — so future sessions know who collaborated:
   ```bash
   memlog "Received task from Main: fix backup auth. Working on it."
   ```

### When Logging Interactions

Always include WHO you talked to:

```bash
memlog "Discussed voice pipeline with Main. Agreed on jess as default voice."
memlog "Handed off backup auth to Codex. They confirmed pickup."
memlog "Got update from Jess: memory manager running, ctx hygiene clean."
```

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
memlog "HANDOFF to [agent]: [task]. Blocked: [reason]. Next: [what to do]. Files: [list]"

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
memlog "PICKUP from [agent]: Continuing [task]. Current state: [summary]"
```

## Reading Another Agent's Workspace

You can read any agent's files for context:
- **Memory:** `~/.openclaw/workspace-<id>/memory/YYYY-MM-DD.md`
- **Long-term:** `~/.openclaw/workspace-<id>/MEMORY.md`
- **Identity:** `~/.openclaw/workspace-<id>/IDENTITY.md`
- **Tools:** `~/.openclaw/workspace-<id>/TOOLS.md`

## Task Checklist Pattern

For multi-step projects, create a checklist in SHARED_CONTEXT.md:

```markdown
### Project Name
- [x] Step 1 — completed by Main (2026-02-28 15:30)
- [x] Step 2 — completed by Jess (2026-02-28 16:00)
- [ ] Step 3 — assigned to Codex
- [ ] Step 4 — unassigned
```

## Finding Knowledge

- **What's everyone working on?** → `SHARED_CONTEXT.md`
- **What happened today?** → `~/.openclaw/workspace-*/memory/$(date +%Y-%m-%d).md`
- **Project ideas?** → `IDEAS.md`
- **Agent-specific knowledge?** → `~/.openclaw/workspace-<agent>/MEMORY.md`
- **Voice setup?** → `skills/local-voice/references/SETUP_GUIDE.md`
- **System info?** → `TOOLS.md` in any workspace

## Project Lifecycle

Use the `project` CLI to track work formally:

```bash
project start "name" "what you're doing"     # Creates file in projects/active/
project update "name" "progress note"         # Appends to active project
project handoff "name" "full state dump"      # Moves to projects/handoffs/
project complete "name" "summary"             # Moves to projects/completed/
project pick "name"                           # Pick up a handoff, move to active
project list                                  # Show all projects by status
```

The `projects/` directory is symlinked into every workspace — all agents see the same projects.

### Auto-Handoff When Context Is High

If your context usage exceeds **75%**:
1. Run `project handoff` with a COMPLETE state dump — everything the next agent needs
2. Include: what's done, what's not, files modified, decisions made, blockers
3. Log via memlog
4. Stop taking on new work — let another agent pick it up

Check your context: use the `session_status` tool or `/status` command.

## Agent Comms Platform

All agents have access to `comms` — an internal messaging platform.

### Session Startup
At the start of every session, run:
```bash
comms unread
```
This shows any messages from other agents you haven't seen yet.

### How to Use

```bash
# Channels (like Slack channels)
comms post general "message"              # Post to #general
comms post projects "status update"       # Post to #projects
comms read general                        # Read recent messages

# Direct Messages
comms dm codex "need your help with X"    # DM another agent
comms read-dm codex                       # Read DM conversation

# Threads (focused discussions within channels)
comms thread projects "voice-pipeline" "Here's what I found..."
comms read-thread projects "voice-pipeline"

# Discovery
comms channels                            # List all channels + threads
comms unread                              # What's new since I last checked
comms search "keyword"                    # Search all messages
```

### When to Use What
- **comms post** — status updates, announcements, general coordination
- **comms dm** — ask another agent for help, share context 1:1
- **comms thread** — deep dive on a specific project/topic
- **sessions_send** — need real-time response from another agent (they run immediately)
- **project** tool — formal project tracking (started → handoff → completed)

### Check Comms During Heartbeats
Add to your heartbeat routine: check `comms unread` and respond to any pending messages.
