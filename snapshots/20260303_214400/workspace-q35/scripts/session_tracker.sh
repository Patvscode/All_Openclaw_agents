#!/usr/bin/env bash
set -euo pipefail

# Session duration + context growth rate tracker
# Tracks: session start time, duration, context growth rate, anomalies

LOG_FILE=${LOG_FILE:-/home/pmello/.openclaw/workspace-q35/logs/session_tracker.log}
STATE_FILE=${STATE_FILE:-/home/pmello/.openclaw/workspace-q35/logs/session_tracker_state.json}
HISTORY_FILE=${HISTORY_FILE:-/home/pmello/.openclaw/workspace-q35/logs/session_history.jsonl}
CTX_GROWTH_WARN=${CTX_GROWTH_WARN:-1000}  # tokens/min threshold
CTX_GROWTH_CRIT=${CTX_GROWTH_CRIT:-2000}  # tokens/min threshold
DURATION_WARN=${DURATION_WARN:-3600}      # seconds (1 hour)
DURATION_CRIT=${DURATION_CRIT:-7200}      # seconds (2 hours)
mkdir -p "$(dirname "$LOG_FILE")"

now_s=$(date +%s)
now_iso=$(date -Iseconds)

# Fetch current session data
payload=$(openclaw sessions --agent q35 --active 240 --json 2>/dev/null || echo '{}')

python3 - <<PY "$payload" "$now_s" "$STATE_FILE" "$HISTORY_FILE" "$LOG_FILE" "$CTX_GROWTH_WARN" "$CTX_GROWTH_CRIT" "$DURATION_WARN" "$DURATION_CRIT"
import json, sys, time

payload = json.loads(sys.argv[1]) if sys.argv[1].strip() else {}
now_s = int(sys.argv[2])
state_path = sys.argv[3]
history_path = sys.argv[4]
log_path = sys.argv[5]
grow_warn = int(sys.argv[6])
grow_crit = int(sys.argv[7])
dur_warn = int(sys.argv[8])
dur_crit = int(sys.argv[9])

sessions = (payload.get('sessions') or [])
s = sessions[0] if sessions else {}

session_key = s.get('key', 'unknown')
age_ms = s.get('ageMs') or 0
age_s = int(age_ms / 1000)
context_tokens = s.get('contextTokens') or 0
input_tokens = s.get('inputTokens') or 0
output_tokens = s.get('outputTokens') or 0

# Load previous state
try:
    with open(state_path, 'r') as f:
        prev_state = json.load(f)
    prev_ctx = prev_state.get('contextTokens', 0)
    prev_time = prev_state.get('checkedAt', 0)
    time_diff_s = now_s - prev_time
    # Calculate growth rate (tokens per minute)
    ctx_diff = context_tokens - prev_ctx
    growth_rate = round((ctx_diff / time_diff_s) * 60, 1) if time_diff_s > 0 and time_diff_s < 300 else 0
except (FileNotFoundError, json.JSONDecodeError):
    prev_ctx = context_tokens
    time_diff_s = 0
    growth_rate = 0
    ctx_diff = 0

# Determine health level
level = 'ok'
anomalies = []

# Duration checks
if age_s >= dur_warn:
    level = 'warn'
    anomalies.append(f'session_duration:{age_s}s')
if age_s >= dur_crit:
    level = 'crit'
    anomalies.append(f'session_duration_critical:{age_s}s')

# Growth rate checks
if growth_rate >= grow_crit:
    level = 'crit'
    anomalies.append(f'context_growth_crit:{growth_rate}tok/min')
elif growth_rate >= grow_warn:
    level = 'warn' if level == 'ok' else level
    anomalies.append(f'context_growth_high:{growth_rate}tok/min')

# Bad memory injection detection: context jumps too fast after restart
if time_diff_s < 60 and ctx_diff > 5000:
    anomalies.append('suspicious_context_jump:possible_bad_injection')
    level = 'crit'

# Checkpoint validation: if session is old but context not growing, checkpoint may be stuck
if age_s > 1800 and growth_rate < 10 and prev_ctx > 0:
    anomalies.append('stale_session:low_growth_after_long_uptime')

state = {
    'checkedAt': now_s,
    'checkedAtISO': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
    'agent': 'q35',
    'sessionKey': session_key,
    'level': level,
    'sessionAgeSec': age_s,
    'sessionAgeMin': round(age_s / 60, 1),
    'contextTokens': context_tokens,
    'inputTokens': input_tokens,
    'outputTokens': output_tokens,
    'contextGrowthRate': growth_rate,  # tokens/min
    'contextGrowthPerMin': round(ctx_diff, 1) if time_diff_s > 0 else 0,
    'anomalies': anomalies,
    'actions': {
        'checkpoint': 'Run /compact to create checkpoint if growth is normal but session is long',
        'new_session': 'Send /new in @Jessa3bot if context_growth_crit or suspicious_context_jump',
        'investigate': 'Check memory_manager logs if anomalous growth detected'
    }
}

# Save state
with open(state_path, 'w') as f:
    json.dump(state, f, indent=2)
    f.write('\n')

# Append to history
with open(history_path, 'a') as f:
    f.write(json.dumps(state) + '\n')

# Log
with open(log_path, 'a') as f:
    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] level={level} age={age_s}s growth={growth_rate}tok/min ctx={context_tokens} anomalies={anomalies if anomalies else '-'}\n")

print(json.dumps(state, indent=2))
PY