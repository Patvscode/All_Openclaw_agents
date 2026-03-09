---
name: jess-ops
description: Operate and troubleshoot Jess quickly. Use when checking Jess health, measuring response latency, switching fast-chat vs deep-chat behavior, validating runtime/watchdog status, or running smoke tests for chat/tool/delegation.
---

## Quick commands
- Health: `scripts/jess_status.sh`
- Smoke test: `scripts/jess_smoke.sh`
- Latency test: `scripts/jess_latency.sh`
- Fast chat mode: `scripts/jess_mode_fast.sh`
- Deep chat mode: `scripts/jess_mode_deep.sh`

## Rules
- Prefer fast mode for Telegram chat responsiveness.
- Use deep mode only for long-context tasks.
- Keep changes reversible; scripts print what they changed.
- Log notable findings to `memory/YYYY-MM-DD.md`.
- For status reports, run `scripts/jess_status.sh` (and relevant targeted checks) before claiming anything as current.
