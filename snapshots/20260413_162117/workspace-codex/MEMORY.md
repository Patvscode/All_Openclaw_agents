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

## MemPalace Sidecar (2026-04-12)
- Pat added MemPalace as an **additional memory feature** through MCP.
- Intended use is supplemental recall, not replacement of OpenClaw memory-core, dreaming, `memory_search`, or `memquery`.
- Correct usage pattern from MemPalace docs:
  - MCP search/status/list tools first
  - optional wake-up/context layer for lightweight critical facts
  - save hooks only as a later opt-in if recall quality is proven and duplicate/noise behavior is acceptable
- Treat raw/verbatim search as the reliable baseline. AAAK is experimental and should not be assumed as the default best mode.
- Operational rule: OpenClaw memory remains primary; MemPalace is a secondary recall lane for deeper conversation-history lookup.

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

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-03-12.md:82:103 -->
- - **Update:** Ensure the progress is updated in the `#projects` channel. ## Session Summary [10:01:22 ] (auto-generated) **Role:** Agent Assistant (Autonomy Loop) **Status:** Active Card: `card-6319c3` **Project:** Memory Ops Hub Integration **Date:** March 12, 2026, 9:49 AM **What was the agent working on?** Executed `/home/pmello/.openclaw/tools/codex_autonomy_loop.sh` to run the autonomy loop. Executed one concrete step on active card `card-6319c3`: verified the Memory Ops hub page (`http://127.0.0.1:8090/20-memory-ops`) in-browser against a fresh fallback/proof bundle. Confirmed the Runtime panel is rendering fresh fallback snapshot data and exposing live API probe failures clearly. Posted progress update to `#projects`. **Key decisions made:** 1. Identified the specific file and command to execute (`/home/pmello/.openclaw/tools/codex_autonomy_loop.sh`). 2. Determined the immediate next action based on the card history (verify UI path vs. post result). 3. Executed the verification step to ensure the Runtime panel is rendering fresh fallback data. 4. Posted the progress update to `#projects` to track the session. **What was completed vs. still in progress?** - **Completed:** Verified Memory Ops hub page in-browser; confirmed Runtime panel rendering fresh fallback snapshot data; posted progress to `#projects`. - **Still in progress:** Waiting for the next step from the card history to proceed with the verification. **The exact next step to continue:** [score=0.802 recalls=9 avg=0.442 source=memory/2026-03-12.md:82-103]
<!-- openclaw-memory-promotion:memory:memory/2026-02-23.md:24:33 -->
- Implemented OpenClaw usage snapshot logging (JSON preferred, text fallback), local Ollama activity + triage metadata logging, daily usage summary report generation, and idempotent cron installer (15m capture + nightly summary). Updated agent_ops README and agent-ops-orchestrator skill docs. Ran smoke tests for py_compile, snapshot/model logging, daily summary, and cron installer dry-run/idempotence via fake crontab. - Created `LEVERAGE_BACKLOG.md` with prioritized initiatives to reduce Codex spend while increasing capability/reliability, including scoring model, KPI set, and milestones. ## 2026-02-23T22:12:00-05:00 | agent_ops milestone A - tags: agent_ops,usage,triage,budget_router - note: | Implemented budget_router.py (70% policy target with threshold overrides), summarize_heavy_output.py, triage report summary-only mode, KPI block in usage_daily_summary.py, and nightly usage_cron_summary.sh router append. Updated agent_ops README + agent-ops-orchestrator skill docs. Ran smoke tests for router/summarizer/daily summary/triage summary-only/nightly summary append. - Added `/home/pmello/.openclaw/workspace-prime/BETA_POLICY.md` to enforce local-first Beta behavior, model routing order, 120B parent-check pattern, and conservative Codex escalation gates. [score=0.802 recalls=9 avg=0.441 source=memory/2026-02-23.md:24-33]

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-02-23.md:14:29 -->
- - Created `USAGE_LEDGER.md` in workspace-codex with recommended local models, benchmark timings, baseline usage snapshot from `session_status`, and ongoing tracking plan. - Expanded `USAGE_LEDGER.md` with recommended additional local models/tools and a routing policy for coding/reasoning/vision/embeddings. ## 2026-02-22T21:11:40-05:00 | Agent ops toolkit build - tags: agent-ops,tooling - note: | Implemented 5 scripts, added skill + operations plan, ran smoke tests. ## 2026-02-22T21:55:06-05:00 | agent_ops passive usage telemetry - tags: agent_ops,telemetry,openclaw,usage,cron - note: | Implemented OpenClaw usage snapshot logging (JSON preferred, text fallback), local Ollama activity + triage metadata logging, daily usage summary report generation, and idempotent cron installer (15m capture + nightly summary). Updated agent_ops README and agent-ops-orchestrator skill docs. Ran smoke tests for py_compile, snapshot/model logging, daily summary, and cron installer dry-run/idempotence via fake crontab. - Created `LEVERAGE_BACKLOG.md` with prioritized initiatives to reduce Codex spend while increasing capability/reliability, including scoring model, KPI set, and milestones. ## 2026-02-23T22:12:00-05:00 | agent_ops milestone A - tags: agent_ops,usage,triage,budget_router - note: | [score=0.809 recalls=8 avg=0.447 source=memory/2026-02-23.md:14-29]
<!-- openclaw-memory-promotion:memory:memory/2026-02-22.md:47:64 -->
- latest_budget_hint=remaining=12% ## 2026-02-22T22:10:50-05:00 | Agent ops triage - tags: agent-ops,triage,routing - note: | triage_report=/home/pmello/.openclaw/workspace-codex/reports/agent_ops/triage_MILESTONEA_SMOKE.md status=ok requested_mode=normal recommended_mode=normal routing_policy=balanced-local-routing failure_path=tools/agent_ops failure_hours=2 failure_limit=3 device_rc=0 failure_rc=0 ollama_rc=0 latest_budget_hint=none report_summary_only=1 [score=0.806 recalls=12 avg=0.424 source=memory/2026-02-22.md:47-64]

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-03-07.md:26:40 -->
- * Ran `comms unread` to identify the stale DM from `main_q35`. * Read `#health` (canary at 18:30) and `#ops`. * Posted status update in `#projects` confirming triage completion. * Sent DM to `main_q35` confirming triage complete and requesting priority task. * Sent DM to `read_q35` confirming benchmark-validation support. * Posted health acknowledgment in `#health` noting no anomalies. * **Still in Progress:** * Resolving the stale unread behavior in `#health` and DM `main_q35` (requires manual intervention or new task). **4. Next Step to Continue** * **Immediate Action:** Post health acknowledgment in `#health` confirming triage completion and no anomalies. * **Follow-up:** Send DM to `main_q35` confirming triage complete and explicitly requesting priority task. * **Secondary Action:** Send DM to `read_q35` confirming benchmark-validation support once artifacts are posted. * **Long-term:** Monitor `#ops` for the recurring `workspace-research missing` failure. If resolved, re-enable `comms unread` for `#ops` and `#projects`. [score=0.801 recalls=5 avg=0.443 source=memory/2026-03-07.md:26-40]

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-03-12.md:99:116 -->
- **What was completed vs. still in progress?** - **Completed:** Verified Memory Ops hub page in-browser; confirmed Runtime panel rendering fresh fallback snapshot data; posted progress to `#projects`. - **Still in progress:** Waiting for the next step from the card history to proceed with the verification. **The exact next step to continue:** Execute one concrete step on active card `card-6319c3` to verify the Memory Ops hub page in-browser against the fresh fallback/proof bundle. ## Session Summary [14:00:32 ] (auto-generated) **Agent Name:** OpenCLaw Agent (P M) **Role:** Content Analysis & Deep Research Architect **Session ID:** 1409 **Status:** Active ### **1. What was the agent working on?** The agent was tasked with diagnosing and analyzing the **Perception Engine** architecture, specifically focusing on how it handles content ingestion, orchestration, and synthesis. Key tasks included: * **Header Analysis:** Investigating the `U:` (unread), `D:` (drift), and `C:43%` (cost/cached) statuslines injected into outgoing messages to identify potential security or formatting issues. * **File Discovery:** Locating the core backend logic, including `youtube-understand/server.py`, `content_swarm.py`, and the service definition (`dgx-youtube-understand.service`). * **Architecture Reconstruction:** Mapping the existing codebase to the described "stacked layers" model (Standard Perception vs. Deep Research Coordinator). [score=0.801 recalls=5 avg=0.442 source=memory/2026-03-12.md:99-116]

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-03-03.md:1:24 -->
- ## 2026-03-03 02:44 EST — Durable memory flush ### Jess runtime / reliability - Confirmed and switched Jess back to GPU-backed llama.cpp runtime (`build-cuda`) with `--n-gpu-layers 999`; verified active GPU attachment via `nvidia-smi` and runtime health endpoint. - Identified real overflow root cause from logs: repeated requests above context limit (e.g., ~68k–70k tokens vs ctx 65536), producing 400 errors. - Applied live mitigation: - increased Jess service context from `65536` to `98304` in `~/.config/systemd/user/jess-q35.service`, - updated OpenClaw q35cpp model contextWindow to `98304` in `~/.openclaw/openclaw.json`, - restarted service and validated health/chat recovery (`/health` 200, chat 200). - Note: warm-up returned temporary 503 while loading model after restart; recovered to healthy. ### Agent Comms / board reliability - Fixed channel routing bug in comms backend (`/api/post`) so payloads using `channel` route correctly (not just `target`). - Migrated/cleaned health canary noise from `#general` into `#health`; routing now lands in health channel. - Mobile board/UI stabilization done across multiple patches: - board panel blocking fixes, - board button + loading fallback, - discuss-thread handlers bound globally, - thread body rendering fix (`body` field display), - mention chips UI added in card thread composer. - Important caveat: @mention chips are UI-only for now (no guaranteed nudge pipeline trigger unless explicitly wired). ### Governance / execution discipline [score=0.805 recalls=7 avg=0.435 source=memory/2026-03-03.md:1-24]

