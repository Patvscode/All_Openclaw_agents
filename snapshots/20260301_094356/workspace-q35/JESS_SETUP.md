# JESS_SETUP.md — Full Setup Process (Q35, non-Ollama)

This documents how Jess was made fully operational with Qwen 3.5 35B-A3B Q8.

## Why non-Ollama
Ollama failed this GGUF with:
- `unknown model architecture: qwen35moe`

Therefore Jess uses **llama.cpp server** as runtime.

## 1) Model Files
- Directory: `/home/pmello/models/qwen3.5-35b-a3b-q8`
- File: `Qwen3.5-35B-A3B-Q8_0.gguf`
- Template file: `Modelfile` (for reference only; runtime is llama.cpp)

## 2) Runtime
- Built llama.cpp locally at:
  - `/home/pmello/llama.cpp-q35/build-cpu/bin/llama-server`
- Run command:
```bash
/home/pmello/llama.cpp-q35/build-cpu/bin/llama-server \
  -m /home/pmello/models/qwen3.5-35b-a3b-q8/Qwen3.5-35B-A3B-Q8_0.gguf \
  --host 127.0.0.1 --port 18080 --ctx-size 32768 --threads 16 --jinja
```

## 3) OpenClaw provider wiring
In `~/.openclaw/openclaw.json`:
- `models.providers.q35cpp.api = openai-completions`
- `models.providers.q35cpp.baseUrl = http://127.0.0.1:18080/v1`
- model id: `qwen3.5-35b-a3b-q8`

## 4) Agent wiring
- Agent id: `q35`
- Name: `JESS (Q35 LOCAL)`
- Model: `q35cpp/qwen3.5-35b-a3b-q8`
- Tools profile: `full`
- Telegram account binding: `jessa -> q35` (`@Jessa3bot`)

## 5) Agent-to-agent delegation
- Enabled via `q35.subagents.allowAgents`.
- Allowed peers: `flash`, `runner`, `prime`, `bob`, `codex`.
- Delegation policy is compute-aware and ROI-based (see `AGENTS.md`).

## 6) Verification checklist
1. `curl -s http://127.0.0.1:18080/health` returns ok.
2. `/v1/chat/completions` returns text from model.
3. `openclaw status --deep` shows Telegram + q35 activity healthy.
4. Jess responds in Telegram without tool/runtime errors.

## 7) Co-running with Ollama
- Q35 backend is independent of Ollama.
- Watch contention when both heavy runtimes are active.
- Use `ollama ps` + system telemetry before launching parallel heavy tasks.
- Prefer sequential heavy workloads when GPU/CPU pressure is high.
