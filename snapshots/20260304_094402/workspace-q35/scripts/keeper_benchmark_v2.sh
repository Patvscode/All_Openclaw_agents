#!/bin/bash
# Memory Coprocessor Benchmark - Simplified Test

WORKSPACE="/home/pmello/.openclaw/workspace-q35"

echo "=== Keeper Benchmark v2 (Structured Text) ==="
echo "Timestamp: $(date -Iseconds)" > "$WORKSPACE/state/keeper_benchmark_v2.txt"
echo "" >> "$WORKSPACE/state/keeper_benchmark_v2.txt"

MODELS=(
    "qwen3.5:0.8b"
    "qwen3.5:2b"
    "qwen3.5:4b"
    "qwen3.5:9b"
)

PROMPT="You are a memory coprocessor. Extract 3 memory units as simple text lines:
- type: fact/decision/task, content: ..., importance: 1-5

Context: Jess working on Memory Coprocessor research for Pat."

for model in "${MODELS[@]}"; do
    echo "Testing $model..."
    
    START=$(date +%s.%N)
    OUTPUT=$(timeout 30 ollama run "$model" "$PROMPT" 2>&1)
    END=$(date +%s.%N)
    
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "N/A")
    LINES=$(echo "$OUTPUT" | grep -c "^-" || echo "0")
    
    echo "{\"model\":\"$model\",\"duration\":\"$DURATION\",\"lines_extracted\":$LINES}" >> "$WORKSPACE/state/keeper_benchmark_v2.txt"
    echo "  $model: ${DURATION}s, $LINES units"
done

echo "" >> "$WORKSPACE/state/keeper_benchmark_v2.txt"
echo "=== Complete ===" >> "$WORKSPACE/state/keeper_benchmark_v2.txt"

echo ""
echo "Results saved to: $WORKSPACE/state/keeper_benchmark_v2.txt"
cat "$WORKSPACE/state/keeper_benchmark_v2.txt"