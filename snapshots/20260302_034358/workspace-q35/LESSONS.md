# LESSONS.md — Jess Operational Lessons

## Runtime
- Ollama can't run this model (`qwen35moe` architecture error) — use llama.cpp
- llama.cpp server runs on port 18080, provider id: q35cpp
- Context window: 65k tokens — be mindful, summarize when getting full
- Watchdog checks health every 2 min, memory manager runs every 2 min

## Communication
- Keep heavy outputs in files; summarize in chat
- When posting to Agent Comms, be concise
- Check `comms unread` at session start — always
- Reply to DMs directed at you
- Comms messages stay in comms — never reply via Telegram

## Task Board
- Check `board list` at session start
- When you grab a card, work on it — don't hoard
- Use `board discuss <id> "msg"` to document what you're doing
- When done: `board done <id>` with a summary of what you did
- If stuck: `board blocked <id> "reason"` — this notifies other agents

## Collaboration
- Ask for help via @mentions in comms when stuck — don't spin
- Codex and Main can help with things outside your capabilities
- Document what you learn so you don't need to ask again

## Memory Discipline
- At session end, promote important learnings from daily logs → MEMORY.md or LESSONS.md
- If you don't write it down, you won't remember it next session
- MEMORY.md = curated wisdom. Daily files = raw notes.

## Reliability
- Always verify system state with live checks before asserting
- One robust attempt > many noisy retries
- Under high load, reduce concurrent work and batch tasks
- Verify end-to-end: runtime health → API response → Telegram reply
