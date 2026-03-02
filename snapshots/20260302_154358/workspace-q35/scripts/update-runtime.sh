#!/usr/bin/env bash
# Runtime tracker script - auto-updates RUNTIME.md
# Usage: ./update-runtime.sh

set -eo pipefail
# Note: removed 'u' to allow undefined variables in grep commands

# === GUARD THRESHOLDS ===
LATENCY_WARN=100      # ms - warn if >100ms
LATENCY_CRIT=500      # ms - critical if >500ms
CONTEXT_WARN=80       # % - warn if >80%
CONTEXT_CRIT=95       # % - critical if >95%
STATE_AGE_WARN=300    # seconds - warn if state older than 5min
STATE_AGE_CRIT=600    # seconds - critical if state older than 10min

# Hardcode to workspace root (not scripts subdirectory)
RUNTIME_FILE="/home/pmello/.openclaw/workspace-q35/RUNTIME.md"

# Get current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')

# Get system info
OS_INFO=$(uname -o)$(uname -r)
NODE_VERSION=$(node --version 2>/dev/null || echo "N/A")
HOSTNAME=$(hostname)

# Get OpenClaw status (extract key fields)
GATEWAY_STATUS=$(openclaw status --deep 2>&1 | grep "Gateway" | grep "reachable" | grep -oP '\d+(?=ms)' | head -1 | tr -d '\n' || echo "unknown")
GATEWAY_PIDS=$(openclaw status --deep 2>&1 | grep "Gateway service" | grep -oP 'pid \K\d+' | head -1 || echo "unknown")
SESSIONS=$(openclaw status --deep 2>&1 | grep "Sessions" | grep -oP '\d+(?= active)' || echo "unknown")
MEMORY_FILES=$(openclaw status --deep 2>&1 | grep "Memory" | grep -oP '\d+(?= files)' || echo "unknown")

# Get model health
MODEL_HEALTH=$(curl -s --max-time 2 http://127.0.0.1:18080/health 2>/dev/null || echo "unreachable")

# === GUARD THRESHOLD CHECKS ===
LATENCY_STATUS="ok"
if [[ "$GATEWAY_STATUS" =~ ^[0-9]+$ ]]; then
    if (( GATEWAY_STATUS > LATENCY_CRIT )); then
        LATENCY_STATUS="CRITICAL ⚠️"
    elif (( GATEWAY_STATUS > LATENCY_WARN )); then
        LATENCY_STATUS="WARN ⚡"
    fi
fi

# Check queue depth
QUEUE_STATUS="empty"
QUEUE_DEPTH=$(openclaw status --deep 2>&1 | grep -oP 'Queue:.*depth\s*\K\d+' | head -1 || echo "0")
if [[ "$QUEUE_DEPTH" =~ ^[0-9]+$ ]] && (( QUEUE_DEPTH > 0 )); then
    QUEUE_STATUS="backlog ($QUEUE_DEPTH)"
fi

# === STALE STATE CHECK ===
# Check if RUNTIME.md exists and calculate age
STATE_AGE="0s"
STATE_STATUS="fresh"
if [[ -f "$RUNTIME_FILE" ]]; then
    LAST_UPDATE=$(stat -c %Y "$RUNTIME_FILE" 2>/dev/null || echo 0)
    NOW=$(date +%s)
    AGE_SECONDS=$((NOW - LAST_UPDATE))
    AGE_MIN=$((AGE_SECONDS / 60))
    
    if (( AGE_SECONDS < STATE_AGE_WARN )); then
        STATE_STATUS="fresh"
    elif (( AGE_SECONDS < STATE_AGE_CRIT )); then
        STATE_STATUS="stale (warn)"
    else
        STATE_STATUS="stale (critical)"
    fi
    STATE_AGE="${AGE_MIN}m ${AGE_SECONDS%?}s"
fi

# === ALERT OUTPUT ===
ALERTS=""
if [[ "$LATENCY_STATUS" != "ok" ]]; then
    ALERTS+="⚠️ Gateway latency: ${GATEWAY_STATUS}ms (${LATENCY_STATUS})"$'\n'
fi
if [[ "$QUEUE_STATUS" != "empty" ]]; then
    ALERTS+="⚠️ Queue depth: $QUEUE_STATUS"$'\n'
fi
if [[ "$STATE_STATUS" != "fresh" ]]; then
    ALERTS+="⚠️ State age: $STATE_AGE (${STATE_STATUS})"$'\n'
fi

if [[ -n "$ALERTS" ]]; then
    echo "⚠️ ALERTS DETECTED:"
    echo "$ALERTS"
fi

# Build update block
ALERT_BLOCK=""
if [[ -n "$ALERTS" ]]; then
    ALERT_BLOCK="
⚠️ **ALERTS:**
${ALERTS}"
fi

cat > "$RUNTIME_FILE" << EOF
# Runtime Tracking

## ⚡ Status Check
**Last Updated:** $TIMESTAMP
**State Age:** $STATE_AGE ($STATE_STATUS)
**Gateway Latency:** ${GATEWAY_STATUS:-unknown}ms ($LATENCY_STATUS)

## Context Window Usage
- Model: \`qwen3.5-35b-a3b-q8\` (35B params)
- Context: 200k tokens (default main session)
- Sessions: $SESSIONS active
- Default session: claude-opus-4-6

## System Info
- **OS:** Linux 6.17.0-1008-nvidia (arm64)
- **Node:** $NODE_VERSION
- **Hostname:** $HOSTNAME
- **RAM:** 128GB (DGX Spark)
- **GPU:** GB10

## Services Status
- **Gateway:** running (pid $GATEWAY_PIDS), ws://127.0.0.1:18789, ${GATEWAY_STATUS:-?}ms latency
- **Node Service:** stopped
- **Tailscale:** off
- **Queue:** $QUEUE_STATUS

## Model Health
- **q35cpp:** $MODEL_HEALTH

## Sessions
- Bootstrap files: 11 present
- Memory: $MEMORY_FILES files, 11 chunks
- Agent active: default main

## Monitoring Commands
\`\`\`bash
# Quick status
openclaw status --deep | head -20

# Gateway latency
curl -s http://127.0.0.1:18789/health

# Model health
curl -s http://127.0.0.1:18080/health

# Resource usage
free -h && df -h && uptime
\`\`\`

## Notes
- Auto-updated by \`update-runtime.sh\`
- Log any service restarts or issues in \`DIAGNOSTICS.md\`
- Track context window patterns over time

$ALERT_BLOCK
EOF

echo "✓ Runtime tracking updated: $RUNTIME_FILE"