#!/usr/bin/env bash
set -euo pipefail
N=${1:-5}
python3 - <<PY
import time, statistics, requests
N=int(${N})
url='http://127.0.0.1:18080/v1/chat/completions'
lat=[]
for i in range(N):
    p={"model":"qwen3.5-35b-a3b-q8","messages":[{"role":"user","content":"Reply with exactly OK"}],"max_tokens":8,"temperature":0}
    t=time.time(); r=requests.post(url,json=p,timeout=120); dt=time.time()-t
    lat.append(dt)
    print(i+1, r.status_code, f"{dt:.3f}s")
print('avg_s',round(statistics.mean(lat),3))
print('p95_s',round(sorted(lat)[max(0,int(len(lat)*0.95)-1)],3))
PY
