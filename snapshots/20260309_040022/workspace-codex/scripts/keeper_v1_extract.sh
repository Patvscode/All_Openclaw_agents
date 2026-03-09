#!/usr/bin/env bash
set -euo pipefail

# Keeper v1 (card-7c2614): lightweight extraction path using qwen3.5:0.8b
# Usage: echo "conversation text" | scripts/keeper_v1_extract.sh

MODEL="${KEEPER_MODEL:-qwen3.5:0.8b}"
MIN_FREE_MB="${KEEPER_MIN_FREE_MB:-1200}"
TIMEOUT_S="${KEEPER_TIMEOUT_S:-90}"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "missing required command: $1" >&2; exit 1; }
}

require_cmd ollama
require_cmd timeout
require_cmd awk

free_mb=$(awk '/MemAvailable:/ {print int($2/1024)}' /proc/meminfo)
if [[ -z "${free_mb}" ]]; then
  echo "unable to read MemAvailable from /proc/meminfo" >&2
  exit 1
fi

if (( free_mb < MIN_FREE_MB )); then
  echo "guardrail: low memory (${free_mb}MB < ${MIN_FREE_MB}MB), skipping keeper run" >&2
  exit 2
fi

input="$(cat)"
if [[ -z "${input// }" ]]; then
  echo "no input provided" >&2
  exit 3
fi

prompt=$(cat <<'PROMPT'
Extract up to 8 atomic memory units from the transcript.
Return ONLY blocks in this exact text format:

type: <fact|decision|task|constraint|question>
content: <one concise line>
importance: <1-5>

Rules:
- No markdown, no JSON.
- High signal only.
- Merge duplicates.
PROMPT
)

payload="${prompt}

Transcript:
${input}"

timeout "${TIMEOUT_S}s" ollama run "${MODEL}" "${payload}"
