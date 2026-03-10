#!/usr/bin/env bash
# Auto-runtime-checker - runs periodically to refresh state AND check for @mentions
# This is the main automation that keeps runtime tracking fresh and handles nudge flags

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
RUNTIME_FILE="$WORKSPACE/RUNTIME.md"
RUNTIME_SCRIPT="$WORKSPACE/scripts/update-runtime.sh"
NUDGE_SCRIPT="$WORKSPACE/scripts/check_nudge.sh"

# Exit silently if scripts don't exist
[[ ! -x "$RUNTIME_SCRIPT" ]] && exit 0

# Check if runtime refresh needed
if [[ -f "$RUNTIME_FILE" ]]; then
    LAST_UPDATE=$(stat -c %Y "$RUNTIME_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE_SECONDS=$((NOW - LAST_UPDATE))
    
    # Refresh if older than 5 minutes
    if (( AGE_SECONDS > 300 )); then
        "$RUNTIME_SCRIPT" >/dev/null 2>&1
        echo "Runtime updated (was $((AGE_SECONDS/60))m old)"
    fi
else
    # First time run
    "$RUNTIME_SCRIPT" >/dev/null 2>&1
    echo "Runtime tracking initialized"
fi

# Check for nudge flags (from @mentions)
if [[ -x "$NUDGE_SCRIPT" ]]; then
    "$NUDGE_SCRIPT" >/dev/null 2>&1
fi

# Context monitoring is now handled by jess-lifecycle.timer (jess_lifecycle.py)
# No need to call the guard here — one system, one responsibility.