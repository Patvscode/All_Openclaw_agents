#!/usr/bin/env bash
set -euo pipefail

LOG_FILE=${LOG_FILE:-/home/pmello/.openclaw/workspace-q35/logs/jess_runtime_guard.log}
STATE_JSON=${STATE_JSON:-/home/pmello/.openclaw/workspace-q35/logs/jess_runtime_state.json}
CTX_WARN=${CTX_WARN:-75}
CTX_CRIT=${CTX_CRIT:-85}
AGE_WARN_SEC=${AGE_WARN_SEC:-180}
AGE_CRIT_SEC=${AGE_CRIT_SEC:-600}
mkdir -p "$(dirname "$LOG_FILE")"

now_s=$(date +%s)

payload=$(openclaw sessions --agent q35 --active 240 --json 2>/dev/null || echo '{}')

python3 - <<PY "$payload" "$now_s" "$STATE_JSON" "$LOG_FILE" "$CTX_WARN" "$CTX_CRIT" "$AGE_WARN_SEC" "$AGE_CRIT_SEC"
import json,sys,time
payload=json.loads(sys.argv[1]) if sys.argv[1].strip() else {}
now_s=int(sys.argv[2]); state_path=sys.argv[3]; log_path=sys.argv[4]
ctx_warn=int(sys.argv[5]); ctx_crit=int(sys.argv[6]); age_warn=int(sys.argv[7]); age_crit=int(sys.argv[8])
arr=payload.get('sessions',[]) or []
s=arr[0] if arr else {}
ctx=s.get('contextTokens') or 0
inp=s.get('inputTokens') or 0
age_ms=s.get('ageMs') or 0
ctx_pct=round((inp/ctx)*100,1) if ctx else None
age_s=int(age_ms/1000)
level='ok'
notes=[]
# Age-based triggers are primary (ctx_pct often None when totalTokens unavailable)
if age_s >= age_warn:
    level='warn'; notes.append(f'session_age_high:{age_s}s')
if age_s >= age_crit:
    level='crit'; notes.append(f'session_age_critical:{age_s}s')
# Context percentage is secondary (only if available)
if ctx_pct is not None:
    if ctx_pct >= ctx_warn:
        level='warn' if level=='ok' else level; notes.append(f'context_high:{ctx_pct}%')
    if ctx_pct >= ctx_crit:
        level='crit'; notes.append(f'context_critical:{ctx_pct}%')

state={
  'checkedAt':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
  'agent':'q35','level':level,
  'sessionKey':s.get('key'),'contextTokens':ctx,'inputTokens':inp,
  'contextPct':ctx_pct,'sessionAgeSec':age_s,
  'notes':notes,
  'actions':{
    'new_session':'Send /new in @Jessa3bot when context is high',
    'compact':'openclaw sessions cleanup --agent q35 --enforce',
    'restart':'systemctl --user restart jess-q35.service'
  }
}
open(state_path,'w').write(json.dumps(state,indent=2)+"\n")
with open(log_path,'a') as f:
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] level={level} ctx_pct={ctx_pct} age_s={age_s} notes={','.join(notes) if notes else '-'}\n")
print(json.dumps(state))

# Auto-trigger context transition when critical
if level == 'crit' and ctx_pct is not None and ctx_pct >= ctx_crit:
    import subprocess
    reason = f"context_at_{ctx_pct}pct"
    subprocess.Popen(['/bin/bash', '/home/pmello/.openclaw/workspace-q35/scripts/context_transition.sh', reason])
    with open(log_path,'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AUTO-TRANSITION triggered: {reason}\n")
PY
