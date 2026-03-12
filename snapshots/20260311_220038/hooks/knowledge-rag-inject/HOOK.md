---
name: knowledge-rag-inject
description: "Auto-inject relevant internal knowledge into agent context before prompt build"
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "events": ["before_prompt_build"]
    }
  }
---

# Knowledge RAG Inject

Automatically searches the internal RAG store (Memory Concierge, port 8102) on every inbound message
and injects relevant results into the agent's context via `prependContext`.

## How It Works

1. On `before_prompt_build`, extracts the user's prompt
2. Skips short/trivial messages, heartbeats, and system commands
3. Queries Memory Concierge `/query` endpoint (fast embedding search, ~100ms)
4. If results score above threshold (0.72), injects top snippets as context
5. Agent sees the knowledge naturally — no extra tool calls needed

## Design Principles
- **Fast**: Single HTTP call, ~100-200ms. No model inference.
- **Smart**: Only injects when results are actually relevant (score threshold)
- **Lean**: Max 3 snippets, ~800 chars each. Won't bloat context.
- **Silent**: No visible prefix. Just prepended context the model can use.
