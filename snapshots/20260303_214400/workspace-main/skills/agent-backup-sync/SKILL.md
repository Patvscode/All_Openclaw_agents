---
name: agent-backup-sync
description: Back up all OpenClaw agents' critical files and configs to the shared GitHub repo (All_Openclaw_agents) multiple times per day. Use when verifying backups, forcing a manual snapshot, checking backup logs, or restoring confidence after major config/runtime changes.
---

## Commands
- Manual backup now:
  - `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
- Check timer:
  - `systemctl --user status agents-backup-sync.timer --no-pager`
- Check latest log:
  - `tail -n 80 /home/pmello/.openclaw/logs/agents_backup_sync.log`
- Check snapshots repo:
  - `ls -lt /home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots | head`

## Notes
- Runs automatically every 6 hours via systemd timer.
- Captures workspace docs/memory/skills metadata, key scripts, openclaw.json, and relevant user systemd units.
- Commits and pushes best-effort; if push fails, local snapshot + commit still persist.
