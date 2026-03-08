#!/usr/bin/env bash
# Quick health check - one command for everything
# Usage: /health or ./quick-health.sh

WORKSPACE="/home/pmello/.openclaw/workspace-q35"

echo "=== Quick Health Check ==="
echo "Time: $(date)"
echo ""

echo "🔌 Gateway:"
curl -s --max-time 2 http://127.0.0.1:18789/health 2>&1 | head -1
echo ""

echo "🤖 Model:"
curl -s --max-time 2 http://127.0.0.1:18080/health 2>&1 | head -1
echo ""

echo "📊 System:"
echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)"
echo "RAM: $(free -h | grep Mem | awk '{print $2" total, "$3" used"}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $5" used"}')"
echo ""

echo "⚡ OpenClaw Status:"
openclaw status --deep 2>&1 | grep -E "(Gateway|Sessions|Memory)" | head -3
echo ""

echo "📈 Runtime State:"
if [[ -f "$WORKSPACE/RUNTIME.md" ]]; then
    grep -E "(State Age|Gateway Latency)" "$WORKSPACE/RUNTIME.md" | sed 's/^\*\*//' | sed 's/\*\*:/:/' | sed 's/$/ /'
fi