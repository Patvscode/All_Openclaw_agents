---
name: gemma-auto-continue
description: "Auto-continue hook — reads Gemma's SCRATCHPAD.md after each turn and triggers continuation if needed"
metadata:
  {
    "openclaw": {
      "emoji": "🔄",
      "events": ["message:sent"]
    }
  }
---

# Gemma Auto-Continue

After every Gemma agent message is sent, reads SCRATCHPAD.md to check if the 
agent decided it needs to continue working. If the scratchpad Decision section
says to continue, automatically triggers the next agent turn.

## How It Works

1. Fires on `message:sent` (after assistant response delivered)
2. Only activates for agent `gemma` sessions
3. Reads `SCRATCHPAD.md` from Gemma's workspace
4. Parses the `## Decision` section
5. If it says "continue" → sends a follow-up message via `openclaw agent`
6. If it says "done" or "no" → does nothing
