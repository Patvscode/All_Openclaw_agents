#!/usr/bin/env bash
# Auto-trigger runtime update at session start
# This script should be called when a new message arrives

RUNTIME_SCRIPT="/home/pmello/.openclaw/workspace-q35/scripts/update-runtime.sh"

if [[ -x "$RUNTIME_SCRIPT" ]]; then
    "$RUNTIME_SCRIPT" >/dev/null 2>&1
fi