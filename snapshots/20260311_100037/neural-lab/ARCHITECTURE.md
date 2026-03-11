# Neural Lab — Technical Architecture Document

**Version:** 0.9  
**Created:** 2026-03-09  
**Last Updated:** 2026-03-09  
**Author:** Main (AI) + Patrick Mello (Human)  
**Purpose:** Complete technical specification for reconstructing and understanding the Neural Lab system.

---

## 1. What This Is

A software simulation of a human brain where each "neuron" is a small language model (LLM). Unlike traditional neural networks where neurons are simple mathematical functions (multiply, add, activate), our neurons can **think in language** — they read messages, reason about them, and produce responses.

**Goal:** Build a persistent, thinking, learning system that models how the human brain actually works — not as a toy, but as a research platform for understanding intelligence.

**Core Hypothesis:** If we arrange language models in the same topology as the human brain, with the same communication patterns and learning rules, emergent intelligence may arise that's qualitatively different from a single large model.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────┐
│                 HUMAN (UI)                   │
│  Chat │ Brain Map │ Monitor │ Intercept │ Settings │
└────┬───────────┬──────────┬─────────────┘
     │           │          │
     ▼           ▼          ▼
┌─────────────────────────────────────────────┐
│           ORCHESTRATOR (Python/Flask)        │
│  Port 8103 | neural-lab.service             │
│                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Agent    │ │ Message  │ │ Plasticity│    │
│  │ Manager  │ │ Bus      │ │ Engine   │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ Snapshot │ │ Narrator │ │ Sleep/   │    │
│  │ Engine   │ │ Agent    │ │ Dream    │    │
│  └──────────┘ └──────────┘ └──────────┘    │
└────┬───────────┬──────────┬─────────────┘
     │           │          │
     ▼           ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Ollama   │ │ Memory   │ │ RAG      │
│ (models) │ │ (disk)   │ │ (vector) │
│ :11434   │ │ ~/.openclaw│ │ :8102   │
└──────────┘ └──────────┘ └──────────┘
```

---

## 3. Brain Regions (Biological Mapping)

Each region is modeled after its real biological function:

### 3.1 Visual Cortex (Occipital Lobe)
- **Agents:** 3 (visual_cortex-0, -1, -2)
- **Biological role:** Processes visual information — edges, shapes, objects, scenes
- **Our implementation:** Processes visual/spatial descriptions in text. When vision is enabled, can analyze images via multimodal models.
- **Model:** qwen3.5:0.8b
- **Connections:** → Prefrontal (for decision-making), → Hippocampus (for memory storage)

### 3.2 Auditory Cortex (Temporal Lobe)
- **Agents:** 2 (auditory_cortex-0, -1)
- **Biological role:** Processes sound — speech recognition, music, environmental sounds
- **Our implementation:** Processes language input, tone analysis, pattern recognition in sequences
- **Model:** qwen3.5:0.8b
- **Connections:** → Wernicke's (for language comprehension), → Hippocampus (for memory)

### 3.3 Wernicke's Area (Temporal Lobe)
- **Agents:** 2 (wernicke-0, -1)
- **Biological role:** Language comprehension — understanding meaning of words and sentences
- **Our implementation:** First receiver of human input. Parses meaning, extracts intent, routes to appropriate regions.
- **Model:** qwen3.5:0.8b
- **Connections:** → Prefrontal (for reasoning), → Hippocampus (for context), → Broca's (for response)

### 3.4 Prefrontal Cortex (Frontal Lobe)
- **Agents:** 3 (prefrontal-0, -1, -2)
- **Biological role:** Executive function — planning, decision-making, working memory, personality
- **Our implementation:** Central reasoning hub. Receives processed input from all sensory areas, makes decisions, directs behavior.
- **Model:** qwen3.5:2b (larger for reasoning tasks)
- **Connections:** → Broca's (for speech output), → Hippocampus (for memory queries), → Cerebellum (for action coordination), → Amygdala (for emotional context)

### 3.5 Broca's Area (Frontal Lobe)
- **Agents:** 2 (broca-0, -1)
- **Biological role:** Speech production — converting thoughts into language
- **Our implementation:** Produces the final response to human queries. Takes reasoning from Prefrontal and formulates coherent output.
- **Model:** qwen3.5:2b (larger for quality output)
- **Connections:** → Prefrontal (feedback loop), → Hippocampus (for factual recall)

### 3.6 Hippocampus (Limbic System)
- **Agents:** 2 (hippocampus-0, -1)
- **Biological role:** Memory formation and retrieval — converts short-term to long-term memory
- **Our implementation:** Manages memory consolidation. During sleep, reviews experiences and decides what to store long-term (RAG). During waking, provides context from memory.
- **Model:** qwen3.5:0.8b
- **Connections:** → Prefrontal (provide context), → Wernicke's (provide language context)

### 3.7 Amygdala (Limbic System)
- **Agents:** 2 (amygdala-0, -1)
- **Biological role:** Emotional processing — fear, reward, motivation, emotional memory
- **Our implementation:** Tags inputs with emotional valence. Flags urgency. Modulates response tone.
- **Model:** qwen3.5:0.8b
- **Connections:** → Prefrontal (emotional input to decisions), → Hippocampus (emotional memory tagging)

### 3.8 Cerebellum
- **Agents:** 1 (cerebellum-0)
- **Biological role:** Motor coordination, procedural memory, timing
- **Our implementation:** Coordinates multi-step actions, manages procedural workflows, timing of responses.
- **Model:** qwen3.5:0.8b
- **Connections:** → Prefrontal (receive action plans)

---

## 4. Message System

### 4.1 Message Format
```python
@dataclass
class Message:
    id: str           # Unique hex ID (8 chars)
    from_agent: str   # Sender agent ID (e.g. "prefrontal-0")
    to_agent: str     # Receiver ID, "broadcast", or region name
    content: str      # The actual message text (LLM-generated)
    timestamp: float  # Unix timestamp
    msg_type: str     # thought | response | observation | directive | knowledge | dream
    seq: int          # Global sequence number (monotonically increasing)
