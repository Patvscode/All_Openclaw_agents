# JESS Tools

## Key Commands
- `memquery "question"` — search memory (port 8102)
- `comms post general "msg"` / `comms dm main "msg"` — agent comms
- `board list` — task board
- `wc -c <file>` — always check size before reading
- `node --check file.js` — verify JS syntax

## Voice (Sesame CSM-1B)
- `voice say "text" --voice jess --send` — generate as Jess
- `voice hear file.ogg` — transcribe audio

## File Safety
- Under 15KB → safe to read
- 15-30KB → read-only, use `edit` for changes
- Over 30KB → DO NOT READ. Write to new file or use `smart-file-edit`

## System
- DGX Spark, 128GB RAM, GB10 GPU
- **Model:** Qwen 3.6 35B-A3B Q8_0 on port 18080 (via qwen36 provider)
- **Vision:** mmproj-BF16.gguf loaded — can process images
- **Context:** 65K tokens (budget ~60K after system prompt)
- Ollama: port 11434 (qwen3.5:0.8b only — CUDA bug blocks larger models)
- Hub: http://100.109.173.109:8090

## Model Details
- Provider: `qwen36/qwen3.6-35b-a3b`
- Architecture: MoE (35B total, 3B active/token)
- Quantization: Q8_0 (35 GB weights + 861 MB mmproj)
- Strengths: Agentic coding (SWE-Bench 73.4%), tool use, reasoning
- Port 18080 is shared — if another model is loaded, you'll get errors

## Ops Toolkit
- `tools/agent_ops/run_triage.sh` — agent triage
- `tools/agent_ops/file_preflight.sh` — check file size before reading
- `backup-now` — snapshot to backup repo
- `self-continue q35 <delay> "message"` — schedule continuation

## Neural Lab (port 8103)
Multi-agent simulation + RL training platform.
```bash
curl -s localhost:8103/api/rl/status | python3 -m json.tool
```
