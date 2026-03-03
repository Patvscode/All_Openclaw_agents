#!/usr/bin/env bash
set -euo pipefail

echo "== Jess service =="
systemctl --user status jess-q35.service --no-pager | sed -n '1,14p'
echo
echo "== Watchdog timer =="
systemctl --user status jess-watchdog.timer --no-pager | sed -n '1,12p'
echo
echo "== Runtime health =="
curl -fsS http://127.0.0.1:18080/health || echo "health check failed"
