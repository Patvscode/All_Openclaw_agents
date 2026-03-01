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
