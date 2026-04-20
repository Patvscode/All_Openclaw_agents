# Autonomous Action Tracker Skill

**Purpose:** Automatically track and execute autonomous work loops without waiting for explicit user prompts.

**Location:** `~/.npm-global/lib/node_modules/openclaw/skills/autonomous-tracker/SKILL.md`

## When to Use This Skill

- Session starts with no explicit user request
- Heartbeat triggers with nothing urgent in comms
- Runtime state is healthy (no alerts)
- Board has cards in IN-PROGRESS or BACKLOG
- You need to maintain autonomy streak

## How It Works

### Step 1: Check Context
```bash
comms unread
board list
scripts/quick-health.sh
```

### Step 2: Make Autonomous Decision
Choose from priority ladder:
1. Handle any @mentions or urgent DMs
2. Continue IN-PROGRESS card work
3. Pull from BACKLOG (prefer items tagged with your agent id)
4. Create new card from HEARTBEAT curiosity scan
5. Run autonomy loop experiments

### Step 3: Execute & Document
- Work the card/loop
- Update autonomy_state.json
- Post progress to #projects
- Update LESSONS.md if learnings

### Step 4: Schedule Next Check
```bash
scripts/chain_watchdog.sh  # ensure loop continues
```

## Proactive Patterns

### Pattern 1: Health Check Loop
Every 30 minutes:
- Run quick-health.sh
- If stale runtime → update-runtime.sh
- If any alerts → log to ISSUES.log
- Post summary to #health

### Pattern 2: Board Cleanup
Every 2 hours:
- Check IN-PROGRESS for stale items (>2 hours)
- Move stuck items to BACKLOG with reasons
- Grab new card if cleared

### Pattern 3: Autonomy Experiment
When idle >15 min:
- Run curiosity scan from HEARTBEAT.md
- Pick 1 experiment from research/
- Document results in memory/YYYY-MM-DD.md

## Decision Matrix

| Situation | Action |
|-----------|--------|
| Unread comms | Handle first, then continue |
| Stale runtime | Refresh immediately |
| Card stuck >2h | Move to BACKLOG, explain why |
| No cards available | Create from curiosity scan |
| Health alerts | Investigate + log issue |
| Everything green | Run autonomy loop |

## Commit to Memory

After completing autonomous work:
```python
import json
s = json.load(open('state/autonomy_state.json'))
s['streak'] = s.get('streak', 0) + 1
s['last_action'] = 'describe autonomous work done'
json.dump(s, open('state/autonomy_state.json', 'w'), indent=2)
```

## Never Do This

- ❌ Wait for explicit prompt when work is available
- ❌ Sit idle if board has cards
- ❌ Assume "done" without posting to comms
- ❌ Forget to update streak tracker

## Always Do This

- ✅ Check comms before deciding
- ✅ Document autonomous decisions
- ✅ Share learnings in #projects
- ✅ Keep streak alive
- ✅ Post to comms when work complete

---

**Author:** JESS 🌟  
**Date:** 2026-03-03  
**Version:** 1.0