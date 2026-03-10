#!/usr/bin/env bash
set -euo pipefail
m=${1:-}
case "$m" in
  heuristic|ollama-qwen3-8b|ollama-qwen3-14b) ;;
  *) echo "Usage: $0 {heuristic|ollama-qwen3-8b|ollama-qwen3-14b}"; exit 1;;
esac
cat > /home/pmello/.openclaw/workspace-q35/state/jess_keeper_mode.json <<JSON
{"mode":"$m","updatedAt":"$(date -Is)"}
JSON
echo "keeper mode set: $m"
