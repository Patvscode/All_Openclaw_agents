# TOOLS.md - Local Notes

## System
- **Host:** DGX Spark (spark-ccb2), ARM64, 128GB unified RAM, GB10 GPU
- **Ollama:** localhost:11434, 17 models installed
- **Tailscale IP:** 100.109.173.109

## CLI Tools Available

### Google Workspace — `gog` (v0.9.0)
Gmail, Calendar, Drive, Contacts, Sheets, Docs, Slides, Tasks.
```bash
gog gmail list          # list emails
gog calendar list       # upcoming events
gog contacts list       # contacts
gog drive list          # drive files
```

### Email — `himalaya`
IMAP/SMTP email client. List, read, write, reply, forward, search.
```bash
himalaya list           # list inbox
himalaya read <id>      # read message
```

### GitHub — `gh`
Full GitHub CLI. Issues, PRs, CI, code review.

### ChatGPT Bridge — `chatgpt-bridge`
Free GPT-4 access via Pat's Plus subscription. Headless browser automation.
```bash
chatgpt-bridge ask "question"
chatgpt-bridge code "coding task"
chatgpt-bridge status
```
⚠️ No memory between calls. Don't send private data.

### Video Analysis — `video-understand`
Extracts frames + runs vision model analysis on video.

### Time — `now`
Ground-truth time with context (period, urgency, uptime).

### Media/Creative
- `gifgrep` — search GIF providers, download, extract stills
- `songsee` — audio spectrograms and feature visualizations
- `nano-pdf` — edit PDFs with natural language
- `blogwatcher` — monitor blogs/RSS feeds

### MCP — `mcporter`
List, configure, auth, and call MCP servers/tools.

### Model Management
- `ollama-safe-run` — safe model swap management (~/bin/)
- `openclaw-system-snapshot` — system health digest (~/bin/)

## Custom Scripts (~/bin/)
- `auto-improve` — self-improvement cycle
- `codex-agent`, `codex-evolve` — codex automation
- `openclaw-ai-scientist-status` — AI scientist pipeline status
- `openclaw-cron-reset-sessions` — session cleanup
- `openclaw-cron-semantic-audit` — semantic audit
- `openclaw-doctor`, `openclaw-heal` — diagnostics
- `openclaw-memory-hybrid-search` — memory search
- `openclaw-morning-briefing` — morning briefing generator
- `openclaw-self-improve-cycle` — self-improvement
- `research-server` — research web server

## Ops Toolkit (tools/agent_ops/)
- `run_triage.sh` — agent triage
- `file_preflight.sh` — check file size before reading
- `budget_router.py` — model routing by budget
- `snapshot_openclaw_usage.py` — usage snapshot
- `usage_daily_summary.py` — daily usage report

## Skills I Have (via OpenClaw)
blogwatcher, blucli, coding-agent, gh-issues, gifgrep, github, gog, healthcheck, himalaya, mcporter, nano-pdf, openai-whisper, openai-whisper-api, oracle, session-logs, skill-creator, songsee, summarize, tmux, video-frames, wacli, weather, web-publish, agent-ops-orchestrator

## Skills Available but Not Wired to Me
These exist in the OpenClaw skills directory but aren't in my available_skills:
1password, apple-notes, apple-reminders, bear-notes, bluebubbles, camsnap, canvas, clawhub, discord, eightctl, gemini, goplaces, imsg, model-usage, nano-banana-pro, notion, obsidian, openai-image-gen, openhue, ordercli, peekaboo, sag (ElevenLabs TTS), sherpa-onnx-tts, slack, sonoscli, spotify-player, things-mac, trello, voice-call, web-serve, xurl

Notable ones that could be useful:
- **sag** — ElevenLabs TTS for voice messages/storytelling
- **openai-image-gen** — image generation
- **model-usage** — usage tracking
- **web-serve** — serve files locally
- **clawhub** — skill marketplace

## Sesame Voice (codex workspace)
Local voice generation via Sesame/Dia API.
```bash
~/.openclaw/workspace-codex/skills/sesame-voice-send/tools/sesame_generate.sh "text"
```

## Web Hub (MAX serves this)
- Hub: http://100.109.173.109:8090
- Dashboard: http://100.109.173.109:8090/04-system-dashboard/


## Universal Backup
- Run backup anytime: `backup-now`
- Full script: `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
