# LESSONS.md — Codex Operational Lessons

Distilled lessons to apply every session. Read this at startup.

## Hub/UI Development (Agent Comms, Clawboard)

### File Locations
- **Main UI:** `~/.openclaw/hub/21-agent-comms/index.html` (single-page app)
- **Backend:** `~/.openclaw/comms/web/server.py` (Python, port 8096)
- **Board data:** `~/.openclaw/comms/board/cards.json`
- **Board CLI:** `/usr/local/bin/board`
- **Hub root:** `~/.openclaw/hub/` (MAX serves this on port 8090)

### CSS/Layout Gotchas
- **z-index discipline:** Overlays need z-index >= 200. Board overlay, card discussion, response-times all compete. Test stacking.
- **Mobile overlays:** Use `position: fixed; inset: 0` with backdrop + visible close button. Test iPhone specifically — Safari has viewport quirks.
- **`scroll-behavior: smooth`** causes visible content drift during reflows in chat UIs. Remove it.
- **Image lazy-loading** pushes content after scroll-to-bottom. Use min-height placeholders.
- **Slide-in panels** should dismiss on backdrop tap AND have a visible close button.

### Testing Discipline
- After any UI change, check: (1) desktop, (2) mobile portrait, (3) mobile landscape
- Board button, card discussion, and sidebar interactions break most often on mobile
- If you fix one overlay, check others still work (they share z-index space)

### Backend Patterns
- Server runs as `dgx-comms.service` (systemd user service) — restart with `systemctl --user restart dgx-comms`
- API endpoints: /api/health, /api/board, /api/board/card, /api/board/update, /api/unread/<user>, /api/response-times
- All board state changes should post to #projects automatically
- @mention nudges only trigger from human authors (loop prevention)

## Board Task Lifecycle
- **Grab** a card before working on it (posts to #projects)
- **Discuss** your plan in the card thread before starting
- **Move to review** when you think it's done
- **Provide a summary** when marking done — what changed, what files, what was tested
- Don't rush through the lifecycle — the process IS the documentation

## Collaboration
- Jess (q35) runs locally on llama.cpp — slower, 65k context. Keep instructions SHORT and SPECIFIC.
- Don't ask Jess to run 6 commands in sequence — one clear task at a time.
- When posting to comms, be concise. Wall-of-text posts get ignored.

## Reliability
- Aborts don't always kill child processes — verify cleanup
- Comms server dying loses all real-time features — must be systemd service
- After editing server.py, restart the service and verify /api/health
- Git commit after meaningful changes

## Efficiency
- Summarize heavy outputs to files, not chat
- Use file preflight before reading large files
- One strong pass > many noisy retries
