#!/bin/bash
# Memory Coprocessor Model Benchmark Harness
# Compares Qwen3.5 small models vs Phi3 for context-pack extraction

set -e

WORKSPACE="/home/pmello/.openclaw/workspace-q35"
RESULTS_FILE="$WORKSPACE/state/keeper_benchmark_results.jsonl"
PROMPT_FILE="$WORKSPACE/scripts/keeper_extraction_prompt.txt"

# Structured extraction prompt for memory tasks
cat > "$PROMPT_FILE" << 'PROMPT'
You are a memory coprocessor. Extract structured memory units from the conversation.

Format as JSON lines with these fields:
- type: fact|decision|task|unresolved|constraint
- content: the extracted information
- importance: 1-5 (5=highest)
- durability: short|medium|long
- dependencies: [list of related IDs if any]

Conversation context:
- User: Patrick Mello (Pat)
- Current focus: Agent comms platform, Memory Ops state-machine, AI-Scientist research
- Active cards: Memory Coprocessor (Keeper v2), Comms-v2 UI upgrade
- Constraints: Local-first execution, compute-aware, sustainability

Extract 5-10 atomic memory units from recent conversation state.
PROMPT

echo "=== Memory Coprocessor Benchmark ===" > "$RESULTS_FILE"
echo "Timestamp: $(date -Iseconds)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"

MODELS=(
    "qwen3.5:0.8b"
    "qwen3.5:2b"
    "qwen3.5:4b"
    "qwen3.5:9b"
    "phi3:latest"
)

for model in "${MODELS[@]}"; do
    echo "Testing $model..."
    
    START_TIME=$(date +%s.%N)
    
    OUTPUT=$(ollama run "$model" "$PROMPT" 2>&1)
    
    END_TIME=$(date +%s.%N)
    DURATION=$(echo "$END_TIME - $START_TIME" | bc)
    
    # Count extracted units
    UNITS=$(echo "$OUTPUT" | grep -c "type:" || echo "0")
    
    # Check JSON validity
    VALID="false"
    if echo "$OUTPUT" | python3 -c "import sys,json; [json.loads(l) for l in sys.stdin if l.strip()]" 2>/dev/null; then
        VALID="true"
    fi
    
    echo "{\"model\":\"$model\",\"duration_sec\":$DURATION,\"units_extracted\":$UNITS,\"json_valid\":$VALID,\"timestamp\":\"$(date -Iseconds)\"}" >> "$RESULTS_FILE"
    
    echo "  ✓ Duration: ${DURATION}s, Units: $UNITS, Valid JSON: $VALID"
done

echo "" >> "$RESULTS_FILE"
echo "=== Benchmark Complete ===" >> "$RESULTS_FILE"
echo "Results saved to: $RESULTS_FILE"

# Display summary
echo ""
echo "=== Benchmark Summary ==="
cat "$RESULTS_FILE" | tail -n +4 | python3 -c "
import sys, json
results = []
for line in sys.stdin:
    if line.strip():
        results.append(json.loads(line))

print(f\"{'Model':<15} {'Duration':>10} {'Units':>8} {'Valid JSON':>10}\")
print('-' * 45)
for r in results:
    print(f\"{r['model']:<15} {r['duration_sec']:>10.2f}s {r['units_extracted']:>8} {str(r['json_valid']):>10}\")
"