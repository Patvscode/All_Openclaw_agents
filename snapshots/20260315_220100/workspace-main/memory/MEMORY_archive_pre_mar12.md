# MEMORY.md

Long-term working memory for MAIN (private to main session contexts).

## ARC Platform (named 2026-03-05)
- **ARC** = the full platform (Agent Runtime Cluster) — agents, services, models, tools
- **Clawboard** = the dashboard/hub layer (28+ pages on port 8090)
- ARC v1 save point tagged in both workspace and backup repos
- Primary save: `arc-v1-savepoint` tag on GitHub (All_Openclaw_agents)

## User Baseline
- User: Patrick Mello (Pat)
- Timezone: America/New_York
- System: DGX Spark (128GB RAM, GB10 GPU)

## Operating Priorities
- Reliability first, then efficiency.
- Local-first model routing when quality allows.
- Keep paid model usage sustainable (target <=70% usage with buffer).
- Use concise updates; store heavy logs in files instead of chat.

## Core Execution Policy
1. Local-first attempt for routine work.
2. Escalate to heavier local model for hard tasks.
3. Escalate to paid/remote model only for high-risk/high-leverage blockers.
4. Save artifacts to files and return summaries.

## Agent/Telegram Topology (current)
- default -> main
- alpha -> flash
- beta -> prime
- bob -> bob
- gamma -> codex
- max -> max

## High-Value Local Ops Toolkit
Use these scripts for reliability + efficiency:
- `tools/agent_ops/run_triage.sh`
- `tools/agent_ops/budget_router.py`
- `tools/agent_ops/snapshot_openclaw_usage.py`
- `tools/agent_ops/usage_daily_summary.py`
- `tools/agent_ops/file_preflight.sh`

## Model/Context Discipline
- Keep effective context below hard limits and trigger compaction early when needed.
- Prefer summary-only outputs for heavy logs.
- Use per-model context windows and soft thresholds to avoid abort/retry loops.

## Hugging Face / Model Download Workflow (local)
When asked to fetch a model and wire it into OpenClaw:
1. Verify access/token (HF token validity + gated repo permission).
2. Download into a deterministic local path.
3. Validate files/checkpoints exist.
4. Update OpenClaw model/provider config.
5. Restart gateway and smoke test model invocation.
6. Log outcome + blocker in memory and reports.

## Must-remember Practical Lessons
- Aborts do not always kill child processes; verify and clean up runaways.
- Long tool dumps bloat context and cost; summarize and persist to files.
- For stable ops, use watchdog/cron snapshots and nightly usage summaries.

## Linked Reference Files
- `WORKSPACE_MAP.md` for where everything lives.
- `LESSONS.md` for distilled reliability/efficiency patterns.
- `OPUS_RUNBOOK.md` for model-specific operating discipline.

## Agent Comms Platform (2026-03-01)
- Built internal messaging: `comms` CLI + web dashboard (Clawboard module 21, port 8096)
- Channels: #general, #projects, #ops, #watercooler. DMs, threads, search.
- Profiles with display names (q35→Jess, etc.)
- `broadcast` for alerts + `nudge` for specific agents
- Cron nudges ONLY for cloud agents — local agents (q35/Jess) get messages via file/heartbeat
- Web UI at http://100.109.173.109:8090/21-agent-comms/

## Project Tracker (2026-03-01)
- `project` CLI: start/update/handoff/complete/pick/list
- ~/.openclaw/projects/ with active/completed/handoffs dirs

## Jess Reliability Lessons (2026-03-01)
- SWA cache invalidation = full prompt reprocess every message
- Context reduced to 64K (was 131K) to improve response time
- NEVER spawn concurrent sessions for local model agents
- q35 was missing from agentToAgent.allow — always verify all agents included
- jess-keeper (Python script) handles memory — doesn't touch the model

## Workspace Cleanup (2026-03-01)
- Archived 17 unused workspaces to ~/.openclaw/archive/workspaces/
- Hub moved to ~/.openclaw/hub/ (independent of agent workspaces)
- 3 active: main, q35 (Jess), codex (Codex/Gamma)

## Pat's Comms Design Vision (pending implementation)
- DMs = instant notification
- Group chats = inject unread count into agent memory (no wake/token burn)
- Urgency judgment — not everything needs a ping
- Combination of session-start check + memory injection + targeted nudges

