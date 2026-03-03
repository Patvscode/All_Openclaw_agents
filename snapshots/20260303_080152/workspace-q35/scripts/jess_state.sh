#!/usr/bin/env bash
set -euo pipefail
/home/pmello/.openclaw/workspace-q35/scripts/jess_runtime_guard.sh >/dev/null 2>&1 || true
cat /home/pmello/.openclaw/workspace-q35/logs/jess_runtime_state.json
