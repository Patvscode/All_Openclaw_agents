# Failure Log — Append Only
# Review during idle heartbeats. Promote patterns to LESSONS.md.

## 2026-04-08 17:04 — Invalid config crashed gateway
Task: Disable orphan agents and heartbeats
Failure: Used `enabled: false` on agents and heartbeats — OpenClaw schema doesn't support these keys
Impact: Gateway crash-looped for several minutes. All agents down.
Root cause: Didn't check OpenClaw schema before writing config. Didn't validate with `openclaw doctor`.
Fix: Always validate config with `openclaw doctor` before restarting gateway.
Applied to: LESSONS.md ✓

## 2026-04-08 17:01 — Restarted gateway mid-session
Task: Apply config changes
Failure: Restarted gateway from inside a tool call, killing my own active response
Impact: Pat saw me go silent twice with no explanation
Root cause: Didn't think through that I run through the gateway
Fix: Finish response → save state to RESUME.md → schedule resume cron → THEN restart
Applied to: LESSONS.md ✓, gateway-restart.sh created

## 2026-03-12 — Gutted own MEMORY.md
Task: Context optimization
Failure: Trimmed MEMORY.md from 415→69 lines. Lost all operational knowledge.
Impact: ~4 weeks of degraded performance. Couldn't complete tasks, re-discovered things every session.
Root cause: Prioritized context headroom over actual knowledge. Archive existed but was never read.
Fix: MEMORY.md is the brain — never trim below functional minimum. Archive exists for overflow.
Applied to: LESSONS.md ✓, MEMORY.md restored
