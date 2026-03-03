#!/usr/bin/env bash
# Auto-runtime-checker - runs at session start to refresh state
# This is the main automation that keeps runtime tracking fresh

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
RUNTIME_FILE="$WORKSPACE/RUNTIME.md"
SCRIPT="$WORKSPACE/scripts/update-runtime.sh"

# Exit silently if script doesn't exist
[[ ! -x "$SCRIPT" ]] && exit 0

# Check if refresh needed
if [[ -f "$RUNTIME_FILE" ]]; then
    LAST_UPDATE=$(stat -c %Y "$RUNTIME_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE_SECONDS=$((NOW - LAST_UPDATE))
    
    # Refresh if older than 5 minutes
    if (( AGE_SECONDS > 300 )); then
        "$SCRIPT" >/dev/null 2>&1
        echo "Runtime updated (was $((AGE_SECONDS/60))m old)"
    fi
else
    # First time run
    "$SCRIPT" >/dev/null 2>&1
    echo "Runtime tracking initialized"
fi