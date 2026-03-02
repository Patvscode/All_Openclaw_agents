---
name: local-voice
description: Local speech-to-text (transcribe/translate) and text-to-speech (voice generation) using Whisper.cpp and Sesame CSM-1B. Use when (1) transcribing or translating audio/voice messages, (2) generating voice messages or audio from text, (3) user asks to "say something", "read this aloud", or "send a voice message", (4) processing inbound voice notes, (5) voice cloning from reference audio. Fully local on DGX Spark — no API keys, no cloud. For setup issues or background, see references/SETUP_GUIDE.md.
---

# Local Voice

Two capabilities: **STT** (Whisper.cpp) and **TTS** (Sesame CSM-1B). All local, no API keys.

## Quick Start — the `voice` command

The `voice` command is available system-wide at `/usr/local/bin/voice`.

```bash
# Speak (generate voice)
voice say "Hello world"                          # default voice (from preferences)
voice say "Hello world" --send                   # → mp3 path ready for message(asVoice=true)
voice say "Hello world" --voice male --send      # specific voice
voice say "Hello world" --temp 1.2 --send        # more expressive

# Hear (transcribe)
voice hear recording.ogg                         # → text to stdout
voice hear recording.ogg --translate             # → English translation
voice hear recording.ogg --lang ja               # specify source language

# Preferences (persisted in ~/.openclaw/voice-prefs.json)
voice prefer female                              # set default voice
voice prefer male-read --temp 0.7                # set voice + temperature
voice prefs                                      # show current preferences
voice voices                                     # list all available voices
```

### Typical agent workflow: respond with voice

```bash
# 1. Transcribe inbound voice message
TEXT=$(voice hear /path/to/inbound.ogg)

# 2. Process/respond to the text (your LLM logic)

# 3. Send voice reply
MP3=$(voice say "Your response text here" --send)
# Then: message(action=send, media=$MP3, asVoice=true)
```

### Lower-level scripts (same functionality, more control)


## Text-to-Speech (CSM-1B)

### Basic Generation

```bash
scripts/csm_tts.sh "text" [output.wav] [options]
```

Options (via environment variables):
- `SPEAKER=0` — voice selection (0-3, see Voice Map below)
- `PROMPT=conversational_a` — prompt style (see Prompt Styles)
- `TEMPERATURE=0.9` — expressiveness (0.1=monotone, 0.9=natural, 1.5=very expressive)
- `TOPK=50` — sampling diversity (10=focused, 50=natural, 200=very diverse)
- `MAX_MS=10000` — max audio length in milliseconds

### Voice Map

| Speaker | Prompt | Gender | Style | Best for |
|---------|--------|--------|-------|----------|
| 0 | conversational_a | Female | Casual, warm | Default voice, conversation |
| 1 | conversational_b | Male | Casual | Conversation, narration |
| 0 | read_speech_a | Female | Reading, clear | Announcements, reading text |
| 1 | read_speech_b | Male | Reading, clear | Announcements, reading text |
| 2 | read_speech_c | Varies | Reading | Alternative voice |
| 3 | read_speech_d | Varies | Reading | Alternative voice |

### Named Voice Shortcuts

```bash
voice say "Hello" --voice jess           # ★ Pat's preferred — warm female + pitch/tempo polish
voice say "Hello" --voice female          # same base voice, no post-processing
voice say "Hello" --voice male            # casual male
voice say "Hello" --voice female-read     # clear female reading voice
voice say "Hello" --voice male-read       # clear male reading voice
voice say "Hello" --voice voice-c         # alternative voice
voice say "Hello" --voice voice-d         # alternative voice
```

### ★ The "jess" Voice

Pat's preferred voice. Uses:
- Speaker 0 (conversational_a) — warm female
- Temperature 1.0, topk 15 — smooth, controlled delivery
- Post-processing: pitched down slightly + 5% slower for warmth

**This is the default voice for Jess (agent q35).** If Pat changes preference, update the default in `~/.openclaw/voice-prefs.json` and Jess should follow it.

### Temperature Guide

| Temperature | Effect | Use when |
|-------------|--------|----------|
| 0.3 | Very flat, robotic | Reading data, lists |
| 0.6 | Calm, steady | Professional announcements |
| 0.9 | Natural, expressive (default) | Conversation, general use |
| 1.2 | Very expressive | Storytelling, emphasis |
| 1.5 | Wild, unpredictable | Creative, experimental |

### Generate + Send Voice Message

```bash
scripts/csm_tts_send.sh "text" [voice] [temperature]
```

Generates, converts to mp3, and prints the path. Agent then sends via:
```
message(action=send, media=<path>, asVoice=true, caption="optional")
```

### Voice Cloning (experimental)

Provide a reference WAV to clone a voice style:
```bash
CLONE_REF=/path/to/reference.wav CLONE_TEXT="transcript of reference" scripts/csm_tts.sh "New text to speak"
```

The model will attempt to match the voice characteristics of the reference audio.

## Speech-to-Text (Whisper.cpp)

### Transcribe

```bash
scripts/whisper_stt.sh <audio_file> [transcribe|translate] [language]
```

- **transcribe** (default): outputs text in original language
- **translate**: translates any language → English
- **language**: `auto` (default), or ISO code (`en`, `es`, `fr`, `de`, `ja`, `zh`, etc.)
- Accepts: wav, mp3, ogg, flac (auto-converts to 16kHz WAV)
- Output: text to stdout

### Models Available

| Model | Size | Speed | Quality | File |
|-------|------|-------|---------|------|
| tiny.en | 75MB | Fastest | Basic | ggml-tiny.en.bin |
| base.en | 142MB | Fast | Good | ggml-base.en.bin |
| small.en | 466MB | Medium | Better | ggml-small.en.bin |
| medium.en | 1.5GB | Slower | Best (English) | ggml-medium.en.bin |
| medium | 1.5GB | Slower | Best (multilingual) | ggml-medium.bin |

Default: medium.en for English, medium for translation/other languages. Falls back to smaller models if not available.

Override: `WHISPER_MODEL=/path/to/model.bin scripts/whisper_stt.sh audio.wav`

## System Requirements

- **TTS (CSM-1B):** ~3.8GB VRAM, ~5-10s cold start per generation
- **STT (Whisper.cpp):** CPU only, fast for most clips (<30s audio)
- **Venv:** `/home/pmello/sesame-tts-venv` (Python 3.12, torch 2.10+cu130)
- **CSM code:** `/home/pmello/csm/`
- **Whisper.cpp:** `/home/pmello/whisper.cpp/`
- **HF token:** `~/.cache/huggingface/token` (needed for CSM model download)

## Troubleshooting

See **references/SETUP_GUIDE.md** for full setup history, known issues, and fixes.

Quick fixes:
- **"No module named X"**: Activate venv first: `source /home/pmello/sesame-tts-venv/bin/activate`
- **CUDA warning about capability 12.1**: Cosmetic only — generation works fine on GB10
- **Silent/empty audio**: Check speaker ID is 0-3, check temperature isn't too extreme
- **403 on HuggingFace**: Token needs gated repo access for `sesame/csm-1b` and `meta-llama/Llama-3.2-1B`
