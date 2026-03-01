# All OpenClaw Agents Backup

Central backup repository for OpenClaw agent state, workspace memory, skills metadata, and key runtime configuration.

## Purpose
- Keep versioned snapshots of all agent workspaces.
- Preserve recovery points for rapid rollback.
- Track what changed across agents over time.
- Provide a shared continuity layer when one agent/session fails.

## What gets backed up
- `~/.openclaw/openclaw.json`
- Agent workspace core files (`AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `MEMORY.md`, etc.)
- `memory/` logs per workspace
- Skill manifests (`SKILL.md` files)
- Key shell scripts in workspace `scripts/`
- Relevant user systemd units (gateway/voice/dashboard/Jess services)

## Schedule
Automated snapshot job runs multiple times per day via systemd timer (`agents-backup-sync.timer`).

Manual trigger:

```bash
/home/pmello/.openclaw/tools/agents_backup_sync.sh
```

## Layout
- `snapshots/<timestamp>/...` — point-in-time backups
- `meta/` — optional metadata/notes

## Notes
- Commits are created locally first, then pushed to GitHub (best effort).
- If push fails, local snapshots and commit history are still preserved.