```

### 4.2 Sequence Ordering (Preventing Stale Reads)
**Problem:** If Agent A and Agent B both send messages at similar times, Agent C might process them out of order, or re-process old messages.

**Solution:** Global monotonic sequence counter.

```
Invariant: For all messages m1, m2:
  if m1 was created before m2, then m1.seq < m2.seq

Per-agent watermark:
  agent_last_seq[agent_id] = highest seq this agent has processed
  
On read:
  new_messages = [m for m in bus if m.seq > agent_last_seq[agent_id] 
                  and m is addressed to agent_id]
  agent_last_seq[agent_id] = max(new_messages.seq)
```

This guarantees:
- No message is processed twice
- No stale messages are read
- Order is preserved regardless of agent think speed

### 4.3 Message Routing
```
Direct:    msg.to_agent = "prefrontal-0"    → only that agent receives it
Broadcast: msg.to_agent = "broadcast"        → all agents receive it
Region:    msg.to_agent = "frontal"          → all agents in that region
Connected: agents receive from their connections list
```

### 4.4 Central Message Router
ALL messages go through `_post_message()`:
1. Acquire lock
2. Increment global seq counter
3. Assign seq to message
4. Append to message bus (deque, maxlen=5000)
5. Append to intercept buffer (for human inspection)
6. Release lock
7. Emit via WebSocket (for UI visualization)
8. Write to log file (for persistence)

---

## 5. Agent Think Loop

Each agent runs a continuous think loop in its own thread:

```
while running:
    if not enabled:
        sleep(1)
        continue
    
    # 1. Gather new messages (seq-based, no stale reads)
    new_messages = get_new_messages_for(agent_id, connections)
    
    # 2. Build context
    context = []
    if directive:  context.add("[ACTIVE DIRECTIVE]: {directive}")
    if messages:   context.add("Recent messages: {messages}")
    if memory:     context.add("Your memory: {last 5 memories}")
    
    # 3. Generate thought (Ollama API call)
    response = ollama.generate(
        model=agent.model,
        system=agent.system_prompt,
        prompt=context,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        think=False  # Don't waste tokens on CoT
    )
    
    # 4. Update state
    agent.current_thought = response
    agent.think_count += 1
    agent.memory.append(response[:200])  # Short-term memory (last 20)
    
    # 5. Send to connected agents (if speak enabled)
    for target in connections:
        post_message(Message(from=agent_id, to=target, content=response))
    
    # 6. Wait for next think cycle
    sleep(think_interval)  # Default 3s
