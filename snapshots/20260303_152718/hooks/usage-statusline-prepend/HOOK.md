---
name: usage-statusline-prepend
description: "Prepend a tiny cached usage statusline to outbound assistant messages"
metadata:
  {
    "openclaw": {
      "emoji": "📊",
      "events": ["message_sending"]
    }
  }
---

# Usage Statusline Prepend

Prepends a short cached usage header (window/day/context/mode) to outbound messages.

Format:
`[U W:<window> D:<day> C:<ctx%> M:<mode>]`

Data source is passive telemetry under `~/.openclaw/workspace-codex/logs/usage/openclaw_status.jsonl`.
