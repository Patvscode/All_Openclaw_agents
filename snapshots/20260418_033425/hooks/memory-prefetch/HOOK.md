---
name: memory-prefetch
description: "Pre-fetch relevant context from RAG before every prompt — infinite memory window"
metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "events": ["before_prompt_build"]
    }
  }
---

# Memory Pre-Fetch

Searches RAG for relevant context before the model sees the message.
Replaces knowledge-rag-inject with conversation-aware retrieval.
