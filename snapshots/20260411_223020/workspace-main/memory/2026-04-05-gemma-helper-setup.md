# Session: 2026-04-05 17:19:21 UTC

- **Session Key**: agent:main:main
- **Session ID**: 090401c7-a7f6-4f54-95d5-7f24106eace4
- **Source**: telegram

## Conversation Summary

assistant: 20GB free, E2B needs ~7GB. That works. Let me spin up a second llama-server for the small model and wire it into OpenClaw as a helper agent:
assistant: E2B is running on :18081. Now add it as a provider in OpenClaw and wire it as a helper agent:
assistant: Now check RAM after both models loaded:
assistant: Both running simultaneously. Now let me add the OC control sheet entry and restart the gateway:
assistant: Done. Here's what's set up now:

**Two Gemma models running concurrently:**

| Model | Port | RAM | Role |
|-------|------|-----|------|
| 26B-A4B MoE | :18080 | ~64GB | Primary (Gemma agent) |
| E2B | :18081 | ~7GB | Helper (subagent, always-on) |

**How Gemma can use the helper:**
- Gemma (26B) can spawn `gemma-helper` as a subagent for quick tasks — summarization, simple lookups, processing chunks
- The E2B helper runs on its own port so it's **always available** regardless of what's on :18080
- When you swap :18080 back to Jess/35B, the E2B helper stays up

**RAM:** 107GB used / 121GB — 14GB free. Tight but stable.

Want me to also set up E4B as a second helper on another port, or is E2B enough for now?
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "9229",
  "sender_id": "7827979987",
  "sender": "P M",
  "timestamp": "Sun 2026-04-05 02:46 EDT"
}
```

Sender (untrusted metadata):
```json
{
  "label": "P M (7827979987)",
  "id": "7827979987",
  "name": "P M"
}
```

So the other things you need to make sure that this fits into our proper structure in that it updates the oc control sheet fully in the proper formatting way to find the instructions for it. Take care of that and then make sure you have both of the models there 4b and 2b of Gemma
assistant: Good, now I understand the full system. Let me do this properly — add both E2B and E4B services, update the target, update the control sheet, and apply correctly:
assistant: Now update the control sheet properly — both services under `[models]`:
assistant: E4B starts as force-off (`=-`) since we're tight on RAM with the 26B loaded. Now update the target:
assistant: Now disable the independent auto-start (per the RUNBOOK — control sheet should manage, not systemd enable):
assistant: Now add E4B to OpenClaw config:
assistant: Now run drift check to verify:
assistant: Clean. Both Gemma helpers are tracked properly:
- **gemma-e2b.service** = `x` (ON) ✅ active
- **gemma-e4b.service** = `-` (force OFF) ✅ off

Only 1 drift issue and it's a pre-existing one (dgx-commands-api). Both new services are exactly where they should be.

Now update the ARCHITECTURE.md to document the new services:
assistant: Here's the full picture now:

**OC Control Sheet — `[models]` group:**
```
jess-q35.service=x        # Main model server (:18080)
model-control.service=-   # Force off
gemma-e2b.service=x       # Gemma E2B helper (:18081) — ON
gemma-e4b.service=-       # Gemma E4B helper (:18082) — OFF (RAM)
```

**Target updated**, **ARCHITECTURE.md updated**, **drift check passes**, **no independent auto-start** (control sheet manages).

To turn E4B on later: change `gemma-e4b.service=-` to `=x` in the control sheet and run `apply-control-sheet.py`. Right now E4B is off because the 26B + E2B already use 107GB of 121GB RAM — no room for the E4B's ~10GB until you swap the 26B for something smaller.
user: Conversation info (untrusted metadata):
```json
{
  "message_id": "9238",
  "sender_id": "7827979987",
  "sender": "P M",
  "timestamp": "Sun 2026-04-05 02:55 EDT"
}
```

Sender (untrusted metadata):
```json
{
  "label": "P M (7827979987)",
  "id": "7827979987",
  "name": "P M"
}
```

Great tell me about this https://github.com/Patvscode/claw-code
