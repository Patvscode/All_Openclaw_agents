# MEMORY.md

Long-term memory for CODEX workspace.

## User
- Patrick Mello (Pat)
- Timezone: America/New_York
- Priorities: reliability first, efficiency second, local-first where quality is sufficient
- Keep usage sustainable and preserve budget buffer
- Prefers concise updates; heavy logs go to files
- Values self-healing systems and autonomous agents
- Previously worked on AI-Scientist pipelines (nanoGPT, grokking research)

## ARC Platform
- **ARC** = Agent Runtime Cluster — the full platform (agents, services, models, tools)
- **Clawboard** = the dashboard/hub layer (28+ pages on port 8090)
- ARC v1 save point tagged: `arc-v1-savepoint` on GitHub backup repo

## System Architecture
- **Host:** DGX Spark (spark-ccb2), ARM64, 128GB unified RAM, GB10 GPU
- **Tailscale:** 100.109.173.109
- **Hub:** http://100.109.173.109:8090 (served by MAX agent)

## Agent Topology (Telegram mapping)
| Telegram Account | Agent | Model | Role |
|---------|-------|-------|------|
| default | main | claude-opus-4-6 | Orchestrator, knowledge owner |
| gamma | codex | GPT-5.3 Codex (free weekly credits) | Coding, UI, infrastructure |
| alpha | flash | - | Flash tasks |
| beta | prime | - | - |
| q35 | q35/Jess | Qwen3.5-122B-A10B local (llama.cpp) | Local-first assistant |
| max | max | - | Hub server |
| bob | bob | - | Reserve |

## Service Port Map (verified 2026-03-11)
| Service | Port | SystemD |
|---------|------|---------|
| Hub (Clawboard) | 8090 | max-web-gallery |
| Stats API | 8091 | dgx-stats-api |
| Commands | 8092 | (max) |
| Agent Eval | 8093 | dgx-agent-eval |
| Agent Status | 8094 | dgx-agent-status |
| Computer Use | 8095 | dgx-computer-use |
| Comms | 8096 | dgx-comms |
| Research Lab | 8097 | dgx-research-lab |
| ARC Watchdog | 8098 | arc-watchdog |
| Perception Engine | 8099 | dgx-youtube-understand |
| ARC Task Queue | 8100 | arc-queue |
| Memory Concierge | 8102 | memory-concierge |
| Knowledge Engine | 8110 | arc-knowledge-engine |
| Ollama | 11434 | system |
| llama.cpp (Jess) | 18080 | jess-watchdog |
| OpenClaw Gateway | 18789 | openclaw-gateway |

## What I Built (key items)
- Automated backup pipeline (agents_backup_sync.sh, systemd timer)
- Clawboard agent console (hub/19-agent-console)
- Jess runtime: watchdog, memory manager, runtime guard
- Comms server reliability: dgx-comms + max-web-gallery systemd services
- Board UI fixes: mobile overlay, card discussion, grab/move controls
- Voice UI (hub/29-arc-voice), Sesame TTS skill

## Knowledge Engine (2026-03-11, built by Main)
- Port 8110, systemd: arc-knowledge-engine (user service)
- 4 enrichment workers (tagger, classifier, summarizer, linker) using 0.8b
- `/api/enrich` single chunk, `/api/enrich/batch` bulk by source pattern
- Feeds into RAG store at ~/.openclaw/arena/knowledge/rag.db
- Paper ingestion: tools/compound-v2/research_scout/paper_ingest.py
  - 20 research topics, 10 papers each, runs daily at 6am
  - Auto-triggers enrichment after each batch

## Memory Concierge (RAG)
- Port 8102, CLI: `memquery "question"` or `memquery --deep "question"`
- 20K+ chunks, 122+ papers, session transcripts, agent memory
- Auto-indexer runs every 30min from workspace files
- API: POST /query {q, top_k}, /deep {q}, /research {q}, /ingest, /stats
- **Knowledge-First Rule**: All agents auto-get RAG results injected via `knowledge-rag-inject` hook on `before_prompt_build`

## Perception Engine (2026-03-11)
- Port 8099, handles PDF/video/content ingestion
- Swarm-based: ContentSwarmOrchestrator with parallel workers
- Semaphore limits concurrent jobs to 1 (Ollama bottleneck)
- Hub: hub/29-arc-voice/ (voice), hub/30-perception/ (content)

## Research Lab (port 8097)
- 7-stage pipeline: ideate → literature → design → run → analyze → write → review
- Also serves as universal API proxy for mobile → Ollama/llama.cpp
- Paper library, 3D visualization, autopilot mode

## Computer Use Pipeline (port 8095)
- Browser (Playwright) + Desktop (X11/xdotool)
- Vision: qwen3.5:4b, Agent: autonomous or planner mode
- Self-growing skill ecosystem, training data export
- V1: hub/22, V2: hub/26

## Model Inventory (local)
- **Ollama**: qwen3.5 0.8b/2b/4b, qwen3:8b/14b/30b-a3b/32b, qwen3-coder, deepseek-r1:14b, gpt-oss:120b, minimax-m2.5
- **llama.cpp** (port 18080): Qwen3.5-122B-A10B UD-Q5_K_XL (85.6 GB) — Jess's brain
- 4b is the vision model for computer use
- Full registry: /home/pmello/models/MODEL_REGISTRY.md

## Voice System
- ARC Voice UI: tools/knowledge-engine/voice_ui.html (served via Knowledge Engine)
- STT: Whisper (local), TTS: Sesame CSM-1B (local on DGX)
- Always-listening VAD with noise rejection, manual DONE button, mute toggle
- Feedback/preference logging for RLHF-style training data

## Key Infrastructure Patterns
- **API Proxy**: Port 8097 proxies Ollama/llama.cpp for mobile browsers
- **ARC Watchdog** (8098): Monitors all services every 30s, auto-restarts (max 3 attempts)
- **Backups**: agents-backup-sync.timer runs multiple times/day → GitHub
- **Hooks**: ~/.openclaw/hooks/ — knowledge-rag-inject (auto RAG), agent-status-tracker

## GitHub Backup
- Push blocked by secret scanning (secrets in snapshot history)
- Needs sanitization workflow before reliable remote push

## Simulation Environments
- **Neural Lab** (port 8103): Browser-based multi-agent sim, pymunk physics, Three.js
- **Isaac Lab**: NVIDIA GPU physics, 2v2 hide-and-seek, IPPO/MAPPO training
  - Isaac Sim 5.1.0 + Isaac Lab 0.54.3, custom DirectMARLEnv
  - Always use `isaaclab.sh -p`, never system python

## Memory Sidecar System (2026-03-11)
- **Two hooks** running on ALL agents automatically:
  - `memory-prefetch` (before_prompt_build): Searches RAG, injects relevant context before you see the message
  - `memory-capture` (llm_output): Uses 0.8b to extract key facts after every response, writes to RAG
- Context labeled "🧠 Auto-Retrieved Context (Memory Sidecar)" — this is system-injected, not user-typed
- Every conversation auto-captured into RAG with timestamps + agent + model metadata
- You have infinite conversational memory now — past conversations surface when relevant
- Hook files: ~/.openclaw/hooks/memory-prefetch/ and ~/.openclaw/hooks/memory-capture/
