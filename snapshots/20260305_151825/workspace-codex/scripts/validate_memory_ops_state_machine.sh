#!/usr/bin/env bash
set -euo pipefail

HOST="localhost"
WATCH_SECONDS=0
INTERVAL_SECONDS=5
OUTFILE=""
SUMMARY=false

usage() {
  cat <<'USAGE'
Usage:
  validate_memory_ops_state_machine.sh [host]
  validate_memory_ops_state_machine.sh --host <host> [--watch-seconds N] [--interval-seconds N] [--out <path>] [--summary]

Examples:
  validate_memory_ops_state_machine.sh
  validate_memory_ops_state_machine.sh --watch-seconds 60 --interval-seconds 5 --out /tmp/memory_ops_transitions.jsonl
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --host)
      HOST="${2:-}"
      shift 2
      ;;
    --watch-seconds)
      WATCH_SECONDS="${2:-0}"
      shift 2
      ;;
    --interval-seconds)
      INTERVAL_SECONDS="${2:-5}"
      shift 2
      ;;
    --out)
      OUTFILE="${2:-}"
      shift 2
      ;;
    --summary)
      SUMMARY=true
      shift
      ;;
    *)
      if [[ "$1" =~ ^[A-Za-z0-9._-]+$ ]] && [[ "$HOST" == "localhost" ]]; then
        HOST="$1"
        shift
      else
        echo "Unknown argument: $1" >&2
        usage >&2
        exit 1
      fi
      ;;
  esac
done

API="http://${HOST}:8095"

fetch_json() {
  local path="$1"
  curl -fsS "${API}${path}" || echo '{}'
}

sample_once() {
  local state_json fresh_json stats_json err_json
  state_json="$(fetch_json /jess/state)"
  fresh_json="$(fetch_json /jess-summary)"
  stats_json="$(fetch_json /jess/memory/stats)"
  err_json="$(fetch_json /jess/keeper/errors)"

  node - <<'NODE' "$state_json" "$fresh_json" "$stats_json" "$err_json" "${1:-null}"
const [st,fr,ms,ke,prevStateRaw] = process.argv.slice(2).map(x=>{try{return JSON.parse(x)}catch{return x}});
const prevState = prevStateRaw && prevStateRaw !== 'null' ? prevStateRaw : null;
function deriveRuntimeState(st,fr,ms,ke,prevState=null){
  const now=Date.now();
  const checkedAt=st?.checkedAt?new Date(st.checkedAt).getTime():null;
  const ageSec=checkedAt?Math.floor((now-checkedAt)/1000):null;
  const keeperErrorText=(ke?.text||'').trim();
  const hasErrors=!!keeperErrorText;
  const summaryStale=typeof fr?.ageSec==='number' && fr.ageSec>900;
  const veryStale=ageSec!=null && ageSec>240;
  const degradedSignals=[];
  const busy=st?.busy===true || /running|processing|summar/i.test(JSON.stringify(st||{}));
  const keeperRecent=st?.keeperLastRunAt && ((now-new Date(st.keeperLastRunAt).getTime())<90*1000);
  const managerRecent=ms?.lastRunAt && ((now-new Date(ms.lastRunAt).getTime())<90*1000);
  const explicitBooting = st?.booting===true || /boot|init|starting/i.test(String(st?.status||''));

  let state='IDLE_READY';
  const reasons=[];
  if(!checkedAt || explicitBooting){ state='BOOTING'; reasons.push(!checkedAt?'missing checkedAt':'explicit boot/init status'); }
  if(busy){ state='PROCESSING'; reasons.push('busy/running markers present'); }
  if(keeperRecent || managerRecent){ state='MEMORY_MAINTENANCE'; reasons.push('recent keeper/manager activity (<90s)'); }
  if(hasErrors) degradedSignals.push('keeper errors present');
  if(veryStale) degradedSignals.push('state check stale >240s');
  if(summaryStale) degradedSignals.push('summary stale >900s');
  if(hasErrors || veryStale || summaryStale){ state='DEGRADED'; reasons.push('errors or stale signals detected'); reasons.push(...degradedSignals); }

  const recovered = degradedSignals.length===0;
  const quiescent = !!checkedAt && !busy && !keeperRecent && !managerRecent;
  if(prevState==='DEGRADED' && recovered && quiescent){ state='RECOVERY'; reasons.push('degraded -> healthy recovery edge (quiescent)'); }

  return {
    sampledAt: new Date(now).toISOString(),
    prevState,
    state,
    transition: prevState && prevState!==state ? `${prevState}->${state}` : null,
    reasons,
    ageSec,
    summaryAgeSec:fr?.ageSec ?? null,
    hasErrors,
    degradedSignals,
    managerLastRun:ms?.lastRunAt ?? null,
    keeperLastRun:st?.keeperLastRunAt ?? null,
  };
}
const r=deriveRuntimeState(st,fr,ms,ke,prevState);
console.log(JSON.stringify(r));
NODE
}

if [[ "$WATCH_SECONDS" -le 0 ]]; then
  sample_once null | jq .
  exit 0
fi

if [[ -n "$OUTFILE" ]]; then
  : > "$OUTFILE"
fi

SUMMARY_FILE=""
if [[ "$SUMMARY" == "true" && -z "$OUTFILE" && "$WATCH_SECONDS" -gt 0 ]]; then
  SUMMARY_FILE="$(mktemp)"
  : > "$SUMMARY_FILE"
fi

start_epoch="$(date +%s)"
prev="null"
while true; do
  now_epoch="$(date +%s)"
  elapsed=$((now_epoch - start_epoch))
  if (( elapsed > WATCH_SECONDS )); then
    break
  fi

  sample="$(sample_once "$prev")"
  echo "$sample" | jq .
  if [[ -n "$OUTFILE" ]]; then
    echo "$sample" >> "$OUTFILE"
  fi
  if [[ -n "$SUMMARY_FILE" ]]; then
    echo "$sample" >> "$SUMMARY_FILE"
  fi
  prev="$(echo "$sample" | jq -r '.state')"
  sleep "$INTERVAL_SECONDS"
done

if [[ -n "$OUTFILE" ]]; then
  echo "wrote transition samples to $OUTFILE"
fi

if [[ "$SUMMARY" == "true" ]]; then
  src_file="$OUTFILE"
  if [[ -n "$SUMMARY_FILE" ]]; then
    src_file="$SUMMARY_FILE"
  fi
  if [[ -z "$src_file" ]]; then
    src_file="$(mktemp)"
    sample_once null > "$src_file"
  fi

  echo "\ntransition summary:"
  jq -r '.state' "$src_file" 2>/dev/null | sort | uniq -c | sed 's/^/  /' || true
  echo "transitions seen:"
  jq -r 'select(.transition != null) | .transition' "$src_file" 2>/dev/null | sort | uniq -c | sed 's/^/  /' || echo "  (none)"

  if [[ -z "$OUTFILE" ]]; then
    rm -f "$src_file"
  fi
fi

if [[ -n "$SUMMARY_FILE" ]]; then
  rm -f "$SUMMARY_FILE"
fi
