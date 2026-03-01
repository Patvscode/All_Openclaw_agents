#!/usr/bin/env bash
set -euo pipefail

HEALTH_URL=${HEALTH_URL:-http://127.0.0.1:18080/health}
SERVICE=${SERVICE:-jess-q35.service}
LOG_FILE=${LOG_FILE:-/home/pmello/.openclaw/workspace-q35/logs/jess_watchdog.log}
mkdir -p "$(dirname "$LOG_FILE")"

ts() { date -Is; }

if ! curl -fsS --max-time 4 "$HEALTH_URL" >/dev/null 2>&1; then
  echo "$(ts) healthcheck failed; restarting $SERVICE" >> "$LOG_FILE"
  systemctl --user restart "$SERVICE"
  sleep 2
  if ! curl -fsS --max-time 6 "$HEALTH_URL" >/dev/null 2>&1; then
    echo "$(ts) restart failed; attempting openclaw-gateway restart" >> "$LOG_FILE"
    systemctl --user restart openclaw-gateway.service || true
  else
    echo "$(ts) restart recovered service" >> "$LOG_FILE"
  fi
else
  echo "$(ts) healthy" >> "$LOG_FILE"
fi
