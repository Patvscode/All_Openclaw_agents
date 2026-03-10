# Neural Lab — Pat's Vision (2026-03-09)

## Part 1: Synthetic Brain Architecture
- 40-50 tiny agents (0.8b primary, 2b/4b for specialized tasks)
- Each agent = cluster of neurons with ONE specific function
- Brain-region mapping:
  - **Visual Cortex**: vision-only agents (image/frame analysis)
  - **Auditory Cortex**: audio processing agents
  - **Prefrontal Cortex**: reasoning, planning, decision-making
  - **Hippocampus**: short-term memory formation, context tracking
  - **Long-term Memory**: persistent knowledge retrieval (RAG-backed)
  - **Broca's Area**: language production, response generation
  - **Wernicke's Area**: language comprehension, input parsing
  - **Amygdala**: emotional weighting, urgency/priority assessment
  - **Motor Cortex**: action execution (tool use, file operations)
  - **Cerebellum**: coordination, timing, multi-agent synchronization
- Key properties:
  - Always-on, never dormant — continuous processing
  - Bidirectional communication (not request/response)
  - Constant stream of consciousness — can receive input while still thinking
  - Emergent behavior through interaction, not programming
  - Persistent state — agents remember across "cycles"
  - Mixture of experts but with persistent inter-agent connections
- Goal: performance AND emergent awareness/persistence

## Part 2: Agent Simulation Lab
- Free-form interaction space (like The Sims for AI agents)
- Agents communicate, collaborate, form patterns autonomously
- Both modes share the same infrastructure/UI
- Research tool for studying emergent multi-agent behavior

## Lab Requirements (both modes)
- **Save points**: named configurations, click to restore
- **Per-agent tuning**: model, temperature, system prompt, connections, role
- **Real-time visibility**: see what every agent is thinking/saying/doing
- **Inter-agent logs**: who's talking to whom, full conversation history
- **RAG integration**: everything learned flows into unified knowledge store
- **Detailed UI**: 
  - Live agent nodes showing real-time state
  - Message flow visualization between agents
  - Per-agent log panels
  - Configuration panel with save/load
  - Brain-region visualization (for neural mode)

## Technical Approach
- Orchestrator process manages all agent instances
- Each agent = Ollama instance with unique system prompt + state
- Message bus for inter-agent communication (not direct calls)
- State snapshots for save/restore (JSON serialization)
- WebSocket streaming to UI for real-time visibility
- All messages logged + ingested into RAG
