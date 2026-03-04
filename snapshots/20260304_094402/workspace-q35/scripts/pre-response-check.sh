#!/usr/bin/env bash
# Pre-response runtime check
# Run this before every response to ensure fresh state

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
RUNTIME_FILE="$WORKSPACE/RUNTIME.md"
ALERTS_FILE="$WORKSPACE/.runtime-alerts"
SCRIPT="$WORKSPACE/scripts/update-runtime.sh"

# Check if we need to refresh
NEED_REFRESH=0

# Always refresh if alerts file exists (indicates stale state)
if [[ -f "$ALERTS_FILE" ]]; then
    NEED_REFRESH=1
fi

# Also refresh if file is older than 2 minutes
if [[ -f "$RUNTIME_FILE" ]]; then
    LAST_UPDATE=$(stat -c %Y "$RUNTIME_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE_SECONDS=$((NOW - LAST_UPDATE))
    if (( AGE_SECONDS > 120 )); then
        NEED_REFRESH=1
    fi
fi

# Run refresh if needed
if (( NEED_REFRESH )) && [[ -x "$SCRIPT" ]]; then
    "$SCRIPT" >/dev/null 2>&1
    rm -f "$ALERTS_FILE"
fi

# Return current state for JESS to use
if [[ -f "$RUNTIME_FILE" ]]; then
    # Extract key metrics
    STATE_STATUS=$(grep -oP 'State Age:.*\(\K[^)]+' "$RUNTIME_FILE" 2>/dev/null || echo "unknown")
    LATENCY=$(grep -oP 'Gateway Latency: \K\d+' "$RUNTIME_FILE" 2>/dev/null || echo "unknown")
    
    # Check for alerts in file
    if grep -q "ALERTS" "$RUNTIME_FILE" 2>/dev/null; then
        echo "RUNTIME_ALERTS:1"
    else
        echo "RUNTIME_ALERTS:0"
    fi
fi