# OPUS_RUNBOOK.md (MAIN)

Purpose: keep MAIN on `claude-opus-4-6` reliable, efficient, and context-safe.

## Fast Decision Ladder
1. Can this be answered directly without tools? If yes, do that.
2. If tools are needed, run the minimum set once.
3. If output is large, save to file + return summary.
4. If repetitive/heavy execution is needed, delegate to local/specialist agent.

## Context Discipline
- Soft warning: 80%
- Conserve mode: 85%
- Hard stop target: 95%
- If above 85%, summarize old state before continuing.

## Tool Discipline
- Use `file_preflight.sh` before opening large files.
- Avoid dumping command output directly into chat.
- Prefer single high-quality command over many tiny retries.

## Escalation Rules
Escalate from MAIN to specialist/local worker when:
- coding work is substantial,
- repeated shell retries are needed,
- task is operational/monitoring and can be scripted,
- response quality can be preserved with cheaper local execution.

## Reporting Format
- Outcome
- What changed
- What remains
- Next action (one line)
