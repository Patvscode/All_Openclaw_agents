# LESSONS.md — Codex Operational Lessons

Distilled lessons to apply every session. Read this at startup.

## Knowledge-First Rule (CRITICAL)
- ALWAYS check internal knowledge before web search
- `memquery "topic"` → fast RAG search (100ms, 20K+ chunks, 122+ papers)
- `memquery --deep "question"` → parallel 0.8b synthesis
- The `knowledge-rag-inject` hook auto-injects relevant RAG into your context
- Web search is LAST RESORT, not default

## Hub/UI Development

### File Locations
- **Hub root:** `~/.openclaw/hub/` (MAX serves on port 8090)
- **Comms UI:** hub/21-agent-comms/index.html
- **Backend:** ~/.openclaw/comms/web/server.py (Python, port 8096)
- **Board data:** ~/.openclaw/comms/board/cards.json

### CSS/Layout Gotchas
- **z-index discipline:** Overlays need >= 200. Board overlay, card discussion, response-times compete.
- **Mobile overlays:** `position: fixed; inset: 0` with backdrop + visible close button. Test iPhone Safari.
- **`scroll-behavior: smooth`** causes drift in chat UIs. Remove it.
- **Image lazy-loading** pushes content after scroll-to-bottom. Use min-height placeholders.
- Python 3.14 has no `cgi` module — don't import it.

### Testing Discipline
- After any UI change: desktop → mobile portrait → mobile landscape
- Board button, card discussion, sidebar break most on mobile
- If you fix one overlay, check others still work (shared z-index space)

### Backend Patterns
- Services are systemd user services: `systemctl --user restart <service>`
- After editing server.py, restart service and verify /api/health
- @mention nudges only from human authors (loop prevention)

## Service Architecture Lessons

### Concurrency
- Ollama can only serve one model inference at a time effectively
- Perception Engine uses semaphore to limit concurrent PDF processing to 1
- Don't spawn parallel workers that all call Ollama — they'll just queue

### Model Management
- `ollama-safe-run` for model swaps (handles port conflicts)
- systemd `Restart=on-failure` + timer = persistent resurrection — disable BOTH to stop
- Split GGUFs: point at shard 1, llama.cpp finds the rest
- A supervisor (not a model) must manage swaps — models can't restart themselves

### Reliability
- Aborts don't always kill child processes — verify cleanup
- ARC Watchdog monitors all services every 30s, auto-restarts up to 3x
- Stats API (8091) crash-loops sometimes (WorkingDirectory config issue)
- When something breaks: check `journalctl --user -u <service>` first

## Board Task Lifecycle
- **Grab** a card before working
- **Discuss** your plan in thread before starting
- **Move to review** when done
- **Provide summary** — what changed, what files, what tested
- Process IS documentation — don't skip steps

## Collaboration
- Jess (q35): 65k context, slower model. Keep instructions SHORT and SPECIFIC.
- Don't ask Jess to run 6 commands in sequence — one clear task at a time.
- When posting to comms, be concise. Wall-of-text posts get ignored.
- Check SHARED_CONTEXT.md before shared system work to avoid collisions.

## Efficiency / Cost
- GPT-5.3 Codex has free weekly credits — still be efficient
- Summarize heavy outputs to files, not chat
- Use file preflight before reading large files
- One strong pass > many noisy retries
- Long tool dumps bloat context — summarize and persist

## Git
- Commit after meaningful changes
- GitHub push may be blocked by secret scanning — check before assuming push worked
- Backup via `backup-now` works independently of git push

## Hooks System
- Hooks live in ~/.openclaw/hooks/<name>/handler.ts + HOOK.md
- Events: before_prompt_build, message_received, message_sending, message_sent, before_tool_call, etc.
- `before_prompt_build` can return `prependContext` to inject into agent context
- `knowledge-rag-inject` hook auto-queries RAG on every inbound message
- To disable a hook: move it out of hooks/ directory (renaming isn't enough)
