#!/usr/bin/env bash
set -euo pipefail

DAYS="${1:-14}"
BASE_DIR="${2:-/home/pmello/mempalace_stage2_corpus}"
MEMPALACE_BIN="${MEMPALACE_BIN:-/home/pmello/.venvs/mempalace/bin/mempalace}"
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
AGENTS=(codex main gemma)
WORKSPACES=(codex gemma main)
DOC_FILES=(AGENTS.md USER.md MEMORY.md RESUME.md SHARED_CONTEXT.md SOUL.md TOOLS.md LESSONS.md AGENT_PLAYBOOK.md CODEX_RUNBOOK.md WORKSPACE_MAP.md DREAMS.md)

need_bin() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing required binary: $1" >&2; exit 1; }
}

copy_tree() {
  local src="$1"
  local dst="$2"
  [ -d "$src" ] || return 0
  mkdir -p "$dst"
  rsync -a \
    --exclude '.git/' \
    --exclude 'node_modules/' \
    --exclude 'venv/' \
    --exclude '.venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.openclaw/' \
    --exclude 'memory/' \
    --exclude 'artifacts/' \
    --exclude 'tmp/' \
    --exclude 'state/' \
    "$src"/ "$dst"/
}

need_bin jq
need_bin rsync
[ -x "$MEMPALACE_BIN" ] || { echo "Missing mempalace binary: $MEMPALACE_BIN" >&2; exit 1; }

rm -rf "$BASE_DIR"
mkdir -p "$BASE_DIR"/{sessions/codex,sessions/main,sessions/gemma,shared/codex,shared/gemma,shared/main,code/codex,code/gemma,code/shared}

for agent in "${AGENTS[@]}"; do
  src="$OPENCLAW_DIR/agents/$agent/sessions"
  dst="$BASE_DIR/sessions/$agent"
  [ -d "$src" ] || continue
  while IFS= read -r -d '' file; do
    base="$(basename "$file" .jsonl)"
    jq -r '
      select(.type=="message")
      | .message as $m
      | ($m.role // "unknown") as $role
      | ($m.content // [])[]?
      | select(.type=="text")
      | "[" + $role + "]\n" + .text + "\n"
    ' "$file" > "$dst/$base.md" || true
    [ -s "$dst/$base.md" ] || rm -f "$dst/$base.md"
  done < <(find "$src" -maxdepth 1 -type f -name '*.jsonl' ! -name '*.checkpoint.*' ! -name '*.deleted.*' -mtime "-$DAYS" -print0 | sort -z)
done

for ws in "${WORKSPACES[@]}"; do
  wdir="$OPENCLAW_DIR/workspace-$ws"
  target="$BASE_DIR/shared/$ws"
  [ -d "$wdir" ] || continue
  mkdir -p "$target"
  for f in "${DOC_FILES[@]}"; do
    [ -f "$wdir/$f" ] && cp -a "$wdir/$f" "$target/"
  done
  if [ -d "$wdir/memory" ]; then
    find "$wdir/memory" -maxdepth 1 -type f -name '*.md' -mtime -$((DAYS + 7)) -exec cp -a {} "$target/" \;
  fi
done

[ -f "$OPENCLAW_DIR/AGENT_BOARD.md" ] && cp -a "$OPENCLAW_DIR/AGENT_BOARD.md" "$BASE_DIR/shared/"

copy_tree "$OPENCLAW_DIR/workspace-codex/scripts" "$BASE_DIR/code/codex/scripts"
copy_tree "$OPENCLAW_DIR/workspace-codex/skills" "$BASE_DIR/code/codex/skills"
copy_tree "$OPENCLAW_DIR/workspace-gemma/scripts" "$BASE_DIR/code/gemma/scripts"
copy_tree "$OPENCLAW_DIR/workspace-gemma/skills" "$BASE_DIR/code/gemma/skills"

cat > "$BASE_DIR/README.md" <<EOF
Stage 2 MemPalace corpus

Generated: $(date)
Lookback days: $DAYS
Includes: text-exported sessions for codex/main/gemma, shared workspace memory/docs, filtered durable code from scripts/ and skills/
EOF

printf 'Export complete for %s\n' "$BASE_DIR"
printf '  sessions: %s\n' "$(find "$BASE_DIR/sessions" -type f | wc -l | tr -d ' ')"
printf '  shared:   %s\n' "$(find "$BASE_DIR/shared" -type f | wc -l | tr -d ' ')"
printf '  code:     %s\n' "$(find "$BASE_DIR/code" -type f | wc -l | tr -d ' ')"

[ -f "$BASE_DIR/mempalace.yaml" ] || "$MEMPALACE_BIN" init "$BASE_DIR" --yes >/dev/null
"$MEMPALACE_BIN" mine "$BASE_DIR"
"$MEMPALACE_BIN" status
