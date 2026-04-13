#!/usr/bin/env bash
# Daily runtime summary - captures state for tracking trends
# Usage: ./daily-summary.sh

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
DATE=$(date '+%Y-%m-%d')
SUMMARY_FILE="$WORKSPACE/summaries/daily-$DATE.md"

mkdir -p "$WORKSPACE/summaries"

# Get current state
"$WORKSPACE/scripts/update-runtime.sh" >/dev/null 2>&1

cat > "$SUMMARY_FILE" << EOF
# Daily Runtime Summary - $DATE

## Morning Check
\`\`\`bash
$(date '+%H:%M:%S') - Initial state captured
\`\`\`

EOF

# Append key metrics
echo "### Current State" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
grep -A 20 "^## ⚡ Status Check" "$WORKSPACE/RUNTIME.md" >> "$SUMMARY_FILE" 2>/dev/null || echo "No runtime data available" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

# Add commands for reference
cat >> "$SUMMARY_FILE" << EOF

### Useful Commands
- \`/status\` - Quick OpenClaw status
- \`/runtime\` - Full runtime check
- \`/compact\` - Compact sessions
- \`/restart\` - Restart gateway
- \`/health\` - Service health check
- \`./quick-health.sh\` - One-command health

### Notes
- Log any issues or actions taken
- Update this file throughout the day
- Compare with previous days in \`summaries/\`
EOF

echo "✓ Daily summary created: $SUMMARY_FILE"