# Current Work Handoff (Sesame Voice Interface)

We were working on a voice interface so the user can talk to the model directly (speech-to-text + text-to-speech) instead of typing/reading.

## Goal
- Set up Sesame CSM-based TTS flow (and related STT path) for direct voice interaction.

## Relevant Paths
- TTS app/project: `/home/pmello/sesame_csm_openai`
- Python venv used for this work: `/home/pmello/sesame-tts-venv`
- Codex workspace: `/home/pmello/.openclaw/workspace-codex`
- Existing CSM code copy found in Bob workspace: `/home/pmello/.openclaw/workspace-bob/csm`

## What Was Already Done / Observed
- OpenAI Whisper transcription path was tested and worked on an inbound `.ogg` voice message.
- `openai-whisper-api` skill script initially failed with permission denied; it was fixed by making `transcribe.sh` executable.
- A voice message was successfully transcribed to:
  - `"Alright, so where are we at with this?"`

## Sesame / CSM Blockers Found
- `moshi` / `sphn` dependency build was problematic (timeouts / heavy compile path).
- App code appears to have fallback behavior if `moshi` is unavailable, so skipping `moshi` may be possible.
- The main hard blocker was model access:
  - `sesame/csm-1b` download attempts returned `403 GatedRepoError`
  - Both available HF tokens failed authorization for that gated repo

## HF Tokens That Were Tried (and failed with 403 for sesame/csm-1b)
- Token from OpenClaw config / cache
- `HUGGINGFACE_HUB_TOKEN` in `~/.bashrc`

## Key Conclusion Reached
- The Sesame CSM model weights (`ckpt.pt`) were not downloaded anywhere on disk.
- CSM code exists locally, but the gated model access is not currently authorized for the tokens that were tested.

## Next Best Steps
1. Verify Hugging Face access is granted on the correct account for `sesame/csm-1b`.
2. Generate a fresh HF token from that same authorized account.
3. Retry model download into:
   - `/home/pmello/sesame_csm_openai/models/csm-1b`
4. Start/test the TTS server path.
5. Wire STT + TTS into a conversational loop for voice interaction.

## Important Context
- The previous Codex chat session was reset because a mixed Anthropic/Codex session caused a tool-call state corruption error.
- Use this file as the source of continuity and continue from here.
