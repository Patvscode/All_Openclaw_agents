#!/usr/bin/env bash
set -euo pipefail

curl -fsS http://127.0.0.1:18080/health >/dev/null
python3 - <<'PY'
import requests
url='http://127.0.0.1:18080/v1/chat/completions'
p={"model":"qwen3.5-35b-a3b-q8","messages":[{"role":"user","content":"Reply exactly: OK"}],"max_tokens":8,"temperature":0}
r=requests.post(url,json=p,timeout=90)
print('status',r.status_code)
print('body_keys',list(r.json().keys()))
PY
echo "Jess smoke: PASS"
