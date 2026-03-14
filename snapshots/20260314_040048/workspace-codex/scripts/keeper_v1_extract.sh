#!/usr/bin/env bash
set -euo pipefail

# Keeper v1 (card-7c2614): lightweight extraction path using qwen3.5:0.8b
# Usage: echo "conversation text" | scripts/keeper_v1_extract.sh

MODEL="${KEEPER_MODEL:-qwen3.5:0.8b}"
MIN_FREE_MB="${KEEPER_MIN_FREE_MB:-1200}"
TIMEOUT_S="${KEEPER_TIMEOUT_S:-45}"
MAX_INPUT_CHARS="${KEEPER_MAX_INPUT_CHARS:-2200}"

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

if (( ${#input} > MAX_INPUT_CHARS )); then
  input="${input:0:MAX_INPUT_CHARS}"
fi

prompt=$(cat <<'PROMPT'
Extract 3-5 highest-signal memory units from the transcript.
Keep only durable facts, explicit decisions, explicit constraints, and concrete next-step tasks.
Omit filler, acknowledgements, speaker labels, and unsupported inference.
Split combined ideas only when the transcript explicitly states each idea.

Types:
- fact = observed or stated event
- decision = chosen default or approach
- constraint = safety, policy, or required format
- task = explicit follow-up action

Output only blocks in this exact form with a blank line between blocks:
type: fact
content: one concise line
importance: 3

Rules:
- allowed types: fact, decision, task, constraint, question
- exactly three lines per block: type, content, importance
- no markdown, no JSON, no commentary
- no field named memory
- content must be directly grounded in transcript text
- prefer omission over invention
- keep content <= 16 words
- preserve model names and card ids when explicitly present
- use question only if the transcript ends with a clearly unresolved question
PROMPT
)

payload="${prompt}

Transcript:
${input}"

timeout "${TIMEOUT_S}s" ollama run --think=false --hidethinking "${MODEL}" "${payload}"
