# Neural Lab — Research Foundation

## The Science Behind Our Approach

### What the research says (2024-2025)
There's an active field at the intersection of computational neuroscience and AI doing exactly what we're building toward. Key references:

**"A multiscale brain emulation-based AI framework" (Nature Scientific Reports, May 2025)**
- Models the brain at THREE scales simultaneously:
  - **Microscale**: Individual neurons, synapses, ion channels, neurotransmitter actions
  - **Mesoscale**: Neural circuits, cortical columns, population dynamics
  - **Macroscale**: Whole-brain network interactions, consciousness
- Uses Hodgkin-Huxley neuron models, spike-timing dependent plasticity (STDP)
- Key insight: current DNNs fail because they lack biological plausibility

**Established frameworks we should study:**
- **Spaun** — Largest functional brain model (2.5M spiking neurons)
- **BrainCog** — Brain-inspired cognitive intelligence engine
- **Nengo** — Neural engineering framework for building brain models
- **NEST** — Large-scale network simulator
- **HTM (Hierarchical Temporal Memory)** — Cortical column simulation
- **Thousand Brains Theory** (Jeff Hawkins) — Each cortical column is a complete model

**"Brain-Inspired AI Agent Architecture" (EmergentMind, 2025)**
- Hebbian learning: "cells that fire together wire together"
- Synaptic pruning guided by utility (sparsity + continual optimization)
- Reward-modulated learning mimicking neurotransmitter activity
- Intrinsic motivation / curiosity-driven exploration

**"AI Brain Model Shows How Neurons Learn" (Neuroscience News, Dec 2025)**
- Biology-first design: real neuronal connectivity rules
- Neurotransmitter dynamics embedded in the model
- Multi-region architecture replicating biological computation

### Brain Systems to Replicate

#### Level 1: Neurotransmitter Systems (Global Modulators)
These are like "mood settings" that affect ALL agents simultaneously:

| System | Chemical | Effect | Our Implementation |
|--------|----------|--------|--------------------|
| Dopaminergic | Dopamine | Reward, motivation, learning rate | Global reward signal that strengthens successful connections |
| Serotonergic | Serotonin | Mood, patience, exploration vs exploitation | Temperature modifier for all agents |
| Noradrenergic | Norepinephrine | Alertness, attention, arousal | Think-interval modifier (faster when alert) |
| GABAergic | GABA | Inhibition, calming, filtering | Suppresses low-priority agent outputs |
| Glutamatergic | Glutamate | Excitation, signal amplification | Boosts high-priority agent outputs |
| Cholinergic | Acetylcholine | Memory formation, attention focus | Controls which agents write to long-term memory |

#### Level 2: Synaptic Dynamics
- **Hebbian Plasticity**: Agents that frequently communicate successfully → stronger connection weight
- **STDP**: Timing matters — if Agent A fires just before Agent B, strengthen A→B connection
- **Synaptic Pruning**: Unused connections weaken and eventually disconnect
- **Long-term Potentiation (LTP)**: Repeated activation = permanent strengthening
- **Long-term Depression (LTD)**: Lack of activation = permanent weakening

#### Level 3: Brain Regions (Our Agent Clusters)

| Brain Region | Function | Agent Implementation |
|-------------|----------|---------------------|
| **Visual Cortex (V1-V5)** | Raw vision → object recognition | Chain of agents: edge detection → shape → object → scene |
| **Auditory Cortex (A1)** | Sound processing → speech recognition | Frequency analysis → phoneme → word → meaning |
| **Prefrontal Cortex (PFC)** | Executive function, planning, reasoning | Decision-making agents with access to all other regions |
| **Hippocampus** | Memory consolidation, spatial navigation | Short-term buffer, decides what goes to long-term storage |
| **Amygdala** | Emotional tagging, threat detection | Priority/urgency scoring for all incoming signals |
| **Thalamus** | Sensory relay, attention gating | Routes signals between regions, filters noise |
| **Basal Ganglia** | Action selection, habit formation | Chooses which response to execute, learns from rewards |
| **Cerebellum** | Timing, coordination, motor learning | Synchronizes multi-agent responses |
| **Broca's Area** | Speech production | Converts decisions into language output |
| **Wernicke's Area** | Speech comprehension | Parses input into structured meaning |
| **Default Mode Network** | Mind-wandering, creativity, self-reflection | Active when no task is present — generates novel associations |
| **Reticular Formation** | Sleep/wake cycles, arousal | Controls system-wide active/idle cycles |

#### Level 4: Processes to Simulate

**Attention (Thalamic Gating)**:
- Not all agents receive all messages — the thalamus agent decides what gets through
- "Spotlight attention" — only 2-3 regions active at once, others suppressed

**Memory Consolidation (Sleep Cycles)**:
- Periodic "sleep" phases where active processing pauses
- During sleep: replay recent experiences, strengthen important memories, prune weak ones
- Like our Knowledge Scout but integrated into the brain's own cycle

**Emotional Modulation**:
- The amygdala doesn't just tag emotions — it CHANGES how other regions process
- High threat → all regions process faster, more connections active (fight/flight)
- Calm state → slower, more deliberate processing, Default Mode Network active

**Predictive Processing (Free Energy Principle)**:
- Each region maintains predictions about what it expects
- Only DIFFERENCES from prediction (prediction errors) are passed forward
- This massively reduces communication overhead

### Our Advantage
We're not trying to simulate billions of biological neurons. We're using LLMs AS the neurons — each one already has massive pattern recognition capability. So our "neurons" are insanely powerful compared to biological ones. The question is: can we organize them using biological principles to get emergent behavior that neither individual agents nor current monolithic models achieve?

### Implementation Phases
1. **Phase 1 (NOW)**: Basic multi-agent brain with region mapping, message bus, visualization
2. **Phase 2**: Add neurotransmitter systems (global modulators), synaptic plasticity (connection strength), thalamic gating
3. **Phase 3**: Add sleep/consolidation cycles, predictive processing, emotional modulation
4. **Phase 4**: Run systematic experiments, measure emergence, compare to single-model baselines
5. **Phase 5**: Design novel architecture based on findings — potentially a publishable paper
