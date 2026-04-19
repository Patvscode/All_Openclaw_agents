# OC-Control — OpenClaw Service Control Skill

## Purpose
Inspect, control, and audit the OpenClaw/AI service stack via the systemd control sheet architecture. This skill understands the full hierarchy: control sheet → apply script → targets → services → timers → watchdogs → cron.

## Key Principle
**This skill operates on the agent's own runtime stack.** Mistakes can kill the gateway, model server, or agent sessions. Always inspect before acting.

## Quick Commands

### Inspect current state
```bash
# Full drift check — desired vs actual
python3 ~/openclaw-systemd/scripts/oc-drift-check.py

# What's actually running (our stuff only)
systemctl --user list-units --type=service --state=running --no-legend | grep -vE 'gnome|evolution|gvfs|dbus|pipewire|wire|tracker|xdg|snap|gcr|dconf|at-spi'

# What's enabled (auto-starts at login)
systemctl --user list-unit-files --state=enabled --no-legend

# Active timers
systemctl --user list-timers --no-legend
```

### Edit the switchboard
```bash
oc-sheet                    # Interactive menu
cat ~/openclaw-systemd/control-sheet.conf   # View raw
```

### Apply control sheet
```bash
python3 ~/openclaw-systemd/scripts/apply-control-sheet.py
```

### Verify after apply
```bash
python3 ~/openclaw-systemd/scripts/oc-drift-check.py
```

## Architecture

```
control-sheet.conf  ──→  apply-control-sheet.py  ──→  systemd + cron
       ↑                                                    ↓
  oc-sheet CLI                                    actual running state
                                                        ↓
                                              oc-drift-check.py (audit)
```

### Source of Truth
`~/openclaw-systemd/control-sheet.conf`
- `x` = on
- blank = inherit group default (off unless group is x)
- `-` = force off

### Groups
| Group | Target | Controls |
|-------|--------|----------|
| [extended] | openclaw-extended.target | Platform APIs, UIs, labs, autopilot, helpers |
| [core] | openclaw-core.target | Gateway, Node |
| [models] | openclaw-models.target | llama.cpp, model-control |
| [research] | openclaw-research.target | ARC, autoresearch, research-engine |
| [ai_timers] | openclaw-ai-timers.target | Jess timers, knowledge timers |
| [system_services] | *(none)* | model-supervisor (sudo) |
| [maintenance_timers] | *(none)* | backup, indexer, audit timers |
| [cron_jobs] | *(none)* | 3 periodic python scripts |
| [ollama] | *(none)* | ollama.service (sudo) |

### Revival Paths (things that can bring "off" services back)
1. **Restart= policy** — gateway (always), jess-q35 (on-failure)
2. **Watchdog timer** — jess-watchdog restarts jess-q35 + gateway unconditionally
3. **Independently enabled** — services with WantedBy=default.target restart at login
4. **Timer auto-start** — enabled timers fire at login even if target is stopped

## Runbook: Adding a New Service

When a new service is discovered:

1. **Inspect** — `systemctl --user cat <unit>` to see ExecStart, Restart=, After=, Wants=
2. **Identify scope** — user-scope (most) or system-scope (needs sudo)?
3. **Identify group** — Which control sheet section does it belong to?
4. **Check revival paths** — Is it enabled? Does anything Wants= or Restart= it?
5. **Add to control-sheet.conf** — Under the correct `[section]`, add `<unit>=`
6. **Add to target** — If it belongs to a target group, add to the target's Wants= and After= lines
7. **Disable independent startup** — `systemctl --user disable <unit>` so only the target controls it
8. **Apply** — `python3 ~/openclaw-systemd/scripts/apply-control-sheet.py`
9. **Verify** — `python3 ~/openclaw-systemd/scripts/oc-drift-check.py`
10. **Document** — Update ARCHITECTURE.md if significant

## Files

| File | Purpose |
|------|---------|
| `~/openclaw-systemd/control-sheet.conf` | Source of truth |
| `~/openclaw-systemd/scripts/apply-control-sheet.py` | Applies desired state |
| `~/openclaw-systemd/scripts/oc-drift-check.py` | Audits drift |
| `~/openclaw-systemd/scripts/oc-sheet-cli.py` | Interactive menu |
| `~/openclaw-systemd/targets/` | Target unit files |
| `~/openclaw-systemd/ARCHITECTURE.md` | Full architecture doc |
| `~/.config/systemd/user/` | Live unit files |

## Safety Rules

- **Never rename unit files**
- **Inspect before acting** — `systemctl --user status <unit>` first
- **The apply script affects your own runtime** — gateway/model death kills agent sessions
- **Verify after every change** — run drift check
- **Prefer disable+stop over just stop** — stop alone is temporary
