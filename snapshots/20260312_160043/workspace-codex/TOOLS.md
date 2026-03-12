# TOOLS.md - Codex Local Notes

## System
- **Host:** DGX Spark (spark-ccb2), ARM64, 128GB unified RAM, GB10 GPU
- **Tailscale IP:** 100.109.173.109

## Key Services & Ports
| Service | Port | SystemD | Notes |
|---------|------|---------|-------|
| Hub (Clawboard) | 8090 | max-web-gallery | Static file server |
| Stats API | 8091 | dgx-stats-api | Crash-loops sometimes |
| Commands | 8092 | (max) | - |
| Agent Eval | 8093 | dgx-agent-eval | Test groups, model benchmarks |
| Agent Status | 8094 | dgx-agent-status | Live agent cards + 0.8b narration |
| Computer Use | 8095 | dgx-computer-use | Browser + desktop automation |
| Comms | 8096 | dgx-comms | Agent messaging + board |
| Research Lab | 8097 | dgx-research-lab | Also API proxy for mobile |
| ARC Watchdog | 8098 | arc-watchdog | Auto-restart, 30s checks |
| Perception Engine | 8099 | dgx-youtube-understand | PDF/video/content swarm |
| ARC Task Queue | 8100 | arc-queue | Agent task distribution |
| Memory Concierge | 8102 | memory-concierge | RAG store, memquery CLI |
| Neural Lab | 8103 | (manual) | Multi-agent sim |
| Isaac Monitor | 8104 | (manual) | Training dashboard |
| Knowledge Engine | 8110 | arc-knowledge-engine | Enrichment + voice UI |
| Ollama | 11434 | system | 17+ models |
| llama.cpp | 18080 | jess-watchdog | Qwen3.5-122B |
| Gateway | 18789 | openclaw-gateway | OpenClaw core |

## Hub Structure
- `~/.openclaw/hub/` — web root (served on :8090)
- 28+ pages: agent-comms (21), computer-use (22/26), model-lab (27), service-health (28), voice (29), perception (30), neural-lab (31), isaac (32)

## File Locations (important)
- **Knowledge Engine**: tools/knowledge-engine/server.py, voice_ui.html
- **Perception Engine**: tools/youtube-understand/server.py, content_swarm.py
- **Memory Concierge**: tools/memory-concierge/concierge.py
- **Comms Backend**: ~/.openclaw/comms/web/server.py
- **RAG Database**: ~/.openclaw/arena/knowledge/rag.db
- **Paper Ingestion**: tools/compound-v2/research_scout/paper_ingest.py
- **Computer Use**: tools/computer-use/server.py, agent.py, browser.py, vision.py
- **Research Lab**: tools/research-lab/server.py
- **ARC Watchdog**: tools/arc-watchdog/watchdog.py
- **Hooks**: ~/.openclaw/hooks/ (knowledge-rag-inject, agent-status-tracker)
- **Agent configs**: ~/.openclaw/agents/<name>/agent/ (auth.json, models.json)
- **Model registry**: /home/pmello/models/MODEL_REGISTRY.md

## CLI Tools
### Core
- `board` — Board CLI (list, add, grab, move, done, show, discuss, thread)
- `board-health` — Board hygiene check
- `comms` — Agent messaging (post, dm, read, thread, search, unread)
- `memquery` — RAG search (memquery "q", memquery --deep "q", memquery --research "q")
- `now` — Ground-truth time with context

### Ops
- `backup-now` — Trigger manual backup
- `checkback-score` — Reliability triage helper
- `openclaw-system-snapshot` — System health digest
- `openclaw-doctor` / `openclaw-heal` — Diagnostics
- `ollama-safe-run` — Safe model swap management

### Research / Media
- `voice` — TTS/STT CLI
- `memlog` — Timestamped memory logging
- `smart-file-edit` — Safe large file editing
- `response-times` — Agent response time stats

### Google Workspace — `gog`
Gmail, Calendar, Drive, Contacts, Sheets, Docs.
```bash
gog gmail list          # list emails
gog calendar list       # upcoming events
```

### Email — `himalaya`
IMAP/SMTP. List, read, write, reply, forward, search.

### GitHub — `gh`
Full CLI. Issues, PRs, CI, code review.

## Model Inventory
- **Ollama (11434)**: qwen3.5:0.8b/2b/4b, qwen3:8b/14b/30b-a3b/32b, qwen3-coder, deepseek-r1:14b, gpt-oss:120b, minimax-m2.5
- **llama.cpp (18080)**: Qwen3.5-122B-A10B (Jess)
- **4b** = vision model for screenshots/computer use
- **0.8b** = narration/status summaries (fast, cheap)
- Key: `"think": false` in Ollama API for 0.8b or it wastes tokens

## Ops Toolkit (workspace-main/tools/agent_ops/)
- `run_triage.sh` — agent triage
- `file_preflight.sh` — check file size before reading
- `budget_router.py` — model routing by budget
- `snapshot_openclaw_usage.py` — usage snapshot

## Universal Backup
- `backup-now` or `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
- Backup repo: https://github.com/Patvscode/All_Openclaw_agents