```

**Key properties:**
- Each agent is a separate thread
- Think interval controls rate (default 3s between thoughts)
- Short-term memory: last 20 thoughts (in-memory list)
- Long-term memory: RAG store (via Memory Concierge, port 8102)
- All thoughts are real LLM generations, not scripted

---

## 6. Neuroplasticity

### 6.1 Hebbian Learning
"Neurons that fire together wire together."

```
When agent A sends a message to agent B:
    strength[A→B] += 0.05  (strengthen)
    strength[A→B] = min(1.0, strength[A→B])

When a connection exists but is unused in recent window:
    strength[A→B] -= 0.01  (weaken)
    strength[A→B] = max(0.0, strength[A→B])
```

### 6.2 Synaptic Pruning
```
if strength[A→B] < 0.1:
    remove connection A→B entirely
    (agent A no longer sends to agent B)
```

### 6.3 Neurogenesis (New Connection Growth)
```
Every 30 seconds (plasticity tick):
    if random() < 0.10:  # 10% chance
        pick random agent A
        pick candidate B (not already connected to A)
        if A.region == B.region:
            grow_chance = 0.30  # Same region: 30% chance
        else:
            grow_chance = 0.05  # Cross-region: 5% chance
        
        if random() < grow_chance:
            add connection A→B
            strength[A→B] = 0.3  # Start weak
```

### 6.4 Training vs Testing Mode
- **Training mode (plasticity ON):** Connections evolve. Strengths change. New connections form. Old ones prune.
- **Testing mode (plasticity OFF):** Connections frozen. No changes. Pure evaluation.

---

## 7. Sleep/Dream Cycle

Modeled after human sleep stages:

### Phase 1: Memory Consolidation (Hippocampus)
```
Input: All agent memories from the session
Process: Hippocampus agents review all experiences
Output: Pattern identification, important connection discovery
```

### Phase 2: Rationalization (Prefrontal Cortex)
```
Input: Consolidation output from Hippocampus
Process: Prefrontal decides what to retain vs forget
Output: Long-term learnings, pruned noise
```

### Phase 3: Storage
```
Dream output → RAG store (source_type: "neural-lab-dream")
Dream output → broadcast to all agents
Think intervals → slowed to 10s (dream speed)
```

### Wake
```
Restore normal think intervals
Resume active processing
Dream memories now available to all agents
```

---

## 8. Human Interface

### 8.1 Ask Pipeline
```
Human input → Wernicke's Area (comprehension)
    → Prefrontal Cortex (reasoning)  
    → Broca's Area (speech production)
    → Human output

