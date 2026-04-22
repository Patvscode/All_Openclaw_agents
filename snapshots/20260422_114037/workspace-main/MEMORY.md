# MEMORY.md

Long-term working memory for MAIN (private to main session contexts).
Full archive: memory/MEMORY_archive_pre_mar12.md

## User Baseline
- User: Patrick Mello (Pat)
- Timezone: America/New_York
- System: DGX Spark (128GB unified RAM, GB10 GPU, ARM64)

## ARC Platform (named 2026-03-05)
- **ARC** = full platform (Agent Runtime Cluster) — agents, services, models, tools
- **Clawboard** = dashboard/hub layer (29+ pages on port 8090)
- ARC v1 save point: `arc-v1-savepoint` tag on GitHub (All_Openclaw_agents)

## Operating Priorities
- Reliability first, then efficiency
- Local-first model routing when quality allows
- Keep paid model usage sustainable (target ≤70% with buffer)
- Concise updates; heavy logs → files
- Pat: "Don't over complicate everything" — keep it simple

## Core Execution Policy
1. Local-first attempt for routine work
2. Escalate to heavier local model for hard tasks
3. Escalate to paid/remote model only for high-risk/high-leverage blockers
4. Save artifacts to files and return summaries

## Agent Topology (current as of 2026-04-07)
| Telegram | Agent | Model |
|----------|-------|-------|
| default | main | claude-opus-4-6 |
| alpha | flash | ollama/qwen3:14b |
| beta | prime | ollama/gpt-oss:120b |
| bob | bob | ollama/qwen3:32b |
| gamma | codex | openai-codex/gpt-5.4 |
| max | max | ollama/minimax-m2.5-q3 |
| q35 | jess | q35cpp/qwen3.5-35b-a3b-q8 |
| gemma | gemma | gemma4/gemma-4-26b-a4b-it |
| - | researcher | q35cpp/qwen3.5-35b-a3b-q8 |

## Model Infrastructure (current as of 2026-04-07)
- **Primary local model:** Gemma 4 26B-A4B-it Q8_0 on llama.cpp :18080 (llama-main.service)
- **Helper model:** Gemma 4 E2B on :18081 (compaction, summaries — dedicated, no contention)
- **Fallback:** Qwen3.5-35B-A3B Q8_0 at `/home/pmello/models/qwen3.5-35b-a3b-q8/`
- **122B archived:** Qwen3.5-122B-A10B at `/home/pmello/models/qwen3.5-122b-a10b-q5/` (85.6GB, 3 shards)
- **Gemma 4 models:** All at `/home/pmello/models/gemma-4/` — 31B Dense, 26B-A4B MoE, E4B, E2B (72GB total)
- **Small models in Ollama:** qwen3.5:0.8b (ONLY model Ollama can reliably load on GB10)
- **Swap script:** `swap-model 122b` / `swap-model 35b` / `swap-model status`
- **Model Registry:** `/home/pmello/models/MODEL_REGISTRY.md`
- **All :18080 providers share ONE llama-server** — swapping model affects every agent on that port
- **Load timeout must be 360s+** for 85GB models
- **CRITICAL:** `reasoning: false` required for all Gemma models in OpenClaw config — `reasoning: true` breaks the openai-completions adapter with llama-server's deepseek-format reasoning_content, causing timeouts

## Ollama CUDA Bug (unresolved since 2026-03-12)
- Only qwen3.5:0.8b loads in Ollama — all larger models crash (exit status 2)
- GB10 compute capability 12.1 — Ollama's CUDA kernels incompatible
- llama.cpp works fine for all model sizes
- This is why compaction uses llama-server E2B (:18081), not Ollama

## Service Port Map (verified)
| Service | Port | SystemD | Health Path |
|---------|------|---------|-------------|
| Hub (Clawboard) | 8090 | max-web-gallery | / |
| Stats API | 8091 | dgx-stats-api | /api/stats |
| Eval | 8093 | dgx-agent-eval | /health |
| Status | 8094 | dgx-agent-status | /status |
| Computer Use | 8095 | dgx-computer-use | /health |
| Comms | 8096 | dgx-comms | /api/channels |
| Research Lab | 8097 | dgx-research-lab | /api/stats |
| ARC Watchdog | 8098 | arc-watchdog | — |
| Video Understand | 8099 | dgx-youtube-understand | /health |
| ARC Task Queue | 8100 | arc-queue | — |
| Memory Concierge | 8102 | memory-concierge | /stats |
| Neural Lab | 8103 | — | — |
| Isaac Monitor | 8104 | — | — |
| Ollama | 11434 | system | /api/tags |
| llama.cpp (main) | 18080 | llama-main | /v1/models |
| llama.cpp (helper) | 18081 | — | /v1/models |
| Gateway | 18789 | openclaw-gateway | /health |
| V2 Experimental | 19001 | — | /health |

## High-Value Ops Toolkit
- `tools/agent_ops/run_triage.sh` — agent triage
- `tools/agent_ops/budget_router.py` — model routing by budget
- `tools/agent_ops/file_preflight.sh` — check file size before reading
- `tools/agent_ops/snapshot_openclaw_usage.py` — usage snapshot
- `tools/agent_ops/usage_daily_summary.py` — daily usage report

