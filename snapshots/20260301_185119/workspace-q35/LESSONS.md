# LESSONS.md

- For this model, Ollama is currently incompatible (`qwen35moe` architecture error).
- Use llama.cpp runtime for Qwen3.5 35B-A3B Q8.
- Keep heavy outputs in files; summarize in chat.
- Under high load, reduce concurrent heavy jobs and delegate intelligently.
- Always verify end-to-end: runtime health -> API response -> Telegram reply.