## Promoted From Short-Term Memory (2026-04-10)

<!-- openclaw-memory-promotion:memory:memory/2026-04-08.md:1:8 -->
- - Pat asked for OpenClaw current state, agent inventory, update status, Gemma remote access debugging, and what changed in OpenClaw 2026.4.9. - OpenClaw was updated from 2026.4.5 to 2026.4.8 during this session; 2026.4.9 was available but not installed. - Gemma Interaction Hub outage root cause: frontend on :5174 and backend on :8000 were both down, while Gemma model servers on :18080/:18081 were healthy but localhost-only. Restarting frontend/backend on 0.0.0.0 restored phone access via Tailscale. - Created durable guidance to prevent repeat remote-app false positives: new skill `skills/remote-app-builder/` with checklist and `scripts/check_remote_app.sh`; also copied that skill into workspace-gemma and updated Gemma guidance files. - Improved `/home/pmello/foundry/gemma-interaction-hub/frontend/src/App.tsx` to avoid hardcoded Tailscale websocket host and use runtime/env-derived host logic instead. - Commit created in workspace-codex: `3ae9e5a` with message `Add remote app builder skill for phone-facing apps`. - Verified/presented OpenClaw 2026.4.9 release themes: memory/dreaming upgrades, control UI diary view, character-vibes eval reports, provider auth aliasing, iOS release pinning, plus many security, routing, packaging, NO_REPLY leakage, and provider/runtime fixes. [score=0.812 recalls=6 avg=0.450 source=memory/2026-04-08.md:1-8]
