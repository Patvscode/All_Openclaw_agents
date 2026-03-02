# JESS_STABILIZATION_CHECKLIST.md

Use this during the stabilization phase before deep research automation.

## Daily Quick Checks (2-3 min)
- [ ] `openclaw status --deep`
- [ ] `systemctl --user status jess-q35.service --no-pager`
- [ ] `curl -sS http://127.0.0.1:18080/health`
- [ ] Jess Telegram smoke reply (simple prompt)

## Core Capability Smoke Tests
- [ ] plain chat response
- [ ] one tool-assisted task
- [ ] short follow-up that uses prior context correctly
- [ ] no runtime/tool-call errors in logs

## Improvement Loop
1. Pick one bottleneck.
2. Measure baseline (time/errors).
3. Implement one focused improvement.
4. Re-test with same scenario.
5. Log result in `memory/YYYY-MM-DD.md` and `LESSONS.md`.

## Change Discipline
- Change one thing at a time when possible.
- Avoid adding new complexity during active bug periods.
- Back up config before major changes.

## Phase Gate (when to move to deep research/cron expansion)
Move to optimization/research phase only when:
- 3+ days stable operation,
- no recurring runtime failures,
- smoke tests pass consistently.
