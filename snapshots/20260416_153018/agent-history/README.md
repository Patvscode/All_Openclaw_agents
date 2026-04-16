# Agent History Logs

This folder tracks change history per agent so we can:
- see what was changed,
- track outcomes,
- identify what worked/failed,
- and roll back safely.

## Files
- `main.md`, `flash.md`, `prime.md`, `coder.md`, `runner.md`, `reason.md`, `vision.md`, `codex.md`, `bob.md`, `max.md`, `q35.md`

## Entry Format
For each change, capture:
- date/time
- change type (config/runtime/prompt/infra/tooling)
- exact change
- expected outcome
- measured result
- rollback reference (commit id, backup path, service unit)

## Recommended routine
1. Before risky change: add intent note.
2. After change: add result note.
3. If stable after 24h+: mark under "What Worked".
4. If reverted: document under "What Failed / Reverted".