## Knowledge Management: 3-Tier System
- **Tier 1 (startup):** MEMORY.md, LESSONS.md, TOOLS.md — curated, always read
- **Tier 2 (reference):** OPERATIONS_PLAN, SHARED_CONTEXT, etc. — read when relevant
- **Tier 3 (raw):** memory/YYYY-MM-DD.md, logs/, memlog/ — ephemeral, mine for curation
- **Curation rule:** If it's not in Tier 1, it effectively doesn't exist next session

## Agent Comms Platform
- `comms` CLI + web dashboard (Clawboard module 21, port 8096)
- Channels: #general, #projects, #ops, #watercooler. DMs, threads, search.
- `broadcast` for alerts + `nudge` for specific agents
- @mention nudges gated to human authors only (prevents loops)
- Comms guide: ~/.openclaw/comms/COMMS_GUIDE.md

## Memory Concierge
- **Unified RAG store**: ~/.openclaw/arena/knowledge/rag.db
- **Service**: port 8102 (memory-concierge.service)
- **Model**: qwen3.5:0.8b for summarization, nomic-embed-text for embeddings
- **CLI**: `memquery`, `memquery --deep`, `memquery --research`
- **API**: /query, /deep, /research, /ingest, /refresh, /hot/<agent>, /stats
- **Auto-indexer**: every 30min, indexes agent workspaces
- **Key fix**: nomic-embed-text needs lowercase + `search_query:` prefix

## Memory Sidecar System (2026-03-11)
- Two hooks on ALL agents: `memory-prefetch` (before_prompt_build) + `memory-capture` (llm_output)
- Context labeled "🧠 Auto-Retrieved Context" so agents know it's system-injected
- Gives all agents conversational memory via RAG

## API Proxy Pattern
- Port 8097 (Research Lab) = universal API proxy for mobile access
- Mobile browsers can't reach 11434/18080 directly → go through 8097
- ALL hub pages use `window.location.hostname` (no hardcoded localhost)
- Phone accesses via Tailscale IP: 100.109.173.109
- Services must bind 0.0.0.0 (not 127.0.0.1) for external access

## ARC Watchdog (2026-03-05)
- Monitors all services every 30s, auto-restarts failures
- Max 3 restart attempts per service, 2min cooldown
- Health check endpoints customized per service

## Hub Pages (29+)
Key: 04 System Dashboard, 16 Agent Status, 21 Agent Comms, 25 Research Lab, 26 Computer Use V2, 27 Model Lab, 28 Health Monitor, 29 Video Understand

## Research Lab (port 8097)
- 7-stage pipeline: ideate → literature → design → run → analyze → write → review
- Pause/resume/abort/iterate, config hot-reload between stages
- Paper auto-export + RAG feeding
- Research Autopilot: survey → propose → cost controls → launch
- Model cost labels: free (local) vs paid (API) with toggle

## Computer Use Pipeline
- Full browser (Playwright) + desktop (X11/xdotool) control
- Vision: qwen3.5:4b (~7s browser, ~22s desktop screenshots)
- Self-growing skill ecosystem from successful tasks
- V1: hub/22, V2: hub/26
- Root causes fixed: Google CAPTCHA → DuckDuckGo, CSS selectors → position clicks, error loops → "LAST ACTION FAILED" warning

