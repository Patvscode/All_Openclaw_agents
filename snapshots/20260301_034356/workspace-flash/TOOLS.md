# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## ChatGPT Bridge (GPT-4 via Pat's subscription — FREE)
When local models can't handle something, use ChatGPT:
```bash
exec chatgpt-bridge ask "your question"
exec chatgpt-bridge code "coding task"
exec chatgpt-bridge status
```
- Runs headlessly, zero cost (uses Pat's Plus subscription)
- Use when: stuck, need better code, complex reasoning, debugging, second opinion
- Don't use for: simple tasks local models handle, anything with private data
- Full docs: /home/pmello/.openclaw/workspace-flash/tools/CHATGPT-BRIDGE.md

## Custom Tools (system-wide at /usr/local/bin/)
- `now` — ground-truth time awareness (time, logging, schedule validation)
- `chatgpt-bridge` — ChatGPT web automation (ask/code/status)
- `video-understand` — full video analysis pipeline (download + transcribe + vision)

## Video Understanding
```bash
exec video-understand "https://youtube.com/watch?v=..."
```
- Downloads via yt-dlp, transcribes via YouTube captions (or Whisper), analyzes frames via vision model
- Results saved to: /home/pmello/.openclaw/workspace-flash/knowledge/video-analyses/

## Why Separate?
Skills are shared. Your setup is yours.

---
Add whatever helps you do your job. This is your cheat sheet.
