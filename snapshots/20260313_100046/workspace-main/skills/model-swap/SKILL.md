# Model Swap Skill

Swap between local llama.cpp models on the DGX Spark. Manages the lifecycle of large language models running on port 18080.

## Quick Commands

```bash
# Check what's running
swap-model status

# Switch to 122B (high quality, ~5 min load time)
swap-model 122b

# Switch to 35B (faster, lighter)
swap-model 35b
```

## Supervisor API (port 18090)

```bash
# Status (what model, health, context usage)
curl http://127.0.0.1:18090/status

# Trigger swap via API
curl http://127.0.0.1:18090/swap/122b
curl http://127.0.0.1:18090/swap/35b

# Trigger context rescue manually
curl http://127.0.0.1:18090/rescue

# List available models
curl http://127.0.0.1:18090/models
```

## File Trigger (for scripts/cron/small models)

Any process can trigger a swap by writing to a file:
```bash
echo "122b" > /tmp/model-swap-request
echo "35b" > /tmp/model-swap-request
```

## Available Models

| Key | Model | Size | Active Params | Context | Load Time |
|-----|-------|------|---------------|---------|-----------|
| 122b | Qwen3.5-122B-A10B UD-Q5_K_XL | 85.6 GB | 10B/token | 32K | ~5 min |
| 35b | Qwen3.5-35B-A3B Q8_0 | 36.9 GB | 3B/token | 98K | ~1 min |

## Key Files

- Swap script: `/home/pmello/models/swap-model.sh`
- Supervisor: `/home/pmello/models/supervisor/model-supervisor.py`
- Model Registry: `/home/pmello/models/MODEL_REGISTRY.md`
- Supervisor state: `/tmp/model-supervisor/state.json`
- Supervisor logs: `/tmp/model-supervisor/supervisor.log`

## Important Notes

- Both models share port 18080 — only one can run at a time
- The supervisor handles rollback: if the new model fails to load, it auto-restarts the previous one
- The 122B takes ~5 minutes to load 85 GB — don't set timeouts under 360s
- RAM with 122B loaded: ~101 GB used, ~20 GB free. Don't load large Ollama models alongside.
- Split GGUFs: always point at shard `-00001-of-00003`, llama.cpp finds the rest
