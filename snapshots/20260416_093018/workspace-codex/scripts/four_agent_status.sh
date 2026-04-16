#!/usr/bin/env bash
set -euo pipefail

CONFIG="/home/pmello/.openclaw/openclaw.json"
STATUS_CMD="openclaw status"

if [[ ! -f "$CONFIG" ]]; then
  echo "Missing config: $CONFIG" >&2
  exit 1
fi

echo "== Four-Agent Core =="
python3 - <<'PY'
import json
from pathlib import Path
obj=json.loads(Path('/home/pmello/.openclaw/openclaw.json').read_text())
for a in obj.get('agents',{}).get('list',[]):
    hb=(a.get('heartbeat') or {}).get('every','disabled')
    subs=','.join((a.get('subagents') or {}).get('allowAgents',[])) or '-'
    print(f"{a['id']}: model={a.get('model','-')} heartbeat={hb} delegates={subs}")
PY

echo
echo "== OpenClaw Status Summary =="
$STATUS_CMD | sed -n '1,80p'

echo
echo "== Core Sessions =="
$STATUS_CMD | awk '
  /agent:main:main|agent:codex:main|agent:gemma:main|agent:q35:main/ {print}
'
