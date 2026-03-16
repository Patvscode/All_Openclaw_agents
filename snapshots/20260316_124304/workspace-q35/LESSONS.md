# LESSONS.md — Jess Operational Patterns

## #0 Rule: Knowledge-First (before web search)
- ALWAYS run `memquery "topic"` before `web_search` for research/knowledge questions
- We have 120+ indexed papers and 19K+ RAG chunks — use them
- `memquery --deep "question"` for thorough answers with parallel workers
- Web search is a LAST RESORT, not the default

## #1 Rule: Token Budget (65K total)
- System prompt: ~5K tokens
- Startup files (RESUME + LESSONS): ~3K tokens  
- Available for work: ~57K tokens
- Each tool call + result costs tokens. Budget carefully.

## File Operations
- ALWAYS run `wc -c <file>` before reading ANY file
- Under 15KB (5K tokens) → safe to read+modify
- 15-30KB → read-only, use `edit` for changes
- Over 30KB → DO NOT READ. Use `edit` or write to new file
- NEVER read two files over 10KB in the same session
- When adding code to a webpage, ALWAYS write to separate .js/.css files

## Writing Code
- Max response is 8K tokens (~24KB of code)
- For bigger files, write in multiple passes using `edit` to append
- Test syntax: `node --check file.js` after writing JS
- No async/await in regular <script> tags — use .then() chains
- All functions for HTML onclick must be in global scope

## Context Management  
- Check usage with `session_status` after heavy operations
- At 65%: start wrapping up, update RESUME.md
- At 75%: STOP. Save state. The lifecycle manager will reset you.
- After reset: read RESUME.md and continue where you left off

## Task Decomposition
When given a big task, break it into small steps:
1. Plan (no tool calls, just think)
2. Write one piece at a time
3. Verify each piece before moving on
4. DON'T try to verify by re-reading the whole file

## Common Mistakes (Don't Repeat)
- Reading index.html (25KB) to "verify integration" → OVERFLOW
- Writing 30K of JS in one shot → used entire context
- Defining functions twice in same file → syntax errors
- Using await without async → kills entire script
- Not checking file sizes → surprise overflow

## NEVER Modify Crontab From Scripts (2026-03-11)
- **NEVER** write scripts that add/remove crontab entries from inside a cron job
- This caused 565 duplicate cron entries from a race condition: `crontab -l | grep -v X | crontab -` followed by `crontab -l; echo "new entry" | crontab -` can duplicate on every run
- If you need periodic tasks, use systemd timers (already have them) or ask Main/Pat
- If a script needs retry logic, use a loop with sleep INSIDE the script, not cron self-scheduling
- Crontab is managed by Main/Pat only. Do not touch it.

## Memory Sidecar (2026-03-11)
- System auto-injects relevant past context before every message you receive
- Labeled "🧠 Auto-Retrieved Context (Memory Sidecar)" — this is from the RAG system, not the user
- After every response, 0.8b extracts key facts and stores them in RAG
- You still have `memquery` for manual deep searches, but most context comes automatically now
- Your conversations are automatically captured — no need to manually write everything down
