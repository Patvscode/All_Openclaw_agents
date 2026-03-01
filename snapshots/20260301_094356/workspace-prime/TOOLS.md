# TOOLS.md — PRIME Local Notes

## ChatGPT Bridge (GPT-4 via Pat's subscription — FREE)
When local models can't handle something, escalate to ChatGPT:
```bash
exec chatgpt-bridge ask "your question"
exec chatgpt-bridge code "coding task"  
exec chatgpt-bridge status
```
- Runs headlessly, zero cost (uses Pat's Plus subscription)
- **Use when**: you're stuck, need better code, complex reasoning, debugging, need a second opinion
- **Don't use for**: simple tasks you can handle, anything with private data
- Each call = new conversation (no memory between calls)
- Full docs: /home/pmello/.openclaw/workspace-flash/tools/CHATGPT-BRIDGE.md

### Example — Escalating when stuck:
```
# You tried to solve something but local model output was bad
exec chatgpt-bridge ask "I'm trying to implement X but getting Y error. Here's my code: [paste]. What's wrong?"
```

### Example — Getting code:
```
exec chatgpt-bridge code "Build a Python Flask REST API with SQLite backend for a todo app. Include CRUD endpoints and error handling."
```

## Custom Tools (system-wide)
- `now` — ground-truth time, logging, schedule validation
- `chatgpt-bridge` — ChatGPT web automation
- `video-understand` — video analysis pipeline

## Shared Resources
- Research library: /home/pmello/.openclaw/workspace-flash/research-library.md
- Knowledge base: /home/pmello/.openclaw/workspace-flash/knowledge/
- Self-improvement log: /home/pmello/.openclaw/workspace-flash/self-improvement-log.md
- FRIS architecture: /home/pmello/.openclaw/workspace-flash/FRIS-architecture.md


## Universal Backup
- Run backup anytime: `backup-now`
- Full script: `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
