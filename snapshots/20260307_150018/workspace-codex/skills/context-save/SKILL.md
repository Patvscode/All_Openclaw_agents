# Context Save — Pre-Reset State Preservation

Save your working state before a context window reset so you (or any agent) can resume cleanly with full understanding and zero wasted tokens.

## When to Use
- User says "back yourself up", "save your state", "I'm going to reset you"
- Before any `/new` or `/reset`
- Before switching to a different model or task that needs a clean window
- Anytime you've done significant work you don't want to lose

## The Process

### Step 1: Assess What Matters

Ask yourself these questions:
1. **What am I currently working on?** (active task, phase, goal)
2. **What did I just finish?** (completed work this session)
3. **What's the next step?** (so future-me can pick up immediately)
4. **What decisions were made?** (design choices, user preferences, rejected approaches)
5. **What did I learn?** (gotchas, bugs hit, workarounds found)
6. **What's the system state?** (services running, ports, files changed, things deployed)

### Step 2: Write RESUME.md

Create or update `RESUME.md` in your workspace root. This is the **single entry point** for resuming work.

Structure:
```markdown
# RESUME.md — Session Continuation Briefing
**Last updated: [date] [time] by [agent name]**
**Read this file first after any /new or /reset to resume work.**

---

## What We're Building
[1-2 sentence summary of the overall project/goal]
[Link to detailed plan file if one exists]

## Completed Work
### [Feature/Phase Name] ✅ ([date])
- [What was built — be specific: files, ports, services, commands]
- [How it works — the architecture in 2-3 bullet points]
- [Key gotcha or lesson learned]

## Next Up: [Next Task Name]
### Architecture/Plan
[How it should be built — enough detail to start coding immediately]

### User Requirements
[Anything the user specifically asked for that might be non-obvious]

## System State
[Services running, ports, RAM usage, disk, anything operational]

## Files to Know
[List of key files with one-line descriptions — the map for future-you]

## How to Resume
1. Read this file (RESUME.md)
2. Read [other key file] for [context]
3. Start [specific next action]
```

**Rules for RESUME.md:**
- **Be specific, not vague.** "Built status API on port 8094" not "built an API"
- **Include the WHY.** "User wants self-growing tool ecosystem" not just "build tools"
- **Include gotchas.** "qwen3.5:0.8b needs think=false or wastes all tokens"
- **Keep it under 200 lines.** Link to other files for deep detail.
- **Write for a fresh session** — assume zero prior context

### Step 3: Update MEMORY.md

Add a summary block to MEMORY.md with:
- What was built/changed (2-3 lines max per item)
- Current project state and next steps
- Any new system facts (ports, services, model configs)

**Don't duplicate RESUME.md** — MEMORY.md is for long-term facts, RESUME.md is for active work continuation.

### Step 4: Update Daily Memory Log

Append to `memory/YYYY-MM-DD.md`:
- Timestamped entries for what happened
- Include the session-save entry itself so there's a trail

### Step 5: Update LESSONS.md (if applicable)

If you learned something reusable:
- New gotcha, workaround, or pattern → add to LESSONS.md
- Operational insight → add to relevant section

### Step 6: Commit and Backup

```bash
cd [workspace] && git add -A && git commit -m "Session save: [brief description]"
bash /home/pmello/.openclaw/tools/agents_backup_sync.sh
```

## What NOT to Save

- Raw logs or verbose command output (summarize instead)
- Secrets, tokens, passwords (never in plain files)
- Temporary debug state that won't matter next session
- Duplicate information already in other tier-1 files

## Sizing Guide

| Item | Target Size | Where |
|------|-------------|-------|
| RESUME.md | 100-200 lines | Workspace root |
| MEMORY.md update | 5-15 lines per session | Workspace root |
| Daily log entry | 3-10 lines per save | memory/YYYY-MM-DD.md |
| LESSONS.md update | 1-3 lines if applicable | Workspace root |

## Quality Checklist

Before committing, verify:
- [ ] Can a fresh session read RESUME.md and know exactly what to do next?
- [ ] Are file paths, ports, and service names specific (not "the API")?
- [ ] Are user requirements captured (not just technical state)?
- [ ] Are gotchas/lessons included so mistakes aren't repeated?
- [ ] Is everything under 200 lines (link out for detail)?
- [ ] Git committed + backup pushed?

## Sharing This Skill

This skill lives in the shared workspace. All agents should have access.
If another agent needs this, point them to:
`~/.openclaw/workspace-main/skills/context-save/SKILL.md`

Or copy it to their workspace:
```bash
cp -r ~/.openclaw/workspace-main/skills/context-save ~/.openclaw/workspace-[agent]/skills/
```
