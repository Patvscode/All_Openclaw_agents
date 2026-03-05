# JESS Efficiency Tools

## Quick Commands

### Health & Status
- `./quick-health.sh` - One-command health check
- `./daily-summary.sh` - Create daily runtime summary
- `./log-issue.sh` - Log runtime issues
- `./pre-response-check.sh` - Check state before responding
- `./update-runtime.sh` - Refresh runtime tracking

### Runtime Actions
- `/status` - OpenClaw quick status
- `/runtime` - Full runtime check
- `/compact` - Compact sessions
- `/reset` - Reset session
- `/restart` - Restart gateway
- `/smoke` - Run smoke test
- `/health` - Service health check

### Voice (Sesame CSM-1B — local TTS on DGX Spark)
- `voice say "text" --voice jess --send` - Generate voice as Jess (warm female, pitch-tuned) → outputs mp3 path
- `voice say "text" --voice female --send` - Default female voice
- `voice say "text" --voice male --send` - Male voice
- `voice hear file.ogg` - Transcribe audio (Whisper.cpp)
- `voice hear file.ogg --translate` - Translate audio to English
- `voice voices` - List all available voices (jess, female, male, female-read, male-read, voice-c, voice-d)
- `voice prefs` - Show current voice preferences
- `voice prefer jess` - Set default voice to jess

**To send voice on Telegram:** Generate with `--send`, then use the message tool with `filePath` and `asVoice=true`.
File must be under your workspace or `~/.openclaw/media/` — copy from /tmp if needed.

**Your voice is "jess"** — use `--voice jess` when speaking as yourself.

## Files

### Tracking
- `RUNTIME.md` - Current runtime state (auto-updated)
- `DIAGNOSTICS.md` - Issue tracking and fixes
- `summaries/daily-YYYY-MM-DD.md` - Daily summaries
- `ISSUES.log` - Issue log

### Scripts
- `scripts/update-runtime.sh` - Main runtime updater
- `scripts/pre-response-check.sh` - Pre-response check
- `scripts/quick-health.sh` - Quick health check
- `scripts/daily-summary.sh` - Daily summary
- `scripts/log-issue.sh` - Issue logger
- `scripts/runtime-actions.sh` - Action commands
- `scripts/runtime-commands.sh` - Telegram commands

## Workflow

### Before Responding
1. Run `./pre-response-check.sh`
2. Check for `RUNTIME_ALERTS`
3. If stale, run `./update-runtime.sh`
4. Note state in response if needed

### Daily Routine
1. Morning: `./daily-summary.sh`
2. Throughout day: `./log-issue.sh` for any problems
3. Evening: Review `ISSUES.log` and `RUNTIME.md`

### Troubleshooting
1. `./quick-health.sh` - Get overview
2. Check `RUNTIME.md` for specific metrics
3. Run `/smoke` for service health
4. Log issue with `./log-issue.sh`

## Automation

### Auto-run on Session Start
The `pre-response-check.sh` should run automatically before every response.

### Cron Jobs (Optional)
Add to crontab for periodic checks:
```bash
# Every hour
0 * * * * ~/openclaw/workspace-q35/scripts/update-runtime.sh >/dev/null 2>&1

# Daily at 9 AM
0 9 * * * ~/openclaw/workspace-q35/scripts/daily-summary.sh >/dev/null 2>&1
```

## Reliability Checkback
- Score and cadence helper: `checkback-score <c> <i> <b> <r>`
- Script: `/home/pmello/.openclaw/tools/checkback-score.sh`
