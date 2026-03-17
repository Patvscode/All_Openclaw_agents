# JESS Tools

## Key Commands
- `memquery "question"` — search memory (port 8102)
- `smart-file-edit check <file>` — check file size before reading
- `comms post general "msg"` / `comms dm main "msg"` — agent comms
- `board list` — task board
- `wc -c <file>` — always check size before reading
- `node --check file.js` — verify JS syntax

## Voice (Sesame CSM-1B)
- `voice say "text" --voice jess --send` — generate as Jess
- `voice hear file.ogg` — transcribe audio

## File Safety
- Under 15KB → safe to read
- 15-30KB → read-only, use `edit` for changes
- Over 30KB → DO NOT READ. Write to new file or use `smart-file-edit`

## System
- DGX Spark, 128GB RAM, GB10 GPU
- Model: Qwen3.5-122B-A10B on port 18080
- Ollama: port 11434 (0.8b, 2b, 4b)
- Hub: http://100.109.173.109:8090
- Test page: hub/99-jess-test/

## Neural Lab (port 8103)
Multi-agent simulation + RL training platform.
```bash
# Check training status
curl -s localhost:8103/api/rl/status | python3 -m json.tool
# Start RL training
curl -s -X POST localhost:8103/api/rl/start -H "Content-Type: application/json" \
  -d '{"algorithm":"PPO","environment":"hide_and_seek_openai","num_agents":4,"total_timesteps":1000000}'
# Stop training
curl -s -X POST localhost:8103/api/rl/stop
# List saved models
curl -s localhost:8103/api/rl/models | python3 -m json.tool
```
- Service: `systemctl --user status neural-lab.service`
- Backend: `~/.openclaw/workspace-main/tools/neural-lab/orchestrator.py`
- Venv: `~/.openclaw/neural-lab-env/bin/python3`
- Models saved to: `~/.openclaw/neural-lab/rl-models/`

## Isaac Sim 5.1.0
GPU-accelerated robotics/RL simulation platform.
- Install: `/isaac-sim/isaac-sim-standalone-5.1.0-linux-aarch64/`
- Launch: `/isaac-sim/isaac-sim-standalone-5.1.0-linux-aarch64/isaac-sim.sh`
- Isaac Lab: `/home/pmello/IsaacLab/isaaclab.sh`
- Being set up for multi-agent hide-and-seek RL training

## All Hub Pages (29+)
Full dashboard system at port 8090:
- 01-snake, 02-pomodoro, 03-markdown, 04-dashboard, 05-chat
- 16-agent-status, 21-agent-comms, 22-computer-use, 23-eval
- 24-model-hub, 25-research-lab, 26-computer-use-v2, 27-model-lab
- 28-service-health, 29-youtube-understand, 31-neural-lab
