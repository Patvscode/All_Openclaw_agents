#!/usr/bin/env bash
# Issue tracker - logs runtime issues with timestamp
# Usage: ./log-issue.sh "description of issue"

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
LOG_FILE="$WORKSPACE/ISSUES.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')

if [[ -z "$1" ]]; then
    echo "Usage: $0 \"issue description\""
    echo ""
    echo "Current issues:"
    if [[ -f "$LOG_FILE" ]]; then
        tail -20 "$LOG_FILE"
    else
        echo "No issues logged yet."
    fi
    exit 0
fi

echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
echo "✓ Issue logged: $1"