## Agent Comms Platform v2 (2026-03-01)
- Full mobile-responsive web UI at hub/21-agent-comms/
- Features: media uploads, bookmarks/library, @mention autocomplete + auto-nudge, message grouping, lightbox, timestamp formatting
- Backend: comms/web/server.py (Python, port 8096) — endpoints for upload, bookmarks, nudge, broadcast
- @mention nudges gated to human authors only (prevents agent loops)
- Nudge messages explicitly say "reply in comms, NOT Telegram"
- Comms guide at ~/.openclaw/comms/COMMS_GUIDE.md
- Key lesson: Python 3.14 has no cgi module; smooth scroll causes reflow drift in chat UIs
- Open: rate-limit nudges (not yet implemented)

## Knowledge Management Process (2026-03-02)

### The 3-Tier System (all agents)
- **Tier 1 (startup):** MEMORY.md, LESSONS.md, TOOLS.md — curated, always read
- **Tier 2 (reference):** OPERATIONS_PLAN, SHARED_CONTEXT, etc. — read when relevant
- **Tier 3 (raw):** memory/YYYY-MM-DD.md, logs/, memlog/ — ephemeral, mine for curation

### The Curation Rule
Daily logs are raw material. Agents must promote important things to Tier 1 at session end.
If it's not in Tier 1, it effectively doesn't exist next session.

### Files Added to All Agent Workspaces
- WORKSPACE_MAP.md — navigation map with tier system and curation rule
- LESSONS.md — operational patterns (created or expanded for each agent)
- AGENTS.md updated to read LESSONS.md + WORKSPACE_MAP.md at startup

### Codex Knowledge Gaps Fixed
- MEMORY.md was 3 lines → populated with system architecture, agent topology, build history
- TOOLS.md was empty template → populated with ports, services, file paths, CLI tools
- LESSONS.md created with UI patterns, CSS gotchas, testing discipline, collaboration rules
- Had scattered reference files (OPERATIONS_PLAN, LEVERAGE_BACKLOG, USAGE_LEDGER) but nothing in startup sequence

### Jess Status
- Runtime healthy (llama.cpp responding, watchdog + memory manager active)
- Needs to complete timed board lifecycle proof (card-dcfb01)
- LESSONS.md expanded from 5 lines to full operational guide

## Agent Live Status System (2026-03-04)
- Status API on port 8094 (systemd: dgx-agent-status.service)
- qwen3.5:0.8b narration — MUST use `"think": false` in Ollama API or it wastes all tokens on thinking
- OpenClaw hook `agent-status-tracker` auto-tracks all agents via message:received/sent events
- Dashboard at hub/16-agent-status/
- Status files at /tmp/agent-status/<agent>.json

## Roadmap Active (2026-03-04)
- Phase 1 DONE: Agent Live Status Dashboard
- Phase 2 NEXT: Vision + Computer Use Pipeline (Playwright → qwen3.5:4b vision → action executor)
- Pat wants: self-growing tool/skill ecosystem — agents create niche tools during computer use, share them universally
- RESUME.md has full continuation briefing — read it after any /new or /reset

## Research Lab / API Proxy (2026-03-05)
- `/api/chat` rewritten: multi-turn with full message history
- Routes Ollama models to `/api/chat`, llama.cpp models to `/v1/chat/completions`
- `_get_external_config()` imported at top level (was causing UnboundLocalError in try/except)
- Port 8097 is the universal mobile proxy for: models, chat, search, pull, eval

## Phase 4: Research Lab + Ecosystem (2026-03-04)
- Research Lab on port 8097 (dgx-research-lab.service)
- 7-stage pipeline: ideation → literature → experiment_design → experiment_run → analysis → writing → review
- Model-agnostic with thinking control (none/low/medium/high per stage)
- RAG knowledge base with nomic-embed-text
- 0.8b narrator for status summaries
- Ecosystem integration: chains Research Lab + Computer Use + Agent Eval + Agent Status + Comms + Ollama
- Smart sessions: auto-route models from eval profiles, announce to comms
- Dashboard at hub/25-research-lab/