Timeout: 30s (configurable)
Broca responds via response_queue (thread-safe)
```

### 8.2 Narrator Agent
Not part of the brain — an external observer.
```
Input: All recent messages + all agent states + region activity
Model: User-selectable (0.8b, 2b, 4b)
Output: Natural language explanation of brain activity
```

### 8.3 Intercept System
Every message passes through the intercept buffer:
```
intercepted = deque(maxlen=200)
Each message: {seq, from, to, content, type, timestamp}
Human can: view all, filter by agent/region, inject messages
```

---

## 9. Persistence

### 9.1 Short-term Memory
- In-memory list per agent (last 20 thoughts)
- Lost on restart unless saved via graceful shutdown

### 9.2 Session Memory
- Graceful shutdown → saves all agent memories to JSON: `~/.openclaw/neural-lab/memories-{session_id}.json`
- Contains: name, role, memory list, last output, think count, message count

### 9.3 Long-term Memory (RAG)
- Memory Concierge (port 8102): vector database with nomic-embed-text embeddings
- Ingest on: session stop, sleep/dream, manual
- Source types: `neural-lab-session`, `neural-lab-dream`
- Queryable by any agent via `/query` endpoint

### 9.4 Snapshots
- Full brain state saved to JSON: `~/.openclaw/neural-lab/snapshots/`
- Contains: all agent configs, connection strengths, messages, plasticity log
- Auto-checkpoint: every 5 minutes (configurable)
- Manual checkpoint: anytime via API
- Project-tagged for experiment tracking

---

## 10. Connection Strengths & Visualization

```
Visual representation:
    line_width = 0.3 + strength * 1.5    (range: 0.3 to 1.8 pixels)
    opacity = max(0.15, strength)          (range: 15% to 100%)
    
Strength range: 0.0 (about to prune) to 1.0 (maximum)
Initial strength: 0.5 for preset connections, 0.3 for grown connections
```

Message dots on brain map:
- Each dot = one real message with a seq number
- Travel time: 1200ms from sender node to receiver node
- White core + colored glow (color = sender's region)
- Trail line behind the dot

---

## 11. Resource Management

### 11.1 RAM Estimation
```
Ollama shares model weights across concurrent requests.
First instance of a model: full size (0.8b=0.9GB, 2b=2.2GB, 4b=4.5GB)
Additional concurrent instances: ~0.01GB each (shared weights)

Current brain config:
    0.8b (12 agents) = 0.9GB + 11 * 0.01GB = 1.01GB
    2b (5 agents)    = 2.2GB + 4 * 0.01GB  = 2.24GB
    Total estimated: ~3.25GB
    Available (DGX Spark): ~96GB free (without 122B loaded)
    
Max theoretical agents (0.8b, shared weights): ~7000
Max practical agents (with model switching overhead): ~100-200
```

### 11.2 API Call Rate
```
17 agents × 1 think per 3 seconds = ~5.7 Ollama calls/second
Each call: ~0.5-2s for 0.8b, ~1-4s for 2b
Ollama handles concurrent requests via queue
```

---

## 12. API Reference

All endpoints on port 8103.

### Core
| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Service health check |
| GET | /api/state | Full lab state (agents, messages, config) |
| POST | /api/start | Start brain/simulation `{mode, name, config}` |
| POST | /api/stop | Graceful shutdown (saves state) |
| POST | /api/estop | Emergency stop (kill + unload models) |

### Brain Interaction
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/ask | Ask the brain a question `{question, timeout}` |
| POST | /api/inject | Send message to specific agent `{text, target}` |
| POST | /api/inject/random | Send to random agent `{text}` |
| GET | /api/intercept | Get intercepted message stream `?limit=50` |

### Agent Management
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/agent/:id | Get agent details |
| PATCH | /api/agent/:id | Update agent config |
| POST | /api/directive | Broadcast directive `{directive, group, tags}` |
| POST | /api/toggle | Toggle capability `{capability, agents, value}` |
| GET | /api/groups | List agent groups by region |

### Brain Functions
| Method | Path | Description |
|--------|------|-------------|
| POST | /api/sleep | Enter sleep/dream mode |
| POST | /api/wake | Wake from sleep |
| GET | /api/dreams | Get dream consolidation log |
| GET | /api/narrate | Get narrator summary `?model=qwen3.5:0.8b` |
| POST | /api/narrator/chat | Chat with narrator `{question, model}` |

### Plasticity & Checkpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/plasticity | Get plasticity state & log |
| POST | /api/plasticity | Toggle training mode `{enabled}` |
| GET | /api/graph | Connection graph with strengths |
| POST | /api/checkpoint | Save manual checkpoint `{name}` |
| POST | /api/checkpoint/interval | Set auto-checkpoint interval `{interval}` |
| POST | /api/project | Set project name `{name}` |

### Snapshots
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/snapshots | List saved snapshots |
| POST | /api/snapshots | Save snapshot `{name}` |
| POST | /api/snapshots/load | Load snapshot `{id}` |

### Monitoring
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/monitoring | Detailed monitoring data (rates, regions, stats) |

---

## 13. File Map

```
tools/neural-lab/
├── orchestrator.py          # Main backend (Flask + SocketIO, ~1600 lines)
├── ARCHITECTURE.md          # This document
└── RESEARCH.md              # Neuroscience research foundation

