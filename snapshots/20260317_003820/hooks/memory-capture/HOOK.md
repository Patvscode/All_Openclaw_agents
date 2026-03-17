---
name: memory-capture
description: "Real-time memory capture — extracts key facts from every exchange into RAG"
metadata:
  {
    "openclaw": {
      "emoji": "📝",
      "events": ["llm_output"]
    }
  }
---

# Memory Capture

After every assistant response, uses 0.8b to extract key facts, decisions,
and preferences, then writes them to RAG with timestamps. Runs async — 
zero delay to the user. Every conversation becomes searchable memory.
