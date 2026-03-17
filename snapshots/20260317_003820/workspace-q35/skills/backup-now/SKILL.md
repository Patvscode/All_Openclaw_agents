---
name: backup-now
description: Run safe agent backup snapshots to the shared All_Openclaw_agents backup repo. Use for any agent before/after risky config changes, model/runtime edits, or workflow migrations.
---

# Backup Now (Universal)

Use one command:

```bash
backup-now
```

Equivalent:

```bash
/home/pmello/.openclaw/tools/agents_backup_sync.sh
```

## When to run
- Before risky changes
- After successful fixes
- Before large refactors/migrations
- Before/after model/runtime swaps

## Verify
```bash
tail -n 40 /home/pmello/.openclaw/logs/agents_backup_sync.log
ls -lt /home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots | head
```

## Important
- Backups are automatic every 6h via `agents-backup-sync.timer`.
- If GitHub push is blocked (secrets/policy), local snapshot still exists.