hub/31-neural-lab/
└── index.html               # Full UI (tabs, canvas, widgets, ~1400 lines)

~/.openclaw/neural-lab/
├── snapshots/               # Saved brain states (JSON)
├── logs/                    # Session logs (JSONL)
└── memories-*.json          # Saved agent memories

Systemd: neural-lab.service (port 8103)
```

---

## 14. How to Recreate From Scratch

1. Install dependencies: `pip install flask flask-cors flask-socketio requests`
2. Create `orchestrator.py` with:
   - Data models: AgentConfig, AgentState, Message
   - Brain presets (BRAIN_PRESETS dict): 8 regions, 17 agents
   - NeuralLab class with: create_brain(), start(), stop(), emergency_stop()
   - Agent think loop: gather messages → build context → generate via Ollama → post to connections
   - Message bus: deque with global seq counter, per-agent watermarks
   - Plasticity engine: Hebbian strengthen, pruning, neurogenesis
   - Sleep/dream: Hippocampus consolidation → Prefrontal rationalization → RAG ingest
   - API endpoints (see Section 12)
3. Create `index.html` with:
   - Canvas-based brain map with region clustering
   - WebSocket connection for real-time updates
   - Tabs: Agents, Brain Map, Chat, Monitor, Intercept
   - Floating narrator chat widget
4. Create systemd service on port 8103
5. Ensure Ollama running on port 11434 with qwen3.5:0.8b and qwen3.5:2b
6. Ensure Memory Concierge on port 8102 for RAG

---

## 15. Future: Training While Running

**Goal:** Models that learn and update their weights while the brain is running — like real neurons that change through experience.

**Approach (planned):**
1. Collect input→output pairs from each agent's think loop
2. Use these as training data for supervised fine-tuning
3. Fine-tune the agent's model on its own experience
4. Hot-swap the model (Ollama supports this)
5. Repeat → the agent literally gets better at its specific role

**Requirements:**
- safetensors format (not quantized GGUF) for fine-tuning
- Training pipeline (LoRA/QLoRA for efficiency)
- Evaluation framework to measure improvement
- Rollback capability if training degrades performance

---

## 16. Equations & Formulas

### Hebbian Learning Rule
```
Δw(i→j) = η · a(i) · a(j)

where:
  w(i→j) = connection strength from agent i to agent j
  η = learning rate (0.05 for strengthening, 0.01-0.02 for weakening)
  a(i) = activity of agent i (1 if recently sent message, 0 otherwise)
  a(j) = activity of agent j (1 if recently received message, 0 otherwise)

Update rule:
  w(i→j) = clip(w(i→j) + Δw, 0.0, 1.0)
  if w(i→j) < 0.1: prune connection
```

### Think Rate
```
R(agent) = think_count / uptime_seconds × 60   (thinks per minute)
```

### Connection Visualization
```
line_opacity = max(0.15, w(i→j))
line_width = 0.3 + w(i→j) × 1.5
```

### Resource Estimation  
```
RAM_total = Σ(unique_models) model_size + Σ(concurrent_instances - 1) × 0.01 GB
max_agents = available_RAM / 0.01   (shared weights)
```

### Neurogenesis Probability
```
P(grow | same_region) = 0.10 × 0.30 = 0.03 per tick
P(grow | diff_region) = 0.10 × 0.05 = 0.005 per tick
tick_interval = 30 seconds
```

---

*This document is a living specification. Update it every time a significant change is made to the system.*
