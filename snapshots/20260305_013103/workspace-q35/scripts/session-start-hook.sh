#!/usr/bin/env bash
# Session startup hook - auto-checks runtime before responding
# This script runs at the start of each session to refresh state

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
SCRIPT="$WORKSPACE/scripts/update-runtime.sh"

# Only run if script exists and is executable
if [[ -x "$SCRIPT" ]]; then
    # Run silently, capture any alerts
    ALERTS=$("$SCRIPT" 2>&1 | grep -E "^⚠️ ALERTS" || true)
    
    if [[ -n "$ALERTS" ]]; then
        # If alerts detected, we'll surface them when responding
        echo "RUNTIME_ALERTS:1" >> "$WORKSPACE/.runtime-alerts"
    else
        # Clear alerts file
        rm -f "$WORKSPACE/.runtime-alerts"
    fi
fi