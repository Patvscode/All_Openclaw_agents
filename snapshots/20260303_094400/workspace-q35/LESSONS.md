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