---
name: sesame-voice-send
description: Generate and send local Sesame/Dia voice notes to chat. Use when local media path sending is blocked and you must deliver audio via message buffer/caption flow.
---

# Sesame Voice Send

1. Generate audio via local API:
   - `tools/sesame_generate.sh "<text>"`
   - Optional env: `VOICE`, `FORMAT` (`wav`/`mp3`), `OUT`, `API_BASE`.

2. If local file attachments are blocked, send with message `buffer` instead of `media`:
   - Base64-encode output file.
   - Use `message(action=send, buffer=<base64>, filename=<name>, mimeType=<type>, caption=<text>)`.

3. Prefer compact formats for buffer sends (`mp3` usually smaller than wav).

4. Validate delivery by confirming message tool success and notify user.
