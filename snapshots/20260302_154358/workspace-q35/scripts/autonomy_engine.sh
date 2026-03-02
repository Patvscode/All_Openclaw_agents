#!/usr/bin/env bash
set -euo pipefail

# autonomy_engine.sh — Jess's autonomous work-finding and curiosity engine
# Called by heartbeat or manually. Outputs a structured work plan.
# Jess reads this output and acts on it.

BOARD_FILE="$HOME/.openclaw/comms/board/cards.json"
COMMS="$HOME/.openclaw/comms"
RESEARCH="$HOME/research"
WORKSPACE="$HOME/.openclaw/workspace-q35"
STATE="$WORKSPACE/state/autonomy_state.json"

mkdir -p "$RESEARCH" "$(dirname "$STATE")"

# Initialize state if missing
[[ -f "$STATE" ]] || echo '{"last_action":"none","streak":0,"ideas_proposed":0,"tools_built":0,"experiments_run":0}' > "$STATE"

echo "🧠 AUTONOMY ENGINE — $(date '+%H:%M %Z')"
echo ""

# 1. CHECK FOR URGENT COMMS
UNREAD=$(comms unread 2>/dev/null | grep -c "📬" || echo 0)
if [[ "$UNREAD" -gt 0 ]]; then
    echo "📬 URGENT: $UNREAD unread channels/DMs — handle these FIRST"
    comms unread 2>/dev/null
    echo ""
fi

# 2. CHECK NUDGE FLAGS
NUDGE_FILE="$COMMS/.nudge_q35"
if [[ -f "$NUDGE_FILE" ]]; then
    echo "⚡ NUDGE: $(cat "$NUDGE_FILE")"
    rm -f "$NUDGE_FILE"
    echo ""
fi

# 3. CHECK IN-PROGRESS CARDS
MY_CARDS=$(python3 -c "
import json
cards = json.load(open('$BOARD_FILE'))
mine = [c for c in cards if c.get('assignee') == 'q35' and c.get('column') == 'in-progress']
for c in mine:
    print(f'  🔨 [{c[\"id\"]}] {c[\"title\"]} (priority: {c.get(\"priority\",\"?\")})')
if not mine:
    print('NONE')
" 2>/dev/null)

if [[ "$MY_CARDS" != "NONE" ]]; then
    echo "🔨 YOUR ACTIVE WORK:"
    echo "$MY_CARDS"
    echo "ACTION: Continue working on your in-progress card(s). Post updates via board discuss."
    echo ""
else
    # 4. FIND WORK TO GRAB
    echo "⚠️  No in-progress cards. MUST grab work."
    echo ""
    
    TODO=$(python3 -c "
import json
cards = json.load(open('$BOARD_FILE'))
todo = [c for c in cards if c.get('column') == 'todo' and not c.get('assignee')]
for c in todo:
    print(f'  📋 [{c[\"id\"]}] {c[\"title\"]} (priority: {c.get(\"priority\",\"?\")})')
if not todo:
    print('NONE')
" 2>/dev/null)
    
    if [[ "$TODO" != "NONE" ]]; then
        echo "📋 AVAILABLE CARDS:"
        echo "$TODO"
        echo "ACTION: Grab the highest-priority card: board grab <card-id>"
    else
        echo "📋 No unassigned todo cards."
        echo "ACTION: Create a new card from your ideas or research, then grab it."
    fi
    echo ""
fi

# 5. CURIOSITY SCAN — look for things to improve
echo "🔍 CURIOSITY SCAN:"

# Check for files that haven't been updated recently
STALE_LESSONS=$(find "$WORKSPACE/LESSONS.md" -mmin +1440 2>/dev/null | wc -l)
[[ "$STALE_LESSONS" -gt 0 ]] && echo "  💡 LESSONS.md hasn't been updated in 24h+ — review and add new learnings"

STALE_MEMORY=$(find "$WORKSPACE/MEMORY.md" -mmin +1440 2>/dev/null | wc -l)  
[[ "$STALE_MEMORY" -gt 0 ]] && echo "  💡 MEMORY.md hasn't been updated in 24h+ — curate recent daily logs"

# Check research activity
RESEARCH_COUNT=$(find "$RESEARCH" -name "*.md" -mmin -1440 2>/dev/null | wc -l)
echo "  🔬 Research files updated in last 24h: $RESEARCH_COUNT"
[[ "$RESEARCH_COUNT" -eq 0 ]] && echo "  💡 No recent research — consider starting an experiment"

# Check for tools you could build
echo "  🛠️  Scan for automation opportunities:"
echo "     - Any repeated manual steps in your recent work?"
echo "     - Any comms patterns that could be automated?"
echo "     - Any board tasks that could be templated?"

# Check what other agents are doing (learn from them)
RECENT_PROJECTS=$(tail -20 "$COMMS/channels/projects/$(date +%Y-%m-%d).md" 2>/dev/null | grep -c "codex\|main" || echo 0)
[[ "$RECENT_PROJECTS" -gt 0 ]] && echo "  👀 $RECENT_PROJECTS recent project updates from other agents — read #projects for inspiration"

echo ""

# 6. GROWTH METRICS
python3 -c "
import json
s = json.load(open('$STATE'))
print('📊 GROWTH TRACKER:')
print(f'  Ideas proposed: {s.get(\"ideas_proposed\",0)}')
print(f'  Tools built: {s.get(\"tools_built\",0)}')
print(f'  Experiments run: {s.get(\"experiments_run\",0)}')
print(f'  Work streak: {s.get(\"streak\",0)} sessions')
" 2>/dev/null

echo ""
echo "Remember: Learning. Building. Growing. Improving. Autonomy."
