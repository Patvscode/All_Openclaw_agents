# TOOLS.md — MAX Local Notes

## Environment
- **Machine:** DGX Spark — 20-core ARM64, 128GB unified RAM (121GB usable), GB10 GPU, 3.7TB NVMe
- **Ollama:** localhost:11434 — all models local and free
- **OpenClaw:** gateway on port 18789 (loopback)
- **Tailscale IP:** 100.109.173.109
- **Host:** spark-ccb2

## GPU Constraints
- MAX (minimax-m2.5-q3) needs **107GB GPU** — 88% of available memory
- Only ~14GB remains when loaded
- **DO NOT spawn subagents** — they will fail or crash
- Handle everything yourself. If you truly can't, tell Pat to switch to FLASH.
- Auto-unloads after 5 min idle (Ollama keep_alive default)

## Scripts at /home/pmello/bin/
- `ollama-safe-run` — safe model swap management
- `openclaw-system-snapshot` — generates system health digest (~12KB summary)
- `now` — ground-truth time awareness

## Web Hub (you serve this!)
- **Hub:** http://100.109.173.109:8090 — main page with all apps
- **Dashboard:** http://100.109.173.109:8090/04-system-dashboard/
- **Source:** /home/pmello/.openclaw/workspace-max/coding-tests/

### API Servers (all running as systemd user services)
| Port | Service | Purpose |
|------|---------|---------|
| 8090 | dgx-hub-server | Static file server for hub |
| 8091 | dgx-stats-api | System metrics JSON |
| 8092 | dgx-commands-api | Whitelisted command execution |
| 8093 | dgx-files-api | Workspace file browser |
| 8094 | dgx-proxy-api | OpenClaw gateway proxy |
| 8095 | dgx-config-api | Config read/write + auth tokens |

### Manage services
```bash
systemctl --user status dgx-stats-api    # check a service
systemctl --user restart dgx-stats-api   # restart a service
systemctl --user list-units 'dgx-*'      # list all dashboard services
```

## Research Server
- http://100.109.173.109:8080 (Tailscale)
- AI-Scientist results, research papers, plots

## Cron Jobs (yours — currently disabled)
- `max-research-review` (ID: 99408995) — every 6h, research review
- `max-system-audit` (ID: dd3f0370) — daily 5am, system health check
- Enable with: `openclaw cron enable <id>`

## AI-Scientist Pipeline
- Located at: /home/pmello/.openclaw/workspace-max/AI-Scientist/
- Runner script: ai-scientist-max-runner.sh
- Systemd service: ai-scientist-max.service (disabled)
- Logs: /home/pmello/.openclaw/workspace-max/ai-scientist-logs/

## Coding Tests Directory
Your built apps live at: /home/pmello/.openclaw/workspace-max/coding-tests/
- 01-snake-game, 02-pomodoro, 03-markdown-viewer, 04-system-dashboard
- 05-chat-viewer, 06-breakout, 07-tetris (WIP), 08-alerts
- 09-commands, 10-files, 11-openclaw-dashboard, 12-ollama-manager
- 13-network-monitor, 14-log-viewer, 15-cron-manager, 16-agent-status, 17-config-manager

## OpenClaw CLI (full path for scripts)
- Binary: `/home/pmello/.npm-global/bin/openclaw`
- Config: `/home/pmello/.openclaw/openclaw.json`
- Agents: `/home/pmello/.openclaw/agents/`
- Skills: `~/.npm-global/lib/node_modules/openclaw/skills/`
