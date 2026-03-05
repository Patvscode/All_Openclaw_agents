#!/usr/bin/env bash
set -euo pipefail
ROOT=/home/pmello/.openclaw/workspace-q35/logs
mkdir -p "$ROOT"
# size caps (bytes)
CAP_TRACES=$((3*1024*1024*1024))
CAP_MISC=$((500*1024*1024))
trim_file(){
  local f="$1" cap="$2"
  [ -f "$f" ] || return 0
  local sz
  sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
  if [ "$sz" -le "$cap" ]; then return 0; fi
  # keep last ~70% lines when over cap
  local lines keep
  lines=$(wc -l < "$f" || echo 0)
  keep=$(( lines * 70 / 100 ))
  tail -n "$keep" "$f" > "$f.tmp" && mv "$f.tmp" "$f"
}
trim_file "$ROOT/pipeline_traces.jsonl" "$CAP_TRACES"
trim_file "$ROOT/jess_memory_manager.log" "$CAP_MISC"
trim_file "$ROOT/jess_runtime_guard.log" "$CAP_MISC"
trim_file "$ROOT/jess_keeper.log" "$CAP_MISC"
trim_file "$ROOT/jess_keeper_errors.log" "$CAP_MISC"
