# MEMORY.md

Long-term working memory for MAIN. Full archive: memory/MEMORY_archive_pre_mar12.md

## User Baseline
- User: Patrick Mello (Pat)
- Timezone: America/New_York
- System: DGX Spark (128GB RAM, GB10 GPU, ARM64)

## Core Priorities
- Reliability first, then efficiency
- Local-first model routing
- Keep paid model usage sustainable
- Concise updates; heavy logs → files

## Agent Topology
| Telegram | Agent | Model |
|----------|-------|-------|
| default | main | claude-opus-4-6 |
| alpha | flash | ollama/qwen3:14b |
| beta | prime | ollama/gpt-oss:120b |
| bob | bob | ollama/qwen3:32b |
| gamma | codex | openai-codex/gpt-5.4 |
| max | max | ollama/minimax-m2.5-q3 |
| q35 | jess | q35cpp/qwen3.5-35b-a3b-q8 |
| - | researcher | q35cpp/qwen3.5-35b-a3b-q8 |

## Key Services (ports)
- 8090 Hub/Clawboard | 8093 Eval | 8094 Status | 8095 Computer Use
- 8096 Comms | 8097 Research Lab | 8098 Watchdog | 8099 Perception Engine
- 8100 Task Queue | 8102 Memory Concierge | 8103 Neural Lab | 8104 Isaac Monitor
- 11434 Ollama | 18080 llama.cpp (35B) | 18789 Gateway

## Ollama CUDA Issue (2026-03-12)
- Only qwen3.5:0.8b loads in Ollama — all larger models crash (exit status 2)
- GB10 compute capability 12.1 — likely CUDA compatibility bug
- llama.cpp works fine for 35B model

## Auto-Researcher (Karpathy autoresearch)
- Setup: ~/autoresearch, Karpathy's autoresearch repo
- Supervisor: researcher-supervisor.sh (spawns sessions via openclaw agent)
- Model: q35cpp/35B via llama.cpp
- Best BPB: 1.414710 (85+ experiments)
- Key fix (2026-03-12): 122B model swap broke it, switched back to 35B, reduced tools, cleared stale locks
- GPU contention: train.py (5 min runs) competes with 35B inference

## Deep Research Feature (2026-03-12)
- Built by Codex (gpt-5.4): deep_research.py (746 lines)
- 6-stage pipeline: prepare → plan → gather → analyze → synthesize → ingest
- API: POST /api/deep-research/<job_id>, GET status/report
- BUG: Worker IDs need dual registration (prefixed + original) — fixed
- ISSUE: 35B planning/synthesis timeouts when GPU shared with auto-researcher
- NEEDS: Hub UI page with worker cards (like existing swarm UI)

## Perception Engine Enhancements (2026-03-12)
- Adaptive swarm profiles per modality (audio, pdf, video, url, repo, etc)
- Proactive downloads: clones repos, fetches papers, downloads datasets
- RAG ingestion: full summary + chunked detailed extraction via Memory Concierge API
- Data Library Ask AI fix: 0.8b thinking field fallback

## Memory Concierge
- Port 8102, auto-indexer every 30min
- CLI: memquery, memquery --deep, memquery --research
- Memory sidecar hooks on all agents (prefetch + capture)

## Known Issues
- MEMORY.md was 23.5KB causing context overflow — trimmed
- Researcher sessions overflow context (81K tokens vs 65K limit)
- 35B inference slow when GPU shared with training
