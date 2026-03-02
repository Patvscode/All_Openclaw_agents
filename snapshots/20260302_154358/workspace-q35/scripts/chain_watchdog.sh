#!/usr/bin/env bash
# chain_watchdog.sh — Checks if Jess has upcoming chain jobs
# If no chains exist, creates one. Prevents the loop from dying.

OPENCLAW="/home/pmello/.npm-global/bin/openclaw"
CHAINS=$($OPENCLAW cron list 2>/dev/null | grep -c "jess-chain" || echo 0)

if [[ "$CHAINS" -eq 0 ]]; then
    echo "⚠️ No active chains! Restarting work loop..."
    bash /home/pmello/.openclaw/workspace-q35/scripts/chain_next.sh 5 \
        "Your chain died. Read WORK_LOOP.md. Run scripts/autonomy_engine.sh. Grab work. Chain your next action."
else
    echo "✅ $CHAINS active chain(s)"
fi
