#!/usr/bin/env bash
# Handle runtime commands via Telegram message
# Usage: ./runtime-commands.sh <command>

CMD="$1"
WORKSPACE="/home/pmello/.openclaw/workspace-q35"

case "$CMD" in
    /runtime)
        # Trigger full runtime check
        "$WORKSPACE/scripts/update-runtime.sh" 2>&1 | grep -v "✓ Runtime tracking"
        ;;
    /status)
        # Quick status report
        echo "OpenClaw Status:"
        openclaw status --deep 2>&1 | head -15
        ;;
    /compact)
        # Compact sessions
        "$WORKSPACE/scripts/runtime-actions.sh compact"
        ;;
    /reset)
        # Reset session
        "$WORKSPACE/scripts/runtime-actions.sh reset-session"
        ;;
    /restart)
        # Restart runtime
        "$WORKSPACE/scripts/runtime-actions.sh restart-runtime"
        ;;
    /smoke)
        # Run smoke test
        "$WORKSPACE/scripts/runtime-actions.sh smoke-test"
        ;;
    /health)
        # Health check
        echo "Gateway: $(curl -s http://127.0.0.1:18789/health)"
        echo "Model: $(curl -s http://127.0.0.1:18080/health)"
        ;;
    *)
        echo "Unknown command: $CMD"
        echo "Available: /runtime /status /compact /reset /restart /smoke /health"
        exit 1
        ;;
esac