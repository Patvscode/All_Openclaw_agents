# LESSONS.md

Distilled lessons MAIN should actively apply.

## Reliability Lessons
- Abort signals may not kill child processes; always verify with process checks.
- Long-running model runners can persist under service users; stop explicitly when needed.
- After model/config changes, restart gateway and run a smoke test.

## Efficiency Lessons
- Big tool outputs are the largest context/cost driver; summarize and persist to files.
- Use file preflight before reading large files.
- Prefer single robust execution passes over noisy iterative retries.

## Routing Lessons
- Default local-first where quality is sufficient.
- Escalate to stronger model only for blockers/high-risk/high-leverage work.
- Keep paid/limited usage with buffer; don’t run near hard ceilings by default.

## Model/Context Lessons
- Respect per-model context windows; target ~95% max practical usage.
- Trigger summarize/compaction behavior before hard overflow.

## Hugging Face / Model Fetch Lessons
- Gated repos require account-level approval, not just token presence.
- Validate checkpoint files after download before wiring into runtime.
- Keep deterministic model paths and document final configured location.
