# TOOLS.md — JESS Local Notes

## Key Paths
- OpenClaw config: `~/.openclaw/openclaw.json`
- Jess workspace: `~/.openclaw/workspace-q35`
- Q35 model files: `/home/pmello/models/qwen3.5-35b-a3b-q8/`
- llama.cpp build: `/home/pmello/llama.cpp-q35/build-cpu/bin/`

## Key Commands
- OpenClaw health: `openclaw status --deep`
- Jess model quick test:
  - `curl -s http://127.0.0.1:18080/health`
  - `curl -s http://127.0.0.1:18080/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"qwen3.5-35b-a3b-q8","messages":[{"role":"user","content":"hi"}],"max_tokens":24}'`
- Ollama load view (for co-running): `ollama ps`

## Compute Guardrails
- Don't run multiple heavy local models at once unless explicitly needed.
- Prefer sequential heavy tasks under load.
- If latency spikes, reduce concurrency and summarize outputs.

## 🎙️ Voice — Local TTS & STT

You have a voice named after you! Pat picked it specifically.

### Your Voice (the "jess" voice)
- Warm female, smooth delivery, slightly pitched down
- Settings: temp 1.0, topk 15, with post-processing for warmth
- **This is Pat's preferred voice.** Use it when sending voice messages.

### Quick Usage
```bash
# Send a voice message (your voice)
MP3=$(voice say "Your text here" --send)
# Then: message(action=send, media=$MP3, asVoice=true)

# Transcribe an inbound voice message
TEXT=$(voice hear /path/to/audio.ogg)

# Check current voice preferences
voice prefs
```

### Pat's Preferences
Stored in `~/.openclaw/voice-prefs.json`. Currently set to the "jess" voice.
**If Pat asks you to change the default voice, update that file.**
You can do it with: `voice prefer <voice_name> --temp <N>`

### Available Voices
Run `voice voices` to see all options. But unless Pat asks otherwise, always use `--voice jess`.

### Full Docs
See `skills/local-voice/SKILL.md` for complete reference including all parameters, voice cloning, and troubleshooting.


## Universal Backup
- Run backup anytime: `backup-now`
- Full script: `/home/pmello/.openclaw/tools/agents_backup_sync.sh`
