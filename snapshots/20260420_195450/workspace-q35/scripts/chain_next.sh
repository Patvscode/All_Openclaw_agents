#!/usr/bin/env bash
set -euo pipefail

# chain_next.sh — Jess schedules her own next action
# Usage: chain_next.sh <minutes> "<message>"
# Creates a one-shot cron job that fires in N minutes with the given task

MINUTES="${1:-10}"
MESSAGE="${2:-Run scripts/autonomy_engine.sh, read the output, and act on it. After completing work, schedule your next action with: bash scripts/chain_next.sh 10 'your next task description'}"
OPENCLAW="/home/pmello/.npm-global/bin/openclaw"
NAME="jess-chain-$(date +%s)"

# Schedule next action
$OPENCLAW cron add \
    --name "$NAME" \
    --at "${MINUTES}m" \
    --agent q35 \
    --session isolated \
    --delete-after-run \
    --message "$MESSAGE" \
    2>/dev/null

echo "⏰ Next action scheduled: +${MINUTES}m — $NAME"
