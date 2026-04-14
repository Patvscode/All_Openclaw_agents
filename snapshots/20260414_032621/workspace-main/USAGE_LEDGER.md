# USAGE_LEDGER.md

Tracks model recommendations + usage snapshots for this OpenClaw/CODEX session.

## Preferred Local Models (Current)

- **Primary coding worker:** `qwen3-coder:latest`
- **Reasoning backup:** `gpt-oss:20b`
- **Deep-think fallback (slower):** `qwen3:30b-a3b`
- **Vision tasks:** `qwen3-vl:8b`
- **Embeddings/RAG:** `nomic-embed-text:latest`

## Quick Local Speed Check (2026-02-22 20:55 EST)

Prompt: `Return only one Python function named fib(n) using iteration.`

- `qwen3-coder:latest` → 16.4s
- `gpt-oss:20b` → 30.6s
- `qwen3:30b-a3b` → 57.4s

## Usage Snapshots

### 2026-02-22 20:56 EST
Source: `session_status`

- Model: `openai-codex/gpt-5.3-codex`
- Tokens: **61k in / 1.6k out**
- Context: **33k/200k (17%)**
- Window usage left: **41m**
- Day usage left: **4d 13h**

---

## Tracking Plan

- Log a snapshot at major milestones (build complete, tests complete, deploy step).
- If requested, provide periodic deltas (e.g., every 30–60 min):
  - tokens in/out delta
  - context growth
  - remaining usage window/day

## Recommended Additions (Next Pull/Install)

### Local Models to Add

- **`qwen3-coder:32b`** (if available in your Ollama registry)
  - Use for harder refactors/architectural coding where 14B/30B quality is borderline.
- **`deepseek-r1:32b`** (or nearest available larger R1)
  - Better chain-of-thought style planning/debugging; slower but strong for complex analysis.
- **`mistral-small:latest`** (or equivalent ~24B instruction model)
  - Fast, strong general-purpose fallback with good tool-use compliance.
- **`bge-m3` embedding model** (if offered in your local stack)
  - Strong multilingual retrieval over `nomic-embed-text` in mixed corpora.

### Tooling to Add

- **`ollama ps` + lightweight benchmark script**
  - Track active model memory footprint + latency trends.
- **`vllm` server (optional)**
  - Better throughput for concurrent local agent workers.
- **`llama.cpp` server (optional)**
  - Efficient CPU/GPU mixed inference and easy OpenAI-compatible endpoints.
- **`open-webui` (optional)**
  - Fast manual triage/testing UI for model quality checks.

### Suggested Routing Policy

- **Coding default:** `qwen3-coder:latest`
- **Fast reasoning/chat:** `gpt-oss:20b`
- **Deep reasoning (slow):** `qwen3:30b-a3b`
- **Vision:** `qwen3-vl:8b`
- **Embeddings:** `nomic-embed-text:latest`
- **Fallback when primary fails:** `qwen3:14b`
