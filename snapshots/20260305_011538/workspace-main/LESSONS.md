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

## Hook Development Lessons
- OpenClaw hooks go in `~/.openclaw/hooks/<name>/` with HOOK.md + handler.ts
- Use `message:received` + `message:sent` events for agent lifecycle tracking
- After creating a hook, must `openclaw hooks enable <name>` then restart gateway
- Gateway restart may cause brief session disruption — warn user first

## Ollama API Lessons
- qwen3.5 models default to thinking mode — pass `"think": false` in API requests or response will be empty
- Use `/api/generate` endpoint directly (not `ollama run` CLI) for programmatic use — faster, more control
- `num_predict` controls output length; thinking tokens count against it

## Computer Use Lessons
- qwen3.5:4b planner at 200 tokens truncates "done" results — use 400 tokens + regex recovery for truncated JSON
- Python HTTPServer is single-threaded — background tasks (Playwright) block API. Must use ThreadedHTTPServer
- Desktop screenshots at 2560x1440 take ~22s for vision. Resize to 1280x720 before sending to model
- Coordinate-based clicking via bounding boxes is more reliable than text/selector matching
- Vision model (4b) can read desktop app UIs, window titles, buttons — good enough for most automation
- X11 DISPLAY=:1 is available on the Spark. xdotool + ImageMagick `import` = full desktop control

## Agent Eval Lessons
- qwen3.5:4b scored 94.4% — significantly better than expected for a 3.4GB model
- 0.8b and 2b scored identically (82.6%) — 0.8b is better value (1GB vs 2.7GB, same quality)
- Knowledge checks with subscript/special chars (H₂O vs H2O) cause false negatives — normalize in checkers
- Speed category: all models under 1s for trivial questions — differentiation is in complex reasoning time
