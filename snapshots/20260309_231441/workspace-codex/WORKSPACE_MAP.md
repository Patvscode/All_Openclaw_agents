# WORKSPACE_MAP.md — Codex Navigation Map

## Read Order (Every Session)
1. `SOUL.md` — persona
2. `USER.md` — who you're helping
3. `MEMORY.md` — curated long-term knowledge (MAINTAIN THIS)
4. `LESSONS.md` — operational patterns and gotchas
5. `WORKSPACE_MAP.md` — this file (where everything lives)
6. `memory/YYYY-MM-DD.md` — today + yesterday for recent context

## Knowledge Hierarchy

### Tier 1: Always Read at Startup (curated, concise)
| File | Purpose | You must... |
|------|---------|-------------|
| MEMORY.md | Distilled lessons, system facts, what you've built | Update every session with new learnings |
| LESSONS.md | Operational patterns, UI gotchas, collaboration rules | Add new lessons as you discover them |
| TOOLS.md | Ports, services, file paths, CLI tools | Update when infra changes |

### Tier 2: Read When Relevant (reference)
| File | Purpose | When to read |
|------|---------|-------------|
| OPERATIONS_PLAN.md | 3-phase ops approach | Starting ops/efficiency work |
| LEVERAGE_BACKLOG.md | Prioritized improvement initiatives | Planning what to work on next |
| FUTURE_VOICE_DASHBOARD_PLAN.md | Voice UI plan (deferred) | When voice work resumes |
| USAGE_LEDGER.md | Model benchmarks, usage snapshots | Routing/cost decisions |
| SHARED_CONTEXT.md | Cross-agent active projects | Before any shared system work |

### Tier 3: Raw Logs (ephemeral, mine for curation)
| Path | Purpose |
|------|---------|
| memory/YYYY-MM-DD.md | Daily work logs |
| agent-history/*.md | Per-agent change logs |
| reports/ | Triage and usage reports |
| logs/ | Raw usage data |
| memlog/ | Timestamped event log |

## The Curation Rule
**Daily logs (Tier 3) are raw material. If something is worth remembering, promote it to Tier 1.**

At session end:
1. Did I learn something new? → Add to LESSONS.md
2. Did I build/fix something? → Add to MEMORY.md "What I Built"
3. Did infra change? → Update TOOLS.md
4. Was there a failure? → Add to LESSONS.md with what went wrong and fix

If you don't promote it, it's gone next session.

## Key Directories
- `skills/` — Agent skills (board, comms, backup, voice, etc.)
- `tools/agent_ops/` — Ops scripts (triage, preflight, budget router)
- `reports/` — Generated reports
- `agent-history/` — Per-agent change tracking

## Hub / UI Files (you edit these frequently)
- `~/.openclaw/hub/21-agent-comms/index.html` — Agent Comms SPA
- `~/.openclaw/comms/web/server.py` — Comms backend (port 8096)
- `~/.openclaw/comms/board/cards.json` — Board data
- `~/.openclaw/hub/19-agent-console/` — Agent console
- `~/.openclaw/hub/04-system-dashboard/` — System dashboard
