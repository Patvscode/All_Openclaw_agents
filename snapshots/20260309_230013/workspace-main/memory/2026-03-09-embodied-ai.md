# Embodied AI + RL Training Plan — 2026-03-09

## Pat's Vision
- OpenAI hide-and-seek style emergent behavior experiments
- RL training pipeline with automated data selection + testing
- Give Neural Lab agents a BODY in a simulated environment
- Watch them move, interact, hide, seek, learn in real-time from the UI
- Ability to swap models, adjust everything, see it all happening

## Available Options (ranked by feasibility on DGX Spark)

### 1. NVIDIA Isaac Sim + Isaac Lab ⭐ BEST OPTION
- **Official DGX Spark support** — NVIDIA has a build guide at build.nvidia.com/spark/isaac
- GPU-accelerated physics simulation (faster than real-time)
- Pre-built RL environments (locomotion, manipulation, navigation)
- Can create custom multi-agent environments
- 30-min install, ~50GB disk space needed
- Build from source on ARM64/GB10
- **Already has RL training pipelines built in**

### 2. PettingZoo + Gymnasium (lightweight alternative)
- Python multi-agent RL framework
- Lightweight, runs on CPU
- Built-in environments: pursuit-evasion, cooperative, competitive
- Easy to create custom grid/continuous environments
- Could build hide-and-seek as a custom PettingZoo env
- Pairs well with: CleanRL, Stable Baselines3, RLlib

### 3. Custom 2D Simulation (our own, in-browser)
- Build a simple 2D physics world in the Neural Lab UI
- Agents have position, vision cone, movement, communication
- Lightweight, no extra dependencies
- Full control, directly integrated with Neural Lab
- Visualize in browser via Canvas/WebGL
- Good for LLM-as-policy experiments (no traditional RL needed)

## Recommended Approach: Hybrid
1. **Immediate**: Custom 2D simulation in Neural Lab UI (for LLM agents)
2. **This week**: Install Isaac Lab on Spark (for proper RL training)
3. **Connect**: Isaac Lab environments → Neural Lab agents (brain = policy)

## Training Pipeline Requirements
- Automated data selection ("train on data you think is useful")
- Multiple RL algorithms available (PPO, SAC, DQN, etc.)
- Evaluation after training (automated benchmarks)
- Save/load trained models
- Visualize training curves in the UI
- Support for: RL, RLHF, DPO, supervised fine-tuning
