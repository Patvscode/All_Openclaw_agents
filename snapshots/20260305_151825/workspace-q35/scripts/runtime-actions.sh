#!/usr/bin/env bash
# Runtime action commands
# Usage: ./runtime-actions.sh <action>
# Actions: compact | reset-session | restart-runtime | smoke-test

ACTION="$1"
case "$ACTION" in
    compact)
        echo "💾 Compacting sessions..."
        openclaw sessions compact 2>&1 | tail -5
        ;;
    reset-session)
        echo "🔄 Resetting default session..."
        openclaw session reset 2>&1 | tail -5
        ;;
    restart-runtime)
        echo "🔄 Restarting runtime..."
        systemctl restart openclaw-gateway
        sleep 2
        openclaw status --deep 2>&1 | head -10
        ;;
    smoke-test)
        echo "🔥 Running smoke test..."
        echo "1. Gateway health:"
        curl -s --max-time 2 http://127.0.0.1:18789/health
        echo -e "\n2. Model health:"
        curl -s --max-time 2 http://127.0.0.1:18080/health
        echo -e "\n3. Quick query:"
        curl -s http://127.0.0.1:18080/v1/chat/completions \
            -H 'Content-Type: application/json' \
            -d '{"model":"qwen3.5-35b-a3b-q8","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
        ;;
    *)
        echo "Usage: $0 {compact|reset-session|restart-runtime|smoke-test}"
        exit 1
        ;;
esac