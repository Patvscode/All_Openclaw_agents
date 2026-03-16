# Neural Lab Knowledge Transfer — 2026-03-10
Source: Main agent, transferred by Pat's request.

## What Is Neural Lab?
A multi-agent simulation + RL training platform built for the DGX Spark.
- **Hub page**: http://100.109.173.109:8090/31-neural-lab/
- **API**: port 8103 (neural-lab.service, user-level systemd)
- **Backend**: `~/.openclaw/workspace-main/tools/neural-lab/orchestrator.py` (Flask + SocketIO)
- **Simulation**: `~/.openclaw/workspace-main/tools/neural-lab/simulation.py` (pymunk physics)
- **RL Env**: `~/.openclaw/workspace-main/tools/neural-lab/rl_env.py` (Gymnasium wrapper)
- **Frontend**: `~/.openclaw/hub/31-neural-lab/index.html` (5200+ lines, Three.js 3D)
- **Python venv**: `~/.openclaw/neural-lab-env/` (stable-baselines3, pymunk, torch)

## Core Architecture
1. **SimulationEngine** (pymunk 2D physics): agents, walls, objects (boxes/ramps/food/flags/tools)
2. **Vision system**: raycast line-of-sight, configurable range + angle
3. **Actions**: 14 discrete (noop, move, turn, sprint, grab, push, place, use, signal, lock, unlock, look_around)
4. **RL Training**: PPO/A2C/DQN via stable-baselines3, background thread
5. **Environments**: open_field, hide_and_seek, hide_and_seek_openai, maze, foraging
6. **3D Viewport**: Three.js rendering of the 2D sim, first-person mode, AI world builder

## OpenAI Hide & Seek Setup (what we built)
Modeled after OpenAI's "Emergent Tool Use" paper (arxiv 1909.07528):
- **Environment**: `hide_and_seek_openai` — 8 walls (rooms+corridors), 6 boxes, 2 ramps, 1 tool
- **Teams**: 2 hiders (blue) vs 2 seekers (red)
- **Reward**: Joint zero-sum (+1/-1 per team per tick based on ANY hider seen by ANY seeker)
- **Preparation phase**: First 40% of episode, seekers are frozen
- **Vision**: 800 range (covers whole arena), 180° arc, blocked by walls only
- **Self-play**: PPO alternates training hiders/seekers in 10 cycles
- **PPO hyperparams**: batch=2048, epochs=10, γ=0.998, lr=3e-4, ent=0.01

## API Endpoints (port 8103)
- `POST /api/rl/start` — start background RL training
- `POST /api/rl/start_visual` — start RL training with viewport rendering
- `POST /api/rl/stop` — stop training (auto-saves model)
- `GET /api/rl/status` — training progress (episode, timesteps, rewards, log)
- `POST /api/rl/continue` — continue from saved model
- `GET /api/rl/models` — list saved models
- `GET /api/sim/state` — current simulation state (also returns RL state during training)
- `POST /api/sim/start` — start viewport simulation
- `POST /api/sim/stop` — stop viewport simulation
- `POST /api/sim/newgame` — full reset (clear agents, world, objects)
- `POST /api/sim/world/save` / `load` / `delete` / `list`
- `POST /api/sim/world/generate` — AI-generated world from prompt
- `GET /api/sim/environments` — list available environments
- `POST /api/sim/agents/add` / `remove` — manage agents

## Saved Models
Location: `~/.openclaw/neural-lab/rl-models/`
- PPO checkpoints from 27K episodes (6.5M steps) of hide-and-seek training
- JSON metadata alongside each .zip model file

## PIVOT: Isaac Sim + Isaac Lab
Pat directed a pivot to NVIDIA Isaac Sim for proper GPU-accelerated RL training.
- **Isaac Sim 5.1.0**: `/isaac-sim/isaac-sim-standalone-5.1.0-linux-aarch64/`
- **Isaac Lab**: `/home/pmello/IsaacLab/`
- Goal: Same hide-and-seek experiment but with PhysX GPU physics and real-time rendering
- The viewport MUST show what the RL model is actually doing (unified sim + training)

## Key Lessons Learned
1. Always sync sim.max_ticks with RL env max_steps when using prep_fraction
2. Don't show a fake viewport sim separate from training — users want truth
3. Joint zero-sum reward creates arms race dynamics (OpenAI's key insight)
4. Preparation phase is critical — gives hiders time to use tools before seekers activate
5. Vision range and angle dramatically affect training dynamics
6. Self-play alternation (train hiders, then seekers) creates emergent strategies
