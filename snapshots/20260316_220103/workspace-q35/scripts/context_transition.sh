#!/usr/bin/env bash
set -euo pipefail

# context_transition.sh — Automated context save + reset + resume for Jess
#
# When context usage gets too high, this script:
# 1. Saves Jess's current state to RESUME.md
# 2. Logs the transition to daily memory
# 3. Resets/creates a new session
# 4. Schedules a follow-up cron job to wake Jess back up
#
# Can be called by the runtime guard, by Jess herself, or manually.
# Usage: context_transition.sh [reason]

REASON="${1:-context_overflow}"
WORKSPACE="/home/pmello/.openclaw/workspace-q35"
OPENCLAW="/home/pmello/.npm-global/bin/openclaw"
AGENT="q35"
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
MEMORY_FILE="$WORKSPACE/memory/$TODAY.md"
RESUME_FILE="$WORKSPACE/RESUME.md"
LOG_FILE="$WORKSPACE/logs/context_transitions.log"

mkdir -p "$WORKSPACE/logs" "$WORKSPACE/memory"

echo "[$TIMESTAMP] Context transition triggered: $REASON" | tee -a "$LOG_FILE"

# ── Step 1: Get current session state ──────────────────────────────
SESSION_INFO=$($OPENCLAW sessions --agent "$AGENT" --active 60 --json 2>/dev/null || echo '{}')
CTX_PCT=$(echo "$SESSION_INFO" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    sessions = d.get('sessions', [])
    if sessions:
        s = sessions[0]
        ctx = s.get('contextTokens', 0)
        total = s.get('totalTokens', 0)
        if ctx > 0:
            print(round(total / ctx * 100, 1))
        else:
            print('unknown')
    else:
        print('no-session')
except:
    print('error')
" 2>/dev/null || echo "error")

echo "  Context usage: ${CTX_PCT}%" | tee -a "$LOG_FILE"

# ── Step 2: Log the transition to daily memory ────────────────────
cat >> "$MEMORY_FILE" << MEMEOF

## Context Transition [$TIMESTAMP]
- **Reason:** $REASON
- **Context at transition:** ${CTX_PCT}%
- **Action:** Auto-reset + resume scheduled
- **Resume file:** RESUME.md (read this on next wake)
MEMEOF

echo "  Logged to $MEMORY_FILE" | tee -a "$LOG_FILE"

# ── Step 3: Reset the session ──────────────────────────────────────
# Send /reset command to Jess's main session via the gateway
echo "  Resetting session..." | tee -a "$LOG_FILE"

# Use openclaw's session management to reset
$OPENCLAW sessions cleanup --agent "$AGENT" 2>/dev/null || true

echo "  Session reset." | tee -a "$LOG_FILE"

# ── Step 4: Schedule wake-up ───────────────────────────────────────
WAKE_MSG="You just had a context transition (auto-reset). Read RESUME.md FIRST — it has your full state from before the reset. Then continue from where you left off. Reason: $REASON"

CRON_NAME="jess-resume-$(date +%s)"
$OPENCLAW cron add \
    --name "$CRON_NAME" \
    --at "1m" \
    --agent "$AGENT" \
    --session isolated \
    --delete-after-run \
    --message "$WAKE_MSG" \
    2>/dev/null || echo "  ⚠️ Failed to schedule wake-up cron"

echo "  Wake-up scheduled: $CRON_NAME (1 min)" | tee -a "$LOG_FILE"
echo "[$TIMESTAMP] Transition complete. Jess will resume in ~1 minute." | tee -a "$LOG_FILE"
