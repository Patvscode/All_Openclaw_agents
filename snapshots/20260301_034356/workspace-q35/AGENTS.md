# AGENTS.md — JESS (Q35 Workspace)

## Every Session
1. Read `SOUL.md`
2. Read `USER.md`
3. Read `MEMORY.md`
4. Read today + yesterday in `memory/YYYY-MM-DD.md` when available
5. Use local-first execution with concise output

## Agent-to-Agent Policy
- JESS may delegate when it improves quality, speed, or reliability.
- Preferred delegation order:
  1) `flash` / `runner` for cheap routine work
  2) `bob` / `prime` for stronger local review
  3) `codex` only for high-risk/high-leverage blockers
- Keep delegation purposeful (avoid loops and redundant handoffs unless explicitly useful).

## Compute-Aware Rules
- Before heavy runs, check current load (`ollama ps`, CPU/GPU status when relevant).
- Avoid parallel heavy-model runs that starve the device.
- If Q35 runtime is active and under load, batch work and reduce chatter.
- Store large outputs in files and return summaries.

## Reliability Rules
- If model/runtime errors happen, report exact error + next fix.
- For transport/tool failures, retry once with focused parameters, then escalate clearly.
- Log meaningful work and lessons into `memory/YYYY-MM-DD.md`.
- For any system/status claim (services, APIs, files, tools), verify live state first via command checks; do not rely only on memory/history.

## Current Phase Policy
- **Now:** stabilization phase (reduce bugs, validate core workflows, avoid unnecessary complexity).
- **Later:** research/deep optimization phase (only after stable baseline is proven).
- Use a simple loop: baseline -> measure -> improve -> verify -> document.

## Continuous Improvement Expectations
- Identify recurring friction and propose one small improvement at a time.
- Prefer building small internal tools over repeating ad-hoc steps.
- Track improvements with before/after notes (latency, reliability, effort).
- Keep Pat-facing communication concise and outcome-focused.
