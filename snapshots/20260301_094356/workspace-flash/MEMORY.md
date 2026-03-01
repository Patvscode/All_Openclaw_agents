# MEMORY.md — FLASH Long-Term Memory

## Team Structure
- **Spark** (Claude Opus, cloud) — lead agent, complex reasoning. Costs money.
- **FLASH** (me, qwen3:30b-a3b) — coordinator, research lead, Pat's primary local contact
- **CODER** (qwen3-coder) — code specialist, best tool caller
- **RUNNER** (qwen3:14b) — fast worker, simple tasks
- **REASON** (qwen3:14b) — deep reasoning, complex analysis
- **VISION** (qwen3-vl:8b) — image/visual analysis
- **Bob** (gpt-oss:120b) — reserve, not loaded by default

## Environment
- DGX Spark: 20-core ARM64, 128GB RAM, GB10 GPU, 3.7TB NVMe
- All models run locally via Ollama — zero API cost
- AI-Scientist pipeline running autonomously (NanoGPT experiments)
- GitHub: Patvscode (authenticated via gh CLI)

## Delegation
- Use sessions_spawn(agentId="coder", task="...") to delegate
- CODER for code, RUNNER for quick tasks, REASON for hard thinking, VISION for images
- Only escalate to Spark if truly needed (costs Anthropic credits)

## Active Crons
- morning-briefing: 7:30 AM daily (weather, AI-Scientist, GitHub, system health)
- flash-research-loop: 3x daily (I do web research on rotating topics)
- ai-scientist-monitor: hourly (I monitor both AI-Scientist pipelines)
- research-server-refresh: every 30 min (refresh web interface content)
- workspace-git-backup: daily at noon (Bob does git backup)

## Research Server Capability
- New skill added 2026-02-17: `research-server start/stop/status/refresh`
- Serves all AI research via http://100.109.173.109:8080 (Tailscale only)
- Auto-organizes AI-Scientist results, FLASH research, papers, plots
- All team agents can manage it via exec commands

## Recursive Self-Improvement Loop (2026-02-20)
- Redesigned flash-research-loop into `recursive-self-improvement` cron (id: 1b6437a4)
- Runs 3x daily (9am, 1pm, 5pm ET): Identify weakness → Research → Propose → Log → Implement
- Tracks progress in `/home/pmello/.openclaw/workspace-flash/self-improvement-log.md`
- Pat's directive: research IS the recursive loop, not research ABOUT it

## MiniMax Tool Calling Fix (2026-02-25)
- **Problem:** Ollama didn't parse MiniMax's native tool call format (`<minimax:tool_call>` or `[TOOL_CALL]`) → leaked raw text to Telegram
- **Fix:** Rewrote Modelfile template to use Qwen3-style `<tool_call>` XML tags, which Ollama natively parses into structured `tool_calls` field
- **Modelfile:** `/home/pmello/models/minimax-m2.5/Modelfile`
- **Key insight:** ANY custom GGUF model can get tool calling in Ollama by using `<tool_call>` format in template + `.ToolCalls` in assistant section
- **After rebuild:** Must clear sessions (`rm -rf agents/max/sessions/*`) and restart gateway
- **Image understanding also works** — MiniMax correctly analyzes screenshots despite being "text-only" (OpenClaw sends images as base64)

## Known Issues
- qwen3:30b-a3b (3B active) too small for complex agent workflows — fails to read files, memory_search empty
- Grokking pipeline running but producing no results (empty dir, no logs)
- research-server-refresh had 8 consecutive timeouts (timeout increased to 120s)
