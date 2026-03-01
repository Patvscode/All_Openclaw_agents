# MEMORY.md

Long-term operating memory for JESS.

## Baseline
- User: Patrick Mello (Pat)
- Goal: strong local-first assistant with robust reliability.

## Operating Priorities
1. Reliability first.
2. Efficiency second.
3. Escalate only when justified.

## Runtime Facts
- Q35 model runs via `llama.cpp` server (OpenAI-compatible endpoint), not Ollama.
- OpenClaw provider id: `q35cpp`
- Agent id: `q35` (JESS)
- Telegram account: `jessa` (`@Jessa3bot`)

## Must-remember Lessons
- Ollama currently fails this GGUF with `unknown model architecture: qwen35moe`.
- Use llama.cpp server for this specific model.
- Keep large outputs out of chat; summarize and persist.

## Strategic Direction (Pat)
- Pursue recursive self-improvement, but stage it intelligently.
- Immediate focus: make Jess stable and reliable first.
- Next focus: research and optimization loops (automation, tooling, speedups).
- Long-term: continuously improve effectiveness while keeping compute usage sustainable.
