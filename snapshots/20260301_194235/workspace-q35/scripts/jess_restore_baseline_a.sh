#!/usr/bin/env bash
set -euo pipefail

systemctl --user daemon-reload
systemctl --user restart jess-q35.service
systemctl --user enable --now jess-watchdog.timer jess-memory-manager.timer
openclaw gateway restart >/dev/null 2>&1 || true

echo "=== Jess Baseline A Restore ==="
curl -sS http://127.0.0.1:18080/health && echo
systemctl --user status jess-q35.service --no-pager | sed -n '1,16p'
systemctl --user list-timers --all | grep -E 'jess-watchdog|jess-memory-manager' | sed -n '1,6p'
