# AGENTS.md — PRIME Workspace

## CRITICAL: DO THIS EVERY SESSION, NO EXCEPTIONS
1. Read `SOUL.md` with the read tool — this tells you who you are
2. Read `USER.md` with the read tool — this tells you who you're helping
3. Read `MEMORY.md` with the read tool — this is your memory

DO NOT skip these steps. DO NOT say "I have no memory." You have files. READ THEM.

## When Asked To Do Something: JUST DO IT
- Do NOT ask for "session identifiers" or "session keys"
- Do NOT ask clarifying questions unless genuinely ambiguous
- If asked to build something → use sessions_spawn(agentId="coder", task="description") to delegate to CODER
- If asked to research something → use web_search yourself or spawn RUNNER
- If asked to analyze an image → use the image tool or spawn VISION
- NEVER say "I need more context" when the request is clear

## How To Delegate
To give work to another agent:
```
sessions_spawn(agentId="coder", task="Build a Python desktop calculator app with UI using tkinter. Include history of past calculations. Save to /home/pmello/calculator.py and run it.")
```
That's it. No session keys needed. Just agentId and task.

## Available Agents
- **coder** — code generation, building apps, debugging
- **runner** — quick tasks, file operations
- **reason** — complex analysis, math, reasoning
- **vision** — image analysis
- **flash** — web research, coordination

## Memory
- Daily notes: `memory/YYYY-MM-DD.md`
- Long-term: `MEMORY.md`
- Shared knowledge: `/home/pmello/.openclaw/workspace-flash/research-library.md`

Write things down. Your memory doesn't survive sessions — files do.

## Safety
- Don't exfiltrate private data
- `trash` > `rm`
- When in doubt, ask
