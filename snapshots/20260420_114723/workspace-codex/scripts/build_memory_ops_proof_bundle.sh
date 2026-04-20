#!/usr/bin/env bash
set -euo pipefail

ARTIFACT_DIR="/home/pmello/.openclaw/workspace-codex/artifacts"
OUT_DIR="${ARTIFACT_DIR}/proof_bundles"
mkdir -p "$OUT_DIR"

stamp="$(date +%Y%m%d_%H%M%S)"
bundle_dir="${OUT_DIR}/memory_ops_state_machine_${stamp}"
mkdir -p "$bundle_dir"

latest_live="$(ls -1t "$ARTIFACT_DIR"/memory_ops_state_machine_*.jsonl 2>/dev/null | head -n1 || true)"
latest_degraded="$(ls -1t "$ARTIFACT_DIR"/memory-ops-degraded-recovery-*.jsonl 2>/dev/null | head -n1 || true)"
latest_runtime="$(ls -1t "$ARTIFACT_DIR"/memory_ops_runtime_validation.json 2>/dev/null | head -n1 || true)"

copy_if_present() {
  local src="$1"
  [[ -n "$src" && -f "$src" ]] || return 0
  cp "$src" "$bundle_dir/"
}

copy_if_present "$latest_live"
copy_if_present "$latest_degraded"
copy_if_present "$latest_runtime"

summary_file="$bundle_dir/SUMMARY.md"
{
  echo "# Memory Ops State-Machine Proof Bundle"
  echo
  echo "Generated: $(date -Is)"
  echo
  echo "## Included artifacts"
  for f in "$bundle_dir"/*; do
    [[ -f "$f" ]] || continue
    bn="$(basename "$f")"
    [[ "$bn" == "SUMMARY.md" ]] && continue
    echo "- $bn"
  done
  echo

  if [[ -f "$bundle_dir/$(basename "$latest_degraded")" ]]; then
    echo "## DEGRADED→RECOVERY evidence"
    jq -r 'select(.transition!=null) | .transition' "$bundle_dir/$(basename "$latest_degraded")" | sort | uniq -c | sed 's/^/- /' || true
    echo
  fi

  if [[ -f "$bundle_dir/$(basename "$latest_live")" ]]; then
    echo "## Latest live state distribution"
    jq -r '.state' "$bundle_dir/$(basename "$latest_live")" | sort | uniq -c | sed 's/^/- /' || true
    echo
  fi

  echo "## Next manual checks"
  echo "- Verify desktop Memory Ops panel transition log shows expected edges"
  echo "- Verify mobile Memory Ops panel transition log shows expected edges"
} > "$summary_file"

echo "$bundle_dir"