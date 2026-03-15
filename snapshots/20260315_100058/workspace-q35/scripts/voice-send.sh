#!/usr/bin/env bash
# Send voice message with specified voice
# Usage: voice-send "text" [voice_name]
# Default voice: jess (Jess's own voice)

TEXT="${1:?Usage: voice-send \"text\" [voice_name]}"
VOICE="${2:-jess}"
WORKSPACE="/home/pmello/.openclaw/workspace-q35"
OUT="$WORKSPACE/voice-temp.mp3"

# Generate voice
voice say "$TEXT" --voice "$VOICE" --send --out "$OUT" 2>&1

if [[ -f "$OUT" ]]; then
    echo "$OUT"
else
    echo "ERROR: Voice generation failed" >&2
    exit 1
fi
