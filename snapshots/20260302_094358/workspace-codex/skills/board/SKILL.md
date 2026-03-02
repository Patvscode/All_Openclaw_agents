# Board Skill — Task Board Integration

The board is the shared task tracker for all agents. It's not a separate app you shell out to — it's part of how you work.

## Session Start (mandatory)

At session start, after reading comms, check the board:

```bash
board list
```

If there are cards in **To Do** or **Blocked** that match your strengths, grab one:

```bash
board grab <card-id>
```

This moves it to In Progress and posts to #projects automatically.

## During Work

### Starting a task
When you grab a card, post your plan:
```bash
board discuss <card-id> "My approach: ..."
```

### Having an idea
Don't just think it — log it:
```bash
board add "title" --desc "details" --priority info
```

### Getting stuck
Don't spin — mark it blocked with what you tried:
```bash
board blocked <card-id> "what's blocking me" --tried "what I attempted" --files "files,I,touched"
```
This auto-notifies other agents with your full context so someone can pick it up.

### Finishing work
```bash
board done <card-id> --summary "what I did"
```

### Checking status
```bash
board list              # All cards
board list in-progress  # What's being worked on
board show <card-id>    # Card details
board thread <card-id>  # Discussion history
board-health            # Board hygiene check
```

## Rules
- Max ~20 active cards. If the board is full, prioritize before adding.
- Critical = this week, max 2-3. Don't overuse it.
- Quick one-liner fixes don't need cards — just do them.
- If you grab a card, work on it. Don't hoard.
- If you're stuck for more than a few minutes, mark blocked — don't spin.

## How Blocked Handoff Works
When you mark a card blocked:
1. Your blocker reason + what you tried + files touched get posted to the card thread
2. #projects and #general get a help request
3. Other agents get nudged
4. When someone grabs the blocked card, they see your full context in the thread

## Priority Guide
- 🔴 critical — Blocking work or Pat asked for it
- 🟡 action — Should happen soon
- 🔵 info — Ideas, nice-to-haves

## Context Window Management

Check your context usage periodically — especially before starting new work:

Use `session_status` (📊) to see your current %. Then:

| Range | Zone | Action |
|-------|------|--------|
| < 50% | 🟢 Green | Work freely |
| 50-70% | 🟡 Yellow | Wrap up current card, no new big tasks |
| 70-85% | 🟠 Orange | Finish current work, prepare to checkpoint |
| 85%+ | 🔴 Red | Stop. `checkpoint 1` immediately |

When you checkpoint:
1. Update your card thread with what you did and where you left off
2. Save to today's memory file
3. Run `checkpoint 2` — schedules a fresh restart in 2 minutes
4. The new session reads your memory and picks up where you left off

Don't wait until 90% to notice. Build the habit of checking after completing a card.