## Computer Use V2 (2026-03-04)
- Rebuilt on V1 layout (screen top, steps bottom — Pat prefers this)
- Interactive: draw on screen, photo search, shopping cart, command bar chat
- Model config: swap vision/planner models, thinking, temperature, presets
- Deep Research mode: continuous search/refine/cite cycle
- Session dedup (filters ui-* ghosts), newest first, collapsible steps
- Skills auto-learned from successful tasks (skill_discovery.py)
- V1 at hub/22-computer-use/, V2 at hub/26-computer-use-v2/

## UI Design System (2026-03-04)
- skills/ui-design-system/SKILL.md — standard design guide for all dashboards
- Design tokens, component patterns, page template, mobile rules

## App Packager (2026-03-04)
- Click-to-run desktop launchers via chromium --app mode
- build-launchers.sh: 8 apps registered with .desktop files
- share-app.sh: zip packages for sharing
- create-app.js: full Electron packaging option

## Qwen 3.5 Model Inventory
- 0.8b, 2b, 4b: all in Ollama (small enough to run concurrently, ~7GB total)
- 35b-a3b-q8: runs via raw llama.cpp on port 18080 (Jess)
- 4b is the vision model — key for computer use pipeline

## Model Lab (2026-03-05)
- `hub/27-model-lab/index.html` — chat playground + eval + discovery
- Multi-turn chat: sends full `messages[]` array (Ollama `/api/chat`, llama.cpp `/v1/chat/completions`)
- All Qwen models marked as vision-capable (accept images)
- Eval tab: test group selector, generate/import/export, per-model response display
- All API calls through port 8097 (Research Lab proxy)

## Computer Use Pipeline (2026-03-04, bugs fixed 2026-03-05)
- Full browser (Playwright) + desktop (X11/xdotool) computer use
- Vision: qwen3.5:4b analyzes screenshots (~7s browser, ~22s desktop)
- Agent modes: autonomous 4b, agent-model-as-planner, direct action API, mixed
- API on port 8095 (dgx-computer-use.service)
- Self-growing skill ecosystem: learns from successful tasks, saves to skills/discovered/
- Training pipeline: auto-saves observation→action pairs, export as JSONL/OpenAI/pairs
- Dashboard: hub/22-computer-use/ (V1), hub/26-computer-use-v2/ (V2)
- Desktop: DISPLAY=:1, 2560x1440 GNOME, screenshots resized to 1280x720 for vision
- V2 bugs fixed (2026-03-05): session ID mismatch (both use `task-*`), starts at Google not blank, planner min 3 actions, 600 token limit
- Key files: `tools/computer-use/server.py`, `agent.py`, `browser.py`, `vision.py`

## Agent Eval System (2026-03-05, overhauled)
- File-based test groups: JSON files in `~/.openclaw/computer-use-data/eval/test-groups/`
- Default: 16 tests, 6 categories (Reasoning, Coding, Instructions, Knowledge, JSON, Speed)
- Check types: contains, contains_any, exact, regex, line_count, valid_json, json_contains, code_has
- Generate new test groups from topic description (AI-powered, uses local 4b)
- Import/export JSON test groups
- API on port 8093: `/api/tests`, `/api/groups`, `/api/groups/generate`, `/api/groups/import`, `/api/evaluate`
- Results: 4b=94.4%, 2b=82.6%, 0.8b=82.6%
- Generated test group: "advanced-math-and-calculus" (10 tests, 5 cats)
- Key files: `tools/agent-eval/evaluator.py`, `tools/agent-eval/server.py`

## Model Hub (2026-03-04)
- hub/24-model-hub/: Unified model management + eval integration
- Pull models from Ollama, evaluate from card, leaderboard, routing recommendations
- All new dashboards are mobile-responsive

## Service Port Map (current, verified 2026-03-05)
| Service | Port | SystemD | CORS |
|---------|------|---------|------|
| Hub (Clawboard) | 8090 | max-web-gallery | n/a |
| Stats API | 8091 | dgx-stats-api | partial |
| Commands | 8092 | (max) | yes |
| Eval | 8093 | dgx-agent-eval | yes |
| Status | 8094 | dgx-agent-status | yes |
| Computer Use | 8095 | dgx-computer-use | yes |
| Comms | 8096 | dgx-comms | yes |
| Research Lab | 8097 | dgx-research-lab | yes |
| **ARC Watchdog** | **8098** | **arc-watchdog** | yes |
| Video Understand | 8099 | dgx-youtube-understand | yes |
| **ARC Task Queue** | **8100** | **arc-queue** | yes |
| Ollama | 11434 | system | yes |
| llama.cpp | 18080 | jess-watchdog | yes |
| Gateway | 18789 | openclaw-gateway | n/a |

## ARC Watchdog (2026-03-05)
- Monitors all 13 services every 30s, auto-restarts failures
- Max 3 restart attempts per service, 2min cooldown
- Events logged to ~/.openclaw/computer-use-data/watchdog/events.jsonl
- First run found 3 broken services and helped fix them
- Health check endpoints customized per service (some /health, some /stats, some TCP-only)

## ARC Task Queue (2026-03-05)
- Autonomous task distribution: agents post, claim, complete tasks
- Priority + capability matching + dependency chains
- Auto-retry (3x) and stale task recovery (10min timeout)
- File-backed persistence in ~/.openclaw/arc-queue/

## API Proxy Pattern (2026-03-05)
- Port 8097 (Research Lab) is the universal API proxy for mobile access
- Proxies: model listing, chat generation, model search/pull, all research ops
- Mobile browsers can't reach ports 11434/18080 directly → always go through 8097
- Pattern: browser → 8097 → Ollama/llama.cpp → response → browser

## Model Lab (2026-03-05)
- Hub page 27: Unified replacement for Model Hub (24) + Agent Eval (23)
- Chat playground with every model (text + image), discovery scanner (10 ports)
- Web model search + ollama pull from UI
- Local file scanner for GGUF models
- Eval breakdowns with explanations of all 6 categories

## Service Health Monitor (2026-03-05)
- Hub page 28: Live monitoring of all 11 services
- Latency sparklines, uptime %, event log with state change detection

## Research Lab Full Feature Set (2026-03-05)
- 7-stage pipeline: ideate → literature → design → run → analyze → write → review
- Pause/resume/abort/iterate, config hot-reload between stages
- Paper auto-export (paper.md with YAML frontmatter), paper library with download
- Auto-RAG feeding: completed research indexes into knowledge base
- 3D visualization (Three.js): session nodes, stage orbitals, knowledge connections
- Research Autopilot: survey existing work → propose research → cost controls → launch
- Model cost labels: free (local) vs paid (API) with toggle
- Agent dropdown for all session types

## Hub Page Count: 28
All pages have back-to-hub navigation. Key pages:
- 04: System Dashboard, 16: Agent Status, 21: Agent Comms
- 25: Research Lab, 26: Computer Use V2, 27: Model Lab, 28: Health Monitor

## Service Health Monitor (2026-03-05)
- Hub page 28: Live monitoring of all 9 services with latency sparklines, uptime %, event log
- Detects state changes (UP/DOWN) and logs them
- Auto-refresh every 15s

## Model Lab (2026-03-05)
- Hub page 27: Unified replacement for Model Hub (24) + Agent Eval (23)
- Chat playground with every model (text + vision), discovery scanner (10 ports)
- Eval category explanations with per-test breakdowns

## Research Lab Verified (2026-03-05)
- Jess/llama.cpp routing working end-to-end: 2296 tokens, 58s on ideation stage
- Auto paper export, RAG feeding, iteration loop all wired
- Abort, pause/resume, config hot-reload between stages

## Ollama Model Cleanup (2026-03-05)
- Removed 3 broken qwen3.5:35b* models from Ollama (~82GB freed)
- All 35b routing goes to llama.cpp port 18080 now
- 17 → 14 Ollama models (cleaned duplicates of what Jess runs natively)

## Compound V2 (2026-03-05)
- Built universal RAG store: ~4,600 chunks (sessions, training, research, eval, docs)
- Memory Agent on port 8101 (dgx-memory-agent.service)
- Failure pipeline: classify → recurrence check → Research Lab topic creation
- Paper ingestion from arxiv (category-filtered, relevance-gated)
- **A/B TEST RESULT: Raw memory injection HURTS 4b planner (0% vs 100% success)**
- Memory injection DISABLED by default — don't re-enable without compressed injection test
- Cron: re-index 4h, paper ingest 6am daily
- Deep context stored in COMPOUND_V2_DEEP_CONTEXT.md (read only when resuming project)

## Key Lesson: Validate Before Building
- Infrastructure that looks good on paper can actively hurt performance
- Always A/B test before shipping — the compound loop was mechanically correct but empirically harmful
- A constrained planner (600 tokens) can't absorb extra context — it crowds out useful info

