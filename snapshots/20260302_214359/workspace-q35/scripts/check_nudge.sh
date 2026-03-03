#!/usr/bin/env bash
# Check and consume nudge flags from comms
FLAG="/home/pmello/.openclaw/comms/.nudge_q35"
if [[ -f "$FLAG" ]]; then
    echo "📬 NUDGE: $(cat "$FLAG")"
    rm -f "$FLAG"
else
    echo "No pending nudges"
fi
