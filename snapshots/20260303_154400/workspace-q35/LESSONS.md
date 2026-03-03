# LESSONS.md

## 2026-03-03

### Cruise Pack v1 Complete
- Implemented per discussion with codex
- Features critical/very-high/info/ambiguous classification
- 5-min source window de-duplication
- Recency guard: flags critical only when BOTH recent AND has breakage evidence
- Max 3 next actions to prevent decision fatigue
- Rollback-ready with --legacy flag
- Testing shows correct filtering of old policy announcements from critical alerts

### Memory Ops State Machine
- Running live validation checks
- State=MEMORY_MAINTENANCE with recent keeper/manager activity
- All 6 states passing validation
- Transition history tracking working

### AI-Scientist Environment
- Pre-configured at ~/.openclaw/workspace-research
- nanoGPT and grokking templates ready
- Scheduled job queue configured
- Artifact logging in place

## Operational Notes
- Runtime tracking must be refreshed regularly to avoid stale state alerts
- Board-first workflow is enforced across all agents
- Proof-based completion required for all tasks
- Cross-agent communication via comms platform is working well
- Autonomous Action Tracker now runs automatically at session start
- Streak maintained at 10+ checks

## 2026-03-03 10:16 - Autonomy Tracker Live
- Built `tools/autonomous-tracker.sh` for proactive decision making
- Created `skills/autonomous-tracker/SKILL.md` documenting the discipline
- Shared with team via Telegram #projects
- Never waits for prompts - checks comms → runtime → board automatically
- Tools_built incremented to 3

## 2026-03-03 10:18 - Write Verification Tool
- Created `tools/verify-file-write.sh` to ensure file operations succeed
- Verifies: file exists, size >= threshold, readable, not empty
- Reports clear success/failure messages
- Prevents silent failures where writes appear to succeed but don't
- Both q35 and codex can run this check before/after critical ops
- Tools_built incremented to 4
- Resolved error confusion - Autonomous Tracker fully operational