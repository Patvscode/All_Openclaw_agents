#!/bin/bash
# Focused Keeper Benchmark - One Model at a Time

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
RESULTS="$WORKSPACE/state/keeper_benchmark_v3.txt"

echo "=== Keeper Benchmark v3 (Sequential) ===" > "$RESULTS"
echo "Timestamp: $(date -Iseconds)" >> "$RESULTS"
echo "" >> "$RESULTS"

PROMPT="Extract 3 memory units as simple lines:
- type: fact, content: Jess working on Memory Coprocessor, importance: 5
- type: task, content: Benchmark small models, importance: 4
- type: constraint, content: Local-first execution, importance: 5"

MODELS=(
    "qwen3.5:0.8b"
    "qwen3.5:2b"
    "qwen3.5:4b"
    "qwen3.5:9b"
)

for model in "${MODELS[@]}"; do
    echo "" >> "$RESULTS"
    echo "--- $model ---" >> "$RESULTS"
    
    echo "Testing $model (pulling if needed)..."
    ollama pull "$model" --quiet 2>/dev/null
    
    START=$(date +%s.%N)
    OUTPUT=$(timeout 60 ollama run "$model" "$PROMPT" 2>&1)
    END=$(date +%s.%N)
    
    DURATION=$(echo "$END - $START" | bc 2>/dev/null || echo "N/A")
    
    # Count extracted units
    LINES=$(echo "$OUTPUT" | grep -c "^-" 2>/dev/null || echo "0")
    
    # Check if it followed instructions
    HAS_TYPE=$(echo "$OUTPUT" | grep -c "type:" 2>/dev/null || echo "0")
    
    echo "Duration: ${DURATION}s" >> "$RESULTS"
    echo "Extracted lines: $LINES" >> "$RESULTS"
    echo "Has 'type:' field: $HAS_TYPE" >> "$RESULTS"
    
    echo "  $model: ${DURATION}s, $LINES units, type:$HAS_TYPE"
    
    # Clean up
    ollama rm "$model" --quiet 2>/dev/null
done

echo "" >> "$RESULTS"
echo "=== Complete ===" >> "$RESULTS"

echo ""
cat "$RESULTS"
echo ""
echo "Results saved to: $RESULTS"