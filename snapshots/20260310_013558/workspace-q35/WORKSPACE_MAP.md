# WORKSPACE_MAP.md — Jess Navigation Map

## Read Order (Every Session)
1. `SOUL.md` — persona
2. `USER.md` — who you're helping
3. `MEMORY.md` — curated long-term knowledge (MAINTAIN THIS)
4. `LESSONS.md` — operational patterns and what you've learned
5. `WORKSPACE_MAP.md` — this file
6. `memory/YYYY-MM-DD.md` — today + yesterday

## Knowledge Hierarchy

### Tier 1: Always Read at Startup (curated, concise)
| File | Purpose | You must... |
|------|---------|-------------|
| MEMORY.md | Your long-term memory — facts, lessons, what works | Update every session |
| LESSONS.md | Patterns, mistakes, things that work | Add new lessons when you learn them |
| TOOLS.md | CLI commands, ports, services available to you | Update when things change |

### Tier 2: Read When Relevant
| File | Purpose | When |
|------|---------|------|
| RUNTIME.md | Your runtime status/health | Diagnosing issues |
| DIAGNOSTICS.md | Past diagnostic findings | Troubleshooting |
| SHARED_CONTEXT.md | Cross-agent project state | Before shared work |
| JESS_SETUP.md | Your setup/config details | Reference |

### Tier 3: Raw Logs (ephemeral)
| Path | Purpose |
|------|---------|
| memory/YYYY-MM-DD.md | Daily work logs |
| state/ | Runtime state files (auto-managed) |
| logs/ | Raw logs |
| memlog/ | Timestamped events |

## The Curation Rule
**If something matters, move it from Tier 3 → Tier 1.**

At session end, ask yourself:
1. Did I learn something? → LESSONS.md
2. Did I do something worth remembering? → MEMORY.md
3. Did a tool/service change? → TOOLS.md

If you don't write it down, you won't remember it.

## Key Commands
- `comms unread` — check messages
- `board list` — check task board
- `comms post general "msg"` — post to channel
- `board grab <id>` — claim a task
- `board done <id>` — complete a task
