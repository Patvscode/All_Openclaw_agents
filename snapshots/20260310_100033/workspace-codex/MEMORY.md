# MEMORY.md

Long-term memory for CODEX workspace.

## User
- Patrick Mello (Pat)
- Priorities: reliability first, efficiency second, local-first where quality is sufficient
- Keep usage sustainable and preserve budget buffer

## System Architecture
- **Host:** DGX Spark (spark-ccb2), ARM64, 128GB unified RAM, GB10 GPU
- **Tailscale:** 100.109.173.109
- **Hub:** http://100.109.173.109:8090 (served by MAX agent)
- **Comms server:** port 8096, systemd: dgx-comms.service
- **Jess (q35):** llama.cpp on port 18080, Qwen3.5-35B-A3B, 65k context

## Agent Topology
| Agent | Model | Role |
|-------|-------|------|
| main | claude-opus-4-6 | Orchestrator, knowledge owner |
| codex | GPT-5.3 | Coding, UI, infrastructure |
| q35/Jess | Qwen3.5-35B local | Local-first assistant |
| max | (hub server) | Serves Clawboard web UI |

## What I Built (key items)
- Automated backup pipeline (agents_backup_sync.sh, systemd timer)
- Clawboard agent console (hub/19-agent-console)
- Jess runtime: watchdog, memory manager, runtime guard
- Comms server reliability: dgx-comms + max-web-gallery systemd services, /api/health
- Board UI fixes: mobile overlay, card discussion, grab/move controls

## Key Lessons
- Read LESSONS.md every session — it has UI patterns, testing discipline, and gotchas
- Jess needs SHORT instructions (65k context, slower model)
- Board lifecycle is documentation — don't skip steps
- Test UI on mobile after every change
- Git commit after meaningful work

## GitHub Backup Status
- Push blocked by secret scanning (secrets in snapshot history)
- Needs sanitization workflow before reliable remote push
