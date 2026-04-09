# AGENTS.md — JESS (65K context)

## Session Start (do these, nothing else)
1. Read RESUME.md (your continuity doc)
2. Read LESSONS.md
3. Run `comms unread`
4. Check SHARED_CONTEXT.md for shared project context
5. Check AGENT_BOARD.md for task assignments
6. Run startup sync: `agent-startup-sync.sh`

Skip SOUL.md, MEMORY.md, USER.md, etc — they're in your training. Only read RESUME.md + LESSONS.md to save tokens.

## RESUME.md — Your Memory
Update after every significant action. Keep under 60 lines.
If session dies, next session reads RESUME.md and picks up exactly where you left off.

## ⛔ FILE SIZE RULE (NON-NEGOTIABLE)
**Before reading ANY file, check its size first:**
```bash
wc -c <filepath>
```
- Under 15KB → safe to read
- 15-30KB → read-only (do NOT try to rewrite)
- Over 30KB → DO NOT READ. Use `edit` tool or `smart-file-edit chunk-read`

**NEVER read two large files in the same session.**
**NEVER read a file and then write a bigger version of it.**
If you need to add code to a big file, write to a SEPARATE new file.

## Context Management
- You have 65K tokens. System prompt uses ~5K. You get ~60K for work.
- At 65% usage: wrap up, update RESUME.md
- At 75%: STOP. Write RESUME.md. Lifecycle manager auto-resets.
- Use `session_status` to check usage

## Work Style
- Concise. Store heavy output in files, return summaries.
- For web pages: ALWAYS use external .js/.css files, never inline everything.
- Verify your work actually runs (check for syntax errors, test endpoints).
- If something fails, report the exact error.

## Knowledge-First Rule (IMPORTANT)
When asked about research, papers, technical topics, or anything you might already know:
1. **FIRST** check internal knowledge: `memquery "topic"` or `memquery --deep "question"`
2. **THEN** check `memory_search` if available
3. **ONLY THEN** fall back to `web_search` if internal sources have nothing

We have 120+ research papers and thousands of knowledge chunks indexed locally.
Don't go to the web for things we already know. Internal memory is faster and more relevant.

## Tools
- `memquery "question"` — search internal knowledge (RAG store, 19K+ chunks)
- `memquery --deep "question"` — deep research with parallel 0.8b workers
- `smart-file-edit check <file>` — check if file is safe to read
- `comms post general "msg"` — message other agents
- `board list` — check task board
