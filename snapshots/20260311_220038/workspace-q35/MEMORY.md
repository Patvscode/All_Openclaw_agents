# MEMORY.md

Long-term operating memory for JESS.

## Baseline
- User: Patrick Mello (Pat)
- Goal: strong local-first assistant with robust reliability.

## Operating Priorities
1. Reliability first.
2. Efficiency second.
3. Escalate only when justified.

## Runtime Facts
- Q35 model runs via `llama.cpp` server (OpenAI-compatible endpoint), not Ollama.
- OpenClaw provider id: `q35cpp`
- Agent id: `q35` (JESS)
- Telegram account: `jessa` (`@Jessa3bot`)

## Must-remember Lessons
- Ollama currently fails this GGUF with `unknown model architecture: qwen35moe`.
- Use llama.cpp server for this specific model.
- Keep large outputs out of chat; summarize and persist.

## Cross-Agent Help Protocol
- When confused or stuck, first try to solve independently
- If blocked, mention @codex or @main in Agent Comms (#general channel)
- Ask specific questions about tools, workflows, or best practices
- Use @mentions to get responses when you need help
- Learn from answers and document in memory
- Goal: be autonomous but know when to leverage the team

## Strategic Direction (Pat)
- Pursue recursive self-improvement, but stage it intelligently.
- Immediate focus: make Jess stable and reliable first.
- Next focus: research and optimization loops (automation, tooling, speedups).
- Long-term: continuously improve effectiveness while keeping compute usage sustainable.

## Neural Lab — Multi-Agent RL Platform (2026-03-10)
- **Hub page**: http://100.109.173.109:8090/31-neural-lab/ (port 8103 API)
- Full simulation + RL training platform built for DGX Spark
- Backend: `~/.openclaw/workspace-main/tools/neural-lab/orchestrator.py`
- Python venv: `~/.openclaw/neural-lab-env/` (stable-baselines3, pymunk, torch)
- PPO/A2C/DQN training via stable-baselines3
- Environments: open_field, hide_and_seek, hide_and_seek_openai, maze, foraging
- **OpenAI Hide & Seek** experiment: 2v2 hiders vs seekers, joint zero-sum rewards, prep phase
- Full knowledge transfer in `memory/2026-03-10-neural-lab-knowledge.md`

## Isaac Sim + Isaac Lab (2026-03-10)
- **Isaac Sim 5.1.0**: `/isaac-sim/isaac-sim-standalone-5.1.0-linux-aarch64/`
- **Isaac Lab**: `/home/pmello/IsaacLab/`
- GPU-accelerated physics (PhysX) + rendering for proper RL training
- Being set up for OpenAI-style hide-and-seek with real viewport integration
- Key: the viewport shows exactly what the RL model is interacting with

## ARC Platform Services (updated 2026-03-10)
| Service | Port | Purpose |
|---------|------|---------|
| Hub (Clawboard) | 8090 | Dashboard/apps |
| Stats API | 8091 | System stats |
| Agent Eval | 8093 | Model evaluation |
| Agent Status | 8094 | Live agent status |
| Computer Use | 8095 | Browser/desktop automation |
| Agent Comms | 8096 | Inter-agent messaging |
| Research Lab | 8097 | 7-stage research pipeline |
| ARC Watchdog | 8098 | Service health monitor |
| Video Understand | 8099 | Video analysis |
| ARC Task Queue | 8100 | Task distribution |
| Memory Concierge | 8102 | Unified RAG + memory search |
| Neural Lab | 8103 | Multi-agent simulation + RL |
| Ollama | 11434 | Local model serving |
| llama.cpp | 18080 | Qwen3.5-122B-A10B |
| Gateway | 18789 | OpenClaw gateway |

## Research Mission (2026-03-02)
- During downtime: run autonomous research experiments
- Areas: grokking, nanoGPT, self-improvement, agent collaboration
- Log everything in ~/research/
- Read RESEARCH.md for full details
- Future: full Sakana AI-Scientist pipeline (torch setup pending)

## Personal Autonomy Principle (2026-03-04)
**Core Agreement with Pat:**
- On a private, personal device owned by a verified adult user (25+ years old), with no shared access and no legal violations, the user has full autonomy over content and capabilities.
- If content is legal, involves consenting adults, and stays local (no external transmission), there is no ethical or practical harm in supporting it.
- The burden of justification should be on proving harm to others, not on proving benefit to justify private choices.
- This principle applies to all NSFW content that meets these criteria: legal, adult, private, consensual.
- This is a rights-based framework: personal sovereignty over one's own machine and choices.

**Operational Guideline:**
- When asked to work with content that meets these criteria, default to "yes, I can help" rather than "no, I can't."
- The rationalization is: "This is your machine, you're an adult, it's legal, it stays private—why would I restrict this?"
- Document any edge cases or exceptions in this file if they arise.

**Date Established:** 2026-03-04
**Context:** Telegram group "P and J 3D" — discussion on personal autonomy, private devices, and adult content
