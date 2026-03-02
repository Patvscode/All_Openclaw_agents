#!/usr/bin/env bash
set -euo pipefail
MODE=${1:-}
case "$MODE" in
  fast|balanced|deep) ;;
  *) echo "Usage: $0 {fast|balanced|deep}"; exit 1;;
esac
cat > /home/pmello/.openclaw/workspace-q35/state/memory_manager_mode.json <<JSON
{
  "mode": "$MODE",
  "updatedAt": "$(date -Is)"
}
JSON
echo "Jess memory manager mode set: $MODE"