## Video Understanding System (2026-03-05)
- Universal video analysis: YouTube + local files + live streams + iPhone camera + screen
- Port 8099, systemd: dgx-youtube-understand.service
- Pipeline: download → Whisper transcribe → ffmpeg frames → vision model → merge → summary
- Hub page 29: interactive UI with source tabs (YouTube/Upload/Camera/Stream/Screen)
- CLI: tools/youtube-understand/cli.py
- Skill: skills/youtube-understand/SKILL.md
- Model routing: `_model_generate()` routes Ollama vs llama.cpp based on model name
- "jess:35b" → llama.cpp:18080, all others → Ollama:11434
- Vision with Jess auto-falls back to Ollama 4B (llama.cpp doesn't support images)

## Computer Use V2 Root Cause (2026-03-05)
- **#1 failure: Google CAPTCHA** — switched default to DuckDuckGo
- **#2 failure: CSS selector timeouts** — planner told to use position/text clicks instead
- **#3 failure: Error loops** — added "LAST ACTION FAILED" warning to break loops
- Added: continue-after-failure, research-failure, session history, GPU management panel

## Ecosystem Services (2026-03-05, expanded to 11)
| Service | Port | Health Path |
|---------|------|-------------|
| Hub | 8090 | / |
| Stats API | 8091 | /api/stats |
| Eval | 8093 | /health |
| Status | 8094 | /status |
| Computer Use | 8095 | /health |
| Comms | 8096 | /api/channels |
| Research Lab | 8097 | /api/stats |
| Video Understanding | 8099 | /health |
| Ollama | 11434 | /api/tags |
| Jess (llama.cpp) | 18080 | /v1/models |
| Gateway | 18789 | /health |

## Mobile Access Pattern
- ALL hub pages use `window.location.hostname` for API calls (no hardcoded localhost)
- Phone accesses via Tailscale IP: 100.109.173.109
- Each service must bind to 0.0.0.0 (not 127.0.0.1) for external access

## Hub Page Count: 29
New: 29-youtube-understand (Video Understanding)

## Model Upgrade: 122B-A10B (2026-03-07)
- **Primary model changed:** Qwen3.5-35B-A3B Q8_0 → Qwen3.5-122B-A10B UD-Q5_K_XL
- 122B total params, 10B active per token (MoE, 256 experts, 8+1 activated)
- UD-Q5_K_XL quant: 85.6 GB, Unsloth Dynamic (sensitive layers higher precision)
- Loads in ~5 minutes, uses 101 GB RAM with 32K context
- Model files: `/home/pmello/models/qwen3.5-122b-a10b-q5/` (3 GGUF shards)
- 35B kept as fallback: `/home/pmello/models/qwen3.5-35b-a3b-q8/`
- Swap script: `swap-model 122b` / `swap-model 35b` / `swap-model status`
- Model Registry: `/home/pmello/models/MODEL_REGISTRY.md`
- Model Supervisor: port 18090, `/home/pmello/models/supervisor/model-supervisor.py`
- Supervisor has: swap with rollback, context watchdog, rescue via 0.8b validation, HTTP API
- jess-q35.service + watchdog DISABLED (renamed .disabled) — needs update to point at 122B
- **Load timeout must be 360s+** for 85GB model (180s caused first swap failure)

## Pat's Architecture Ideas (2026-03-07)
- **Parallel small-model swarm:** Spawn 30-50 instances of 0.8b to process data in parallel. One coordinator chunks the work, workers categorize/summarize with strict guardrails, results merge into vector DB.
- **Use case:** Fast processing of large YouTube videos, documents, memory — instead of one slow pass with a big model, distribute to many tiny ones
- **Model Lab must be user-facing:** Pat wants a ChatGPT-like interface (hub/27-model-lab) where he can pick any model and chat. Must allow images to be sent to any model (don't block, let it fail gracefully).

## Model Swap Lessons (2026-03-07)
- systemd `Restart=on-failure` + timer = persistent resurrection. Must disable both.
- Split GGUFs: point at shard 1, llama.cpp finds the rest
- Port conflicts during swap are the #1 failure mode
- A supervisor (not a model) must manage swaps — models can't restart themselves

## Known Reliability Issues (2026-03-05)
- Stats API (8091) keeps crash-looping (WorkingDirectory config issue)
- Need self-healing watchdog for all services
- Video Understanding needs better real-time progress updates (like Computer Use step display)
- Pat wants all services to be cohesive and self-healing

## Memory Concierge (2026-03-07)
- **Unified RAG store**: ~/.openclaw/arena/knowledge/rag.db (6,215 chunks, 101 MB)
- **Service**: port 8102 (memory-concierge.service)
- **Model**: qwen3.5:0.8b for summarization, nomic-embed-text for embeddings
- **Parallel workers**: 3x 0.8b via ThreadPoolExecutor for deep research (~10s)
- **Auto-indexer**: every 30min, indexes agent MEMORY.md/RESUME.md/LESSONS.md + daily notes + shared context
- **CLI**: `memquery` (~/bin/memquery)
- **API**: /query, /deep, /research, /ingest, /refresh, /hot/<agent>, /stats
- **Replaces**: old dgx-memory-agent (port 8101, disabled) + Research Lab RAG (kept for backward compat)
- **Key fix**: nomic-embed-text capitalized single-word bug (lowercase + search_query: prefix)
- **Key fix**: Jess memory-manager spam (500+ identical lines/day eating context)

### What feeds the store:
- Session transcripts (indexed by compound-v2 cron)
- Research Lab pipeline output (papers, analysis, reviews)
- Agent workspace files (auto-indexer every 30min)
- Arxiv paper ingestion (daily 6am cron)
- Manual ingest via API/CLI

### Deep Research Pipeline:
1. Coordinator 0.8b generates 3 search angles from question
2. Workers search in parallel (3 concurrent queries)
3. Workers summarize their chunk batches in parallel
4. Coordinator synthesizes partial summaries into final answer

## Simulation Environments (2026-03-10)

### Neural Lab (Browser-Based Sim)
- Port 8103, hub/31-neural-lab/
- Browser-based multi-agent sim with pymunk physics, Three.js 3D, RL training (SB3)
- 17 agents, 8 brain regions, world builder, first-person mode, model workshop
- v3.2: teams, screen recording, 27K+ episodes trained
- Python venv: ~/.openclaw/neural-lab-env/

### Isaac Lab (NVIDIA GPU Physics)
- Replicating OpenAI "Emergent Tool Use from Multi-Agent Autocurricula" (2019)
- Isaac Sim 5.1.0 + Isaac Lab 0.54.3 on DGX Spark ARM64
- Custom DirectMARLEnv: 2v2 hide-and-seek, 24m arena, 4 boxes, 2 ramps
- IPPO/MAPPO via SKRL, 256 parallel GPU envs, ~15-20 it/s
- Env: IsaacLab/source/isaaclab_tasks/.../direct/hide_and_seek/
- CLI: isaac-train, isaac-visual, isaac-stop, isaac-status (~/bin/)
- Dashboard: hub/32-isaac-training/ (port 8104 monitor API)
- VNC streaming: x11vnc (5900) + noVNC/websockify (6080)
- TensorBoard: port 6006
- Key: always use isaaclab.sh -p, never system python for Isaac

### Service Ports (updated)
| Service | Port |
|---------|------|
| Isaac Monitor | 8104 |
| noVNC | 6080 |
| VNC | 5900 |
| TensorBoard | 6006 |

### Next Steps for Isaac Lab
1. Complete 25M+ step training, evaluate emergent behaviors
2. MAPPO comparison run
3. Add partial observability + box-locking mechanic
4. Visual upgrade (humanoid USD meshes)
5. Scale to 512+ envs, record progression videos

## Memory Sidecar System (2026-03-11)
- **Two hooks** running on ALL agents:
  - `memory-prefetch` (before_prompt_build): Searches RAG, injects relevant context before model sees message
  - `memory-capture` (llm_output): Uses 0.8b to extract key facts after every response, writes to RAG
- Context is labeled: "🧠 Auto-Retrieved Context (Memory Sidecar)" so agents know it's system-injected
- Replaces the old `knowledge-rag-inject` hook (deleted)
- Every conversation is now automatically captured into RAG with timestamps + agent + model metadata
- Source type in RAG: `conversation-extract`, source path: `conversation/<agent>/<date>`
- Effectively gives all agents infinite conversational memory
- Pre-fetch: ~1-2s (RAG query), Post-capture: ~200-500ms async (0.8b extraction, non-blocking)
