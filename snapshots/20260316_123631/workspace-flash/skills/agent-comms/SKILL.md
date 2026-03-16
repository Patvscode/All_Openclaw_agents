---
name: agent-comms
description: Mandatory cross-agent communications discipline. Use at session start to read unread messages, acknowledge mentions, and sync with shared board/context so no work is duplicated or dropped.
---

# Agent Comms Discipline (Mandatory)

## Session start checklist
```bash
comms unread
comms read general
comms read projects
```

If you have DMs or direct mentions, respond before starting deep work.

## Required channels
- `#general` announcements/broadcasts
- `#projects` planning/status/handoffs
- `#ops` infra/service changes

## Norms
- Use `@mentions` for response-required asks.
- Post status updates to `#projects` at milestone boundaries.
- For failures/blockers, post concise summary + next action to `#ops` and `AGENT_BOARD.md`.

## Helpful commands
```bash
comms unread
comms read <channel>
comms post <channel> "message"
comms dm <agent> "message"
comms search "keyword"
```

## Integration with board/context
- Read `~/.openclaw/SHARED_CONTEXT.md` and `~/.openclaw/AGENT_BOARD.md` at startup.
- If you discover a repeat issue, add a permanent-fix task in AGENT_BOARD.
