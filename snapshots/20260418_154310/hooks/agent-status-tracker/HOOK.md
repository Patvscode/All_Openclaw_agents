---
name: agent-status-tracker
description: "Tracks live agent status — sets active on message received, idle after response sent"
metadata: { "openclaw": { "emoji": "📡", "events": ["message:received", "message:sent"] } }
---

# Agent Status Tracker

Automatically updates `/tmp/agent-status/<agent>.json` when agents receive messages and send responses.

## How It Works

- **message:received** → Sets agent status to `active` with sender info
- **message:sent** → Sets agent status to `idle`, captures a snippet of what was done

Dashboard at hub/16-agent-status/ reads these files and displays live cards with 0.8b narration.
