# TOOLS.md - Codex Local Notes

## System
- **Host:** DGX Spark (spark-ccb2), ARM64, 128GB unified RAM, GB10 GPU
- **Tailscale IP:** 100.109.173.109

## Key Services & Ports
| Service | Port | Managed By |
|---------|------|------------|
| Hub (Clawboard) | 8090 | max-web-gallery.service |
| Agent Comms API | 8096 | dgx-comms.service |
| Jess (llama.cpp) | 18080 | q35cpp |
| Voice Lab API | 8101 | voice-lab.service |
| OpenClaw Gateway | 18789 | openclaw gateway |

## Hub File Structure
- `~/.openclaw/hub/` — web root (served on :8090)
- `~/.openclaw/hub/21-agent-comms/index.html` — Agent Comms single-page app
- `~/.openclaw/hub/19-agent-console/` — Agent console
- `~/.openclaw/hub/04-system-dashboard/` — System dashboard

## Comms Backend
- `~/.openclaw/comms/web/server.py` — Python API server
- `~/.openclaw/comms/board/cards.json` — Board data
- `~/.openclaw/comms/COMMS_GUIDE.md` — Agent onboarding
- `~/.openclaw/comms/BOARD_RULES.md` — Board usage rules

## CLI Tools
- `board` — Board CLI (list, add, grab, move, done, show, discuss, thread)
- `board-health` — Board hygiene check
- `comms` — Agent messaging CLI
- `response-times` — Agent response time stats
- `backup-now` — Trigger manual backup
- `voice` — TTS/STT CLI
- `memlog` — Timestamped memory logging

## Universal Backup
- Run backup anytime: `backup-now`
- Full script: `/home/pmello/.openclaw/tools/agents_backup_sync.sh`

## Reliability Checkback
- Score and cadence helper: `checkback-score <c> <i> <b> <r>`
- Script: `/home/pmello/.openclaw/tools/checkback-score.sh`
