#!/usr/bin/env bash
# Check and consume nudge flags with rate limiting (card-014)
FLAG="/home/pmello/.openclaw/comms/.nudge_q35"
RATE_LIMIT_MINUTES=10  # Configurable rate limit

if [[ -f "$FLAG" ]]; then
    # Check if flag is JSON format (new) or plain text (legacy)
    if head -c 1 "$FLAG" | grep -q '{'; then
        # JSON format with metadata
        last_nudge=$(jq -r '.last_nudge // 0' "$FLAG" 2>/dev/null)
        urgency=$(jq -r '.urgency // "normal"' "$FLAG" 2>/dev/null)
        message=$(jq -r '.message // "Check comms now"' "$FLAG" 2>/dev/null)
        count=$(jq -r '.count // 1' "$FLAG" 2>/dev/null)
        
        if [[ -n "$last_nudge" && "$last_nudge" != "0" ]]; then
            current_time=$(date +%s)
            minutes_since=$(( (current_time - last_nudge) / 60 ))
            
            # Always show and clear when check_nudge.sh is run
            # Rate limiting is server-side to coalesce rapid nudges
            echo "📬 NUDGE (${count} coalesced): $message"
            rm -f "$FLAG"
        else
            # Legacy or malformed JSON - show and clear
            echo "📬 NUDGE: $(cat "$FLAG")"
            rm -f "$FLAG"
        fi
    else
        # Plain text legacy format
        echo "📬 NUDGE: $(cat "$FLAG")"
        rm -f "$FLAG"
    fi
else
    echo "No pending nudges"
fi