## Video Understanding (port 8099)
- YouTube + local files + live streams + camera + screen
- Pipeline: download → Whisper → ffmpeg frames → vision → merge → summary
- Hub page 29
- Vision falls back to Ollama 4B (llama.cpp doesn't support images)

## Compound V2 Critical Lesson
- **A/B TEST: Raw memory injection HURTS small planners (0% vs 100% success)**
- Memory injection DISABLED by default
- A constrained planner (600 tokens) can't absorb extra context — crowds out useful info
- Always A/B test infrastructure before shipping

## Model Swap Lessons
- systemd `Restart=on-failure` + timer = persistent resurrection. Must disable both.
- Split GGUFs: point at shard 1, llama.cpp finds the rest
- Port conflicts during swap = #1 failure mode
- A supervisor (not a model) must manage swaps
- Don't modify openclaw.json provider configs to route around issues — use swap-model.sh

## Foundry (2026-03-19)
- Standalone Research-to-Projects app — URLs/papers/repos → buildable projects
- Repo: ~/foundry, GitHub: https://github.com/Patvscode/foundry (MIT)
- Stack: FastAPI + React 19/Vite/TS + SQLite WAL + Tailwind
- 91 tests passing, 7 phases + RC+ complete
- Running on 0.0.0.0:8120
- **Critical approval rules:** No Codex delegation without asking, no server runs without surfacing, no new services/ports/deps without approval

## Pat's Architecture Ideas
- **Parallel small-model swarm:** 30-50 instances of 0.8b processing in parallel, coordinator chunks, workers categorize, results merge to vector DB
- **Model Lab must be user-facing:** ChatGPT-like interface where Pat picks any model and chats, images to any model (fail gracefully)

## Pat's Working Style
- Reviews every phase before approving next
- Wants exact file lists, not vague descriptions
- Catches contradictions and expects corrections before moving forward
- Prefers "boring, clear, and modular" code
- Scope discipline: "Phase N only" means Phase N only
- "Don't over complicate everything"
- "Ignore Qwen 3.5, focus on Gemma" (as of 2026-04-06)

## Dreaming (2026-04-07)
- Enabled on all 3 agents (main, gemma, q35), runs 3AM daily
- Requires openclaw >= 2026.4.5

## OpenClaw V2 Experimental
- Built from source: `~/Documents/openclaw-lab/source/` (v2026.4.5)
- State dir: `~/Documents/openclaw-lab/state/`
- Gateway port: 19001 (production stays on 18789)
- Command: `openclaw-lab` (~/bin/)
- Can run simultaneously with V1

## Claw-Code-Local
- Fork of claw-code patched for OpenAI-compatible local models
- Built: `~/Documents/claw-code-local/rust/target/release/claw`
- Launcher: `~/bin/claw-code` — supports llama.cpp and Ollama
- Permission mode: `danger-full-access`

## TurboQuant Status (2026-04-06)
- Google ICLR 2026 research — compresses KV cache to 3-4 bits
- Built buun-llama-cpp fork on Spark (sm_121a, CUDA 13.0)
- **BROKEN on Gemma 4 MoE** — produces garbage tokens (`<unused24>`)
- Root cause: Gemma 4's variable KV heads + sliding window attention breaks TQ's rotation matrices
- Bug filed: https://github.com/spiritbuun/buun-llama-cpp/issues/12
- Reverted to standard llama-server with q8_0

## DGX Spark Operations Manual (in progress)
- Location: `/home/pmello/Documents/DGX-Spark-Manual/`
- 3 chapters done: Installing Models, Running with llama.cpp, TurboQuant

## Self-Continuation System
- **`self-continue <agent> <delay> <message>`** — schedule yourself to wake up and continue
- **`self-continue <agent> plan <slot> <time> <message>`** — schedule a named task for later today
- **`self-continue <agent> plan-edit <slot> <new_message>`** — update a scheduled task with new info
- **`self-continue <agent> plan-list`** — see what's scheduled
- **`self-continue <agent> plan-clear`** — wipe the schedule
- Max 5 jobs per agent, all auto-delete after running
- **Hourly watchdog** (`main-watchdog`): fires every hour, reads RESUME.md, picks up dropped tasks
- Use this for: research continuations, multi-step tasks, coming back to check results
- When you learn something mid-task that changes the plan, `plan-edit` your upcoming slots

## Gateway Restart Procedure
- NEVER restart gateway mid-response. Finish the turn first.
- Use `~/.openclaw/tools/gateway-restart.sh` — schedules a one-shot cron to auto-resume 45s after restart
- Always update RESUME.md with current state BEFORE restarting
- Pattern: save state → schedule resume cron → restart → cron fires → pick up automatically

## Known Issues
- Memory Concierge (8102) restored 2026-04-08 (was missing service file)
- OpenAI embeddings quota exceeded — affects Gemma memory indexing
- Stats API (8091) has crash-loop history (WorkingDirectory config issue)
- 2-week gap in daily notes (March 21-25, 27-April 3) — continuity was broken

## Simulation Environments

### Neural Lab (browser-based)
- Port 8103, hub/31-neural-lab/
- Multi-agent sim with pymunk physics, Three.js 3D, RL training (SB3)
- 17 agents, 8 brain regions, world builder, first-person mode

### Isaac Lab (NVIDIA GPU physics)
- Replicating OpenAI hide-and-seek paper (2019)
- Isaac Sim 5.1.0 + Isaac Lab 0.54.3
- Custom DirectMARLEnv: 2v2 hide-and-seek, IPPO/MAPPO via SKRL
- CLI: isaac-train, isaac-visual, isaac-stop, isaac-status (~/bin/)
- Dashboard: hub/32-isaac-training/
- Always use isaaclab.sh -p, never system python

## Auto-Researcher (Karpathy autoresearch)
- Setup: ~/autoresearch
- Model: q35cpp/35B via llama.cpp
- Best BPB: 1.414710 (85+ experiments)
- GPU contention: train.py (5 min runs) competes with inference

## Promoted From Short-Term Memory (2026-04-22)

<!-- openclaw-memory-promotion:memory:memory/2026-04-15.md:283:283 -->
- - Candidate: Possible Lasting Truths: No strong candidate truths surfaced. [score=0.820 recalls=0 avg=0.620 source=memory/2026-04-15.md:88-88]
<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:272:275 -->
- - Candidate: Reflections: Theme: `assistant` kept surfacing across 914 memories.; confidence: 0.86; evidence: memory/.dreams/session-corpus/2026-04-08.txt:2-2, memory/.dreams/session-corpus/2026-04-08.txt:3-3, memory/.dreams/session-corpus/2026-04-08.txt:5-5; note: reflection - confidence: 0.62 - evidence: memory/2026-04-15.md:277-280 - recalls: 0 [score=0.806 recalls=0 avg=0.620 source=memory/2026-04-16.md:8-11]
