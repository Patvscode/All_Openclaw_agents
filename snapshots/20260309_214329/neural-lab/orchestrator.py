#!/usr/bin/env python3
"""
Neural Lab Orchestrator — Manages a swarm of persistent micro-agents.

Two modes:
  1. BRAIN: Biologically-inspired neural architecture (specialized regions)
  2. SIMULATION: Free-form agent interaction sandbox

Each agent:
  - Has a role, system prompt, model, and persistent state
  - Communicates via a shared message bus
  - Runs continuous think cycles (not request/response)
  - Logs everything for observability

Port: 8103
"""

import json
import time
import uuid
import threading
import logging
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from collections import deque
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from simulation import SimulationEngine, ENVIRONMENTS, ACTIONS
from rl_env import NeuralLabEnv
from model_workshop import inspect_model, scan_models, generate_architecture_explanation, duplicate_model
from platform import platform, PluginType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("neural-lab")

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ─── Config ───
OLLAMA_URL = "http://localhost:11434"
DATA_DIR = Path.home() / ".openclaw/neural-lab"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
LOGS_DIR = DATA_DIR / "logs"
CONCIERGE_URL = "http://localhost:8102"

DATA_DIR.mkdir(parents=True, exist_ok=True)
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Data Models ───

@dataclass
class AgentConfig:
    id: str
    name: str
    role: str  # e.g. "visual_cortex", "hippocampus", "free_agent"
    region: str = ""  # Brain region (for brain mode)
    model: str = "qwen3.5:0.8b"
    system_prompt: str = ""
    temperature: float = 0.7
    max_tokens: int = 200
    connections: List[str] = field(default_factory=list)  # IDs of agents this one talks to
    color: str = "#888"
    think_interval: float = 3.0  # seconds between think cycles
    enabled: bool = True
    # Capability toggles
    vision: bool = False  # Can process images
    listen: bool = True   # Receives messages from others
    speak: bool = True    # Sends messages to others
    remember: bool = True # Maintains short-term memory
    persistent: bool = True  # Keeps running (vs run-once)
    # Interaction mode: "community" (free talk) or "pipeline" (strict in→out)
    interaction_mode: str = "community"
    # Active directive/goal — injected by human, auto-read each think cycle
    directive: str = ""
    # Tags for group targeting
    tags: List[str] = field(default_factory=list)

@dataclass 
class AgentState:
    config: AgentConfig
    status: str = "idle"  # idle, thinking, speaking, listening
    current_thought: str = ""
    last_output: str = ""
    message_count: int = 0
    think_count: int = 0
    started_at: float = 0
    last_active: float = 0
    memory: List[str] = field(default_factory=list)  # Short-term memory (last N messages)
    
    def to_dict(self):
        d = asdict(self.config)
        d.update({
            'status': self.status,
            'current_thought': self.current_thought,
            'last_output': self.last_output,
            'message_count': self.message_count,
            'think_count': self.think_count,
            'started_at': self.started_at,
            'last_active': self.last_active,
        })
        return d

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str  # or "broadcast" or region name
    content: str
    timestamp: float
    msg_type: str = "thought"  # thought, response, observation, broadcast
    seq: int = 0  # Global sequence number — monotonically increasing, prevents stale reads
    
    def to_dict(self):
        return asdict(self)

# ─── Brain Region Presets ───

BRAIN_PRESETS = {
    "visual_cortex": {
        "name": "Visual Cortex",
        "region": "occipital",
        "system_prompt": "You are the visual processing center. You ONLY describe what you see in images or visual data passed to you. Be precise and factual about visual content. Report shapes, colors, text, objects, movement. Output short observations, not conversations.",
        "color": "#ff6b6b",
        "count": 3,
    },
    "auditory_cortex": {
        "name": "Auditory Cortex",
        "region": "temporal",
        "system_prompt": "You are the auditory processing center. You analyze sounds, speech, and audio descriptions. Extract meaning from what is heard. Report words, tone, urgency, speaker identity. Output short observations.",
        "color": "#4ecdc4",
        "count": 2,
    },
    "prefrontal": {
        "name": "Prefrontal Cortex",
        "region": "frontal",
        "system_prompt": "You are the reasoning and planning center. You receive observations from other regions and make decisions. You plan actions, evaluate options, and direct attention. Think step by step. Be decisive.",
        "color": "#a78bfa",
        "count": 3,
        "model": "qwen3.5:2b",
    },
    "hippocampus": {
        "name": "Hippocampus",
        "region": "temporal",
        "system_prompt": "You are the memory formation center. You receive all observations and decide what's important enough to remember. You maintain context about recent events. You can recall past observations when asked. Keep a running summary of what's happening.",
        "color": "#ffd93d",
        "count": 2,
    },
    "broca": {
        "name": "Broca's Area",
        "region": "frontal",
        "system_prompt": "You are the speech production center. You take decisions from the prefrontal cortex and observations from other areas and produce coherent spoken responses. You are the voice of the system. Speak naturally and clearly.",
        "color": "#22c55e",
        "count": 2,
        "model": "qwen3.5:2b",
    },
    "wernicke": {
        "name": "Wernicke's Area",
        "region": "temporal",
        "system_prompt": "You are the language comprehension center. You parse incoming text and speech, extract meaning, intent, and context. You pass your understanding to the prefrontal cortex and hippocampus. Output structured interpretations.",
        "color": "#3b82f6",
        "count": 2,
    },
    "amygdala": {
        "name": "Amygdala",
        "region": "limbic",
        "system_prompt": "You are the emotional processing center. You assess the emotional valence and urgency of all incoming information. Tag messages with emotional weight: fear, excitement, curiosity, boredom, urgency. You influence attention priority.",
        "color": "#f97316",
        "count": 2,
    },
    "cerebellum": {
        "name": "Cerebellum",
        "region": "hindbrain",
        "system_prompt": "You are the coordination center. You monitor all agent activity and ensure smooth operation. You detect conflicts, redundancy, and timing issues. You can throttle or boost agent activity. Report coordination status.",
        "color": "#76b900",
        "count": 1,
    },
}

# ─── Lab State ───

class NeuralLab:
    def __init__(self):
        self.agents: Dict[str, AgentState] = {}
        self.messages: deque = deque(maxlen=5000)
        self.mode: str = "stopped"  # stopped, brain, simulation, sleeping, shutdown
        self.running: bool = False
        self.lock = threading.Lock()
        self.tick_count: int = 0
        self.session_id: str = ""
        self.session_name: str = ""
        self.log_file = None
        self.msg_seq: int = 0  # Global message sequence counter
        self.agent_last_seq: Dict[str, int] = {}  # Per-agent: last seq they processed
        self.sleep_log: List[dict] = []  # Dream/consolidation log
        self.intercepted: deque = deque(maxlen=200)  # Messages captured for human inspection
        # Neuroplasticity
        self.plasticity_enabled: bool = False  # Training mode (on) vs testing mode (off)
        self.connection_strengths: Dict[str, float] = {}  # "from->to" : strength (0.0-1.0)
        self.plasticity_log: List[dict] = []  # Record of all connection changes
        # Auto-checkpoint
        self.auto_checkpoint_interval: int = 300  # seconds (5 min default)
        self.last_checkpoint: float = 0
        self.checkpoint_timer = None
        # Project tracking
        self.project_name: str = ""
        
    def create_brain(self, config: dict = None):
        """Create a brain-mode agent swarm from presets."""
        with self.lock:
            self.agents.clear()
            self.messages.clear()
            
        for role, preset in BRAIN_PRESETS.items():
            count = preset.get("count", 1)
            for i in range(count):
                agent_id = f"{role}-{i}" if count > 1 else role
                agent_name = f"{preset['name']} #{i+1}" if count > 1 else preset['name']
                
                cfg = AgentConfig(
                    id=agent_id,
                    name=agent_name,
                    role=role,
                    region=preset.get("region", ""),
                    model=preset.get("model", "qwen3.5:0.8b"),
                    system_prompt=preset["system_prompt"],
                    color=preset["color"],
                    temperature=0.5,
                    max_tokens=150,
                    think_interval=3.0 + (i * 0.5),  # Stagger think cycles
                )
                
                # Default connections: each region connects to prefrontal + hippocampus
                if role not in ("prefrontal", "hippocampus"):
                    cfg.connections = ["prefrontal-0", "hippocampus-0"]
                elif role == "prefrontal":
                    cfg.connections = ["broca-0", "hippocampus-0", "cerebellum"]
                elif role == "hippocampus":
                    cfg.connections = ["prefrontal-0", "wernicke-0"]
                    
                with self.lock:
                    self.agents[agent_id] = AgentState(config=cfg)
        
        logger.info(f"Brain created with {len(self.agents)} agents")
        return len(self.agents)
    
    def create_simulation(self, agent_configs: list):
        """Create a simulation-mode swarm from custom configs."""
        with self.lock:
            self.agents.clear()
            self.messages.clear()
            
        for cfg_dict in agent_configs:
            cfg = AgentConfig(**cfg_dict)
            with self.lock:
                self.agents[cfg.id] = AgentState(config=cfg)
                
        logger.info(f"Simulation created with {len(self.agents)} agents")
        return len(self.agents)
    
    def add_agent(self, config: dict) -> dict:
        """Add a new agent to the running brain."""
        role = config.get('role', 'free_agent')
        region = config.get('region', '')
        name = config.get('name', f'Agent-{len(self.agents)}')
        model = config.get('model', 'qwen3.5:0.8b')
        
        # Generate unique ID
        agent_id = f"{role}-{len([a for a in self.agents if role in a])}"
        if agent_id in self.agents:
            agent_id = f"{role}-{uuid.uuid4().hex[:4]}"
        
        preset = BRAIN_PRESETS.get(role, {})
        
        cfg = AgentConfig(
            id=agent_id, name=name, role=role, region=region or preset.get('region', ''),
            model=model, system_prompt=config.get('system_prompt', preset.get('system_prompt', f'You are {name}.')),
            temperature=config.get('temperature', 0.7), max_tokens=config.get('max_tokens', 200),
            connections=config.get('connections', []),
            color=preset.get('color', '#888'), think_interval=config.get('think_interval', 3.0),
        )
        
        state = AgentState(config=cfg)
        with self.lock:
            self.agents[agent_id] = state
        
        # Start think loop if brain is running
        if self.running:
            state.started_at = time.time()
            state.status = "idle"
            t = threading.Thread(target=self._agent_loop, args=(agent_id,), daemon=True)
            t.start()
        
        logger.info(f"Added agent: {agent_id} ({name}, {role}, {model})")
        return {"ok": True, "id": agent_id, "name": name}
    
    def remove_agent(self, agent_id: str) -> dict:
        """Remove an agent from the brain."""
        if agent_id not in self.agents:
            return {"ok": False, "error": "not found"}
        
        state = self.agents[agent_id]
        state.config.enabled = False  # Stop think loop
        
        # Remove from other agents' connections
        for other in self.agents.values():
            if agent_id in other.config.connections:
                other.config.connections.remove(agent_id)
        
        with self.lock:
            del self.agents[agent_id]
        
        logger.info(f"Removed agent: {agent_id}")
        return {"ok": True, "removed": agent_id}
    
    def start(self, mode: str, name: str = ""):
        """Start the lab."""
        if self.running:
            return False
            
        self.running = True
        self.mode = mode
        self.session_id = f"session-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        self.session_name = name or f"{mode}-{datetime.now().strftime('%H%M')}"
        self.tick_count = 0
        
        # Open log file
        log_path = LOGS_DIR / f"{self.session_id}.jsonl"
        self.log_file = open(log_path, 'a')
        
        # Initialize connection strengths
        for agent_id, state in self.agents.items():
            for target in state.config.connections:
                key = f"{agent_id}->{target}"
                if key not in self.connection_strengths:
                    self.connection_strengths[key] = 0.5
        
        # Start all agent think loops
        for agent_id, state in self.agents.items():
            if state.config.enabled:
                state.started_at = time.time()
                state.status = "idle"
                t = threading.Thread(target=self._agent_loop, args=(agent_id,), daemon=True)
                t.start()
        
        # Start auto-checkpoint
        self._start_auto_checkpoint()
        
        # Start plasticity thread (runs every 30s)
        def _plasticity_loop():
            while self.running:
                time.sleep(30)
                if self.running:
                    self._plasticity_tick()
        threading.Thread(target=_plasticity_loop, daemon=True).start()
        
        logger.info(f"Lab started: {self.session_name} ({mode}) with {len(self.agents)} agents")
        return True
    
    def _post_message(self, msg: Message):
        """Central message posting — assigns seq, logs, intercepts, emits."""
        with self.lock:
            self.msg_seq += 1
            msg.seq = self.msg_seq
            self.messages.append(msg)
            self.intercepted.append(msg.to_dict())
        socketio.emit('message', msg.to_dict())
        self._log(msg)
    
    def _get_new_messages_for(self, agent_id: str, connections: List[str]) -> List[Message]:
        """Get messages newer than what this agent has seen. Prevents stale reads."""
        last_seq = self.agent_last_seq.get(agent_id, 0)
        new_msgs = []
        with self.lock:
            for msg in self.messages:
                if msg.seq <= last_seq:
                    continue
                # Message is for this agent (direct, broadcast, or from a connected agent)
                if (msg.to_agent == agent_id or 
                    msg.to_agent == "broadcast" or 
                    msg.from_agent in connections):
                    new_msgs.append(msg)
            # Update watermark
            if new_msgs:
                self.agent_last_seq[agent_id] = new_msgs[-1].seq
        return new_msgs[-10:]  # Last 10 new messages max
    
    def stop(self):
        """Stop the lab gracefully — saves state, lets agents wind down."""
        logger.info("Graceful shutdown initiated...")
        
        # Signal agents to stop accepting new work
        for state in self.agents.values():
            state.config.enabled = False
        
        # Give agents a moment to finish current thought (up to 5s)
        time.sleep(min(5, max(s.config.think_interval for s in self.agents.values()) if self.agents else 1))
        
        self.running = False
        self.mode = "stopped"
        
        # Save state before closing
        if self.agents:
            self._save_agent_memories()
        
        if self.log_file:
            self.log_file.close()
            self.log_file = None
        
        # Ingest session into RAG
        self._ingest_session()
        
        for state in self.agents.values():
            state.status = "idle"
        logger.info("Lab stopped gracefully — all state saved")
    
    def sleep(self):
        """Enter sleep/dream mode — consolidate learnings, rationalize info."""
        if self.mode != "brain":
            return False
        
        self.mode = "sleeping"
        logger.info("💤 Entering sleep mode — dream consolidation starting...")
        socketio.emit('mode_change', {'mode': 'sleeping'})
        
        # Collect all agent memories and recent messages
        all_memories = []
        for aid, state in self.agents.items():
            all_memories.append({
                'agent': state.config.name,
                'role': state.config.role,
                'region': state.config.region,
                'thoughts': list(state.memory)[-10:],
                'last_output': state.last_output,
                'think_count': state.think_count,
            })
        
        # Reduce think rates to dream speed (slow ticking)
        for state in self.agents.values():
            state.config.think_interval = max(state.config.think_interval, 10.0)
        
        # Run dream consolidation in a thread
        def _dream():
            dream_log = []
            
            # Phase 1: Have hippocampus consolidate memories
            hippo_agents = [s for s in self.agents.values() if 'hippocampus' in s.config.role]
            for hippo in hippo_agents:
                summary = f"DREAM CONSOLIDATION — Review today's experiences and identify patterns:\n"
                for mem in all_memories:
                    summary += f"\n[{mem['agent']}] ({mem['role']}): {'; '.join(mem['thoughts'][-3:])}"
                
                try:
                    result = self._generate(
                        hippo.config.model,
                        "You are the hippocampus in dream/sleep mode. Consolidate memories: find patterns, strengthen important connections, discard noise. Output a brief dream summary of key learnings.",
                        summary[:2000],
                        0.9, 300
                    )
                    dream_entry = {
                        'phase': 'consolidation',
                        'agent': hippo.config.id,
                        'content': result,
                        'timestamp': time.time(),
                    }
                    dream_log.append(dream_entry)
                    self.sleep_log.append(dream_entry)
                    
                    msg = Message(
                        id=uuid.uuid4().hex[:8],
                        from_agent=hippo.config.id,
                        to_agent="broadcast",
                        content=f"💤 DREAM: {result}",
                        timestamp=time.time(),
                        msg_type="dream",
                    )
                    self._post_message(msg)
                except Exception as e:
                    logger.error(f"Dream consolidation error: {e}")
            
            # Phase 2: Have prefrontal rationalize
            pf_agents = [s for s in self.agents.values() if 'prefrontal' in s.config.role]
            for pf in pf_agents[:1]:
                dream_content = "\n".join(d['content'] for d in dream_log)
                try:
                    result = self._generate(
                        pf.config.model,
                        "You are the prefrontal cortex in dream mode. Rationalize the dream consolidation output: what should be retained as long-term learnings? What connections between ideas are important? What can be forgotten?",
                        dream_content[:1500],
                        0.7, 300
                    )
                    dream_entry = {
                        'phase': 'rationalization',
                        'agent': pf.config.id,
                        'content': result,
                        'timestamp': time.time(),
                    }
                    dream_log.append(dream_entry)
                    self.sleep_log.append(dream_entry)
                    
                    msg = Message(
                        id=uuid.uuid4().hex[:8],
                        from_agent=pf.config.id,
                        to_agent="broadcast",
                        content=f"💤 RATIONALIZED: {result}",
                        timestamp=time.time(),
                        msg_type="dream",
                    )
                    self._post_message(msg)
                except Exception as e:
                    logger.error(f"Dream rationalization error: {e}")
            
            # Ingest dream results into RAG
            if dream_log:
                try:
                    dream_text = "\n\n".join(f"[{d['phase']}] {d['content']}" for d in dream_log)
                    requests.post(f"{CONCIERGE_URL}/ingest", json={
                        "text": dream_text[:3000],
                        "source": f"neural-lab-dream-{self.session_id}",
                        "source_type": "neural-lab-dream",
                        "agent": "neural-lab",
                    }, timeout=10)
                except:
                    pass
            
            socketio.emit('dream_complete', {'entries': len(dream_log)})
            logger.info(f"💤 Dream cycle complete — {len(dream_log)} consolidations")
        
        threading.Thread(target=_dream, daemon=True).start()
        return True
    
    def wake(self):
        """Wake from sleep — restore normal think rates."""
        if self.mode != "sleeping":
            return False
        
        self.mode = "brain"
        # Restore normal think intervals
        for role, preset in BRAIN_PRESETS.items():
            for state in self.agents.values():
                if state.config.role == role:
                    state.config.think_interval = preset.get("think_interval", 3.0)
        
        socketio.emit('mode_change', {'mode': 'brain'})
        logger.info("☀️ Brain waking up — normal operations resumed")
        return True
    
    def _save_agent_memories(self):
        """Save all agent memories to disk for recovery."""
        try:
            mem_path = DATA_DIR / f"memories-{self.session_id}.json"
            memories = {}
            for aid, state in self.agents.items():
                memories[aid] = {
                    'name': state.config.name,
                    'role': state.config.role,
                    'memory': list(state.memory),
                    'last_output': state.last_output,
                    'think_count': state.think_count,
                    'message_count': state.message_count,
                }
            with open(mem_path, 'w') as f:
                json.dump(memories, f, indent=2)
            logger.info(f"Saved agent memories to {mem_path}")
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    # ─── Neuroplasticity ───
    
    def _strengthen_connection(self, from_id: str, to_id: str, amount: float = 0.05):
        """Strengthen a connection (Hebbian: neurons that fire together wire together)."""
        if not self.plasticity_enabled:
            return
        key = f"{from_id}->{to_id}"
        current = self.connection_strengths.get(key, 0.5)
        new_val = min(1.0, current + amount)
        self.connection_strengths[key] = new_val
        self.plasticity_log.append({
            'type': 'strengthen', 'from': from_id, 'to': to_id,
            'old': round(current, 3), 'new': round(new_val, 3),
            'timestamp': time.time(),
        })
    
    def _weaken_connection(self, from_id: str, to_id: str, amount: float = 0.02):
        """Weaken an unused connection (synaptic pruning)."""
        if not self.plasticity_enabled:
            return
        key = f"{from_id}->{to_id}"
        current = self.connection_strengths.get(key, 0.5)
        new_val = max(0.0, current - amount)
        self.connection_strengths[key] = new_val
        
        # If connection drops below threshold, remove it
        if new_val < 0.1:
            self._remove_connection(from_id, to_id)
        
        self.plasticity_log.append({
            'type': 'weaken', 'from': from_id, 'to': to_id,
            'old': round(current, 3), 'new': round(new_val, 3),
            'timestamp': time.time(),
        })
    
    def _remove_connection(self, from_id: str, to_id: str):
        """Remove a connection (pruning)."""
        if from_id in self.agents:
            conns = self.agents[from_id].config.connections
            if to_id in conns:
                conns.remove(to_id)
                self.plasticity_log.append({
                    'type': 'prune', 'from': from_id, 'to': to_id,
                    'timestamp': time.time(),
                })
                socketio.emit('connection_pruned', {'from': from_id, 'to': to_id})
                logger.info(f"🧠 Pruned connection: {from_id} → {to_id}")
    
    def _grow_connection(self, from_id: str, to_id: str):
        """Grow a new connection (neurogenesis)."""
        if not self.plasticity_enabled:
            return False
        if from_id not in self.agents or to_id not in self.agents:
            return False
        conns = self.agents[from_id].config.connections
        if to_id in conns:
            return False  # Already connected
        conns.append(to_id)
        self.connection_strengths[f"{from_id}->{to_id}"] = 0.3  # Start weak
        self.plasticity_log.append({
            'type': 'grow', 'from': from_id, 'to': to_id,
            'timestamp': time.time(),
        })
        socketio.emit('connection_grown', {'from': from_id, 'to': to_id})
        logger.info(f"🌱 Grew new connection: {from_id} → {to_id}")
        return True
    
    def _plasticity_tick(self):
        """Run one plasticity update — call periodically from agent loops."""
        if not self.plasticity_enabled or not self.running:
            return
        
        # Track which connections were used recently
        recent_used = set()
        with self.lock:
            for msg in list(self.messages)[-100:]:
                if msg.from_agent in self.agents and msg.to_agent in self.agents:
                    recent_used.add(f"{msg.from_agent}->{msg.to_agent}")
        
        # Strengthen used connections, weaken unused
        for aid, state in self.agents.items():
            for target in list(state.config.connections):
                key = f"{aid}->{target}"
                if key in recent_used:
                    self._strengthen_connection(aid, target)
                else:
                    self._weaken_connection(aid, target, 0.01)
        
        # Chance to grow new connections between agents in the same region
        import random
        if random.random() < 0.1:  # 10% chance per tick
            agents_list = list(self.agents.values())
            if len(agents_list) >= 2:
                a1 = random.choice(agents_list)
                # Find agents in same or adjacent region
                candidates = [a for a in agents_list if a.config.id != a1.config.id 
                             and a.config.id not in a1.config.connections]
                if candidates:
                    a2 = random.choice(candidates)
                    # Higher chance for same region
                    grow_chance = 0.3 if a2.config.region == a1.config.region else 0.05
                    if random.random() < grow_chance:
                        self._grow_connection(a1.config.id, a2.config.id)
    
    # ─── Auto-Checkpoint ───
    
    def _start_auto_checkpoint(self):
        """Start the auto-checkpoint timer."""
        if self.checkpoint_timer:
            self.checkpoint_timer.cancel()
        
        def _checkpoint_loop():
            while self.running:
                time.sleep(self.auto_checkpoint_interval)
                if not self.running:
                    break
                try:
                    name = f"auto-{datetime.now().strftime('%H%M%S')}"
                    if self.project_name:
                        name = f"{self.project_name}-{name}"
                    self.save_snapshot(name)
                    self.last_checkpoint = time.time()
                    socketio.emit('checkpoint_saved', {'name': name, 'timestamp': time.time()})
                    logger.info(f"📸 Auto-checkpoint: {name}")
                except Exception as e:
                    logger.error(f"Checkpoint failed: {e}")
        
        self.checkpoint_timer = threading.Thread(target=_checkpoint_loop, daemon=True)
        self.checkpoint_timer.start()
    
    def emergency_stop(self):
        """EMERGENCY STOP — immediately halt ALL agent activity. No cleanup, no saving."""
        self.running = False
        self.mode = "emergency_stopped"
        
        # Kill all agent states immediately
        for state in self.agents.values():
            state.status = "killed"
            state.config.enabled = False
        
        # Force-unload Ollama models used by the lab
        models_to_unload = set()
        for state in self.agents.values():
            models_to_unload.add(state.config.model)
        
        for model in models_to_unload:
            try:
                requests.post(f"{OLLAMA_URL}/api/generate", json={
                    "model": model, "keep_alive": 0
                }, timeout=5)
                logger.info(f"E-STOP: Unloaded {model}")
            except:
                pass
        
        # Close log file
        if self.log_file:
            try:
                self.log_file.close()
            except:
                pass
            self.log_file = None
        
        socketio.emit('emergency_stop', {'timestamp': time.time()})
        logger.warning("⚠️ EMERGENCY STOP executed — all agents killed, models unloaded")
        return True
    
    def get_monitoring(self) -> dict:
        """Get detailed monitoring data for analytics."""
        now = time.time()
        agent_stats = []
        
        for aid, state in self.agents.items():
            uptime = now - state.started_at if state.started_at else 0
            think_rate = state.think_count / max(uptime, 1) * 60  # thinks per minute
            msg_rate = state.message_count / max(uptime, 1) * 60
            
            agent_stats.append({
                'id': aid,
                'name': state.config.name,
                'role': state.config.role,
                'region': state.config.region,
                'status': state.status,
                'model': state.config.model,
                'think_count': state.think_count,
                'message_count': state.message_count,
                'think_rate': round(think_rate, 1),
                'msg_rate': round(msg_rate, 1),
                'uptime': round(uptime),
                'last_active': round(now - state.last_active, 1) if state.last_active else None,
                'memory_size': len(state.memory),
                'enabled': state.config.enabled,
                'temperature': state.config.temperature,
                'think_interval': state.config.think_interval,
            })
        
        # Message type distribution
        msg_types = {}
        with self.lock:
            for msg in list(self.messages)[-500:]:
                t = msg.msg_type
                msg_types[t] = msg_types.get(t, 0) + 1
        
        # Region activity
        region_activity = {}
        for s in agent_stats:
            r = s['region'] or 'unassigned'
            if r not in region_activity:
                region_activity[r] = {'total_thinks': 0, 'total_msgs': 0, 'active_count': 0, 'agent_count': 0}
            region_activity[r]['total_thinks'] += s['think_count']
            region_activity[r]['total_msgs'] += s['message_count']
            region_activity[r]['agent_count'] += 1
            if s['status'] in ('thinking', 'speaking'):
                region_activity[r]['active_count'] += 1
        
        return {
            'session_id': self.session_id,
            'session_name': self.session_name,
            'mode': self.mode,
            'running': self.running,
            'tick_count': self.tick_count,
            'total_messages': len(self.messages),
            'uptime': round(now - (min(s.started_at for s in self.agents.values() if s.started_at) if self.agents else now)),
            'agents': agent_stats,
            'msg_types': msg_types,
            'region_activity': region_activity,
        }
    
    def _agent_loop(self, agent_id: str):
        """Continuous think loop for an agent."""
        while self.running:
            state = self.agents.get(agent_id)
            if not state or not state.config.enabled:
                time.sleep(1)
                continue
                
            try:
                self._agent_think(agent_id)
            except Exception as e:
                logger.error(f"Agent {agent_id} error: {e}")
                
            time.sleep(state.config.think_interval)
    
    def _get_time_context(self) -> str:
        """Generate time awareness context for agents."""
        now = datetime.now()
        uptime = time.time() - (min(s.started_at for s in self.agents.values() if s.started_at) if self.agents else time.time())
        
        period = "morning" if 6 <= now.hour < 12 else "afternoon" if 12 <= now.hour < 17 else "evening" if 17 <= now.hour < 21 else "night"
        
        return (
            f"[TIME] {now.strftime('%I:%M %p')} ({period}) | "
            f"Date: {now.strftime('%A, %B %d, %Y')} | "
            f"Brain uptime: {int(uptime//60)}m {int(uptime%60)}s | "
            f"Think cycle: #{self.tick_count}"
        )
    
    # Role-specific idle thought prompts — what each region thinks about when there's no input
    IDLE_THOUGHTS = {
        "visual_cortex": "No visual input right now. Reflect on your last visual observations. What patterns did you notice? What would you expect to see next? Maintain spatial awareness.",
        "auditory_cortex": "No audio input. Reflect on recent sounds or speech patterns. What auditory context are you maintaining? Stay alert for new input.",
        "wernicke": "No language input to process. Review your understanding of recent communications. Are there any ambiguities? What context would help future comprehension?",
        "prefrontal": "As the executive center, assess the current state. What should the brain be doing right now? Are there pending tasks? What's the next priority? Plan ahead.",
        "broca": "No speech needed right now. Prepare potential responses. How would you express the current brain state? What words are forming?",
        "hippocampus": "Continuously consolidate recent memories. What patterns are emerging? What's worth remembering long-term? Connect new experiences to old ones.",
        "amygdala": "Assess emotional state. Is the brain calm or agitated? What's the overall mood? Monitor for anything that requires emotional response or urgency flagging.",
        "cerebellum": "Monitor motor readiness. What actions might be needed? Maintain coordination awareness. Review timing and sequencing of recent activities.",
    }
    
    def _agent_think(self, agent_id: str):
        """One think cycle for an agent — always active, never dormant."""
        state = self.agents[agent_id]
        cfg = state.config
        
        if not cfg.enabled:
            time.sleep(1)
            return
            
        state.status = "thinking"
        state.last_active = time.time()
        self.tick_count += 1
        
        # Emit status update
        socketio.emit('agent_updated', state.to_dict())
        
        # Gather NEW messages for this agent (sequence-based — prevents stale/duplicate reads)
        recent = []
        if cfg.listen:
            recent = self._get_new_messages_for(agent_id, cfg.connections)
        
        # ─── Build rich context ───
        context_parts = []
        
        # Time awareness (always present)
        context_parts.append(self._get_time_context())
        
        # Active directive (highest priority)
        if cfg.directive:
            context_parts.append(f"[ACTIVE DIRECTIVE]: {cfg.directive}")
        
        # New messages
        if recent:
            context_parts.append(f"\nNew messages ({len(recent)}):")
            for msg in recent[-10:]:
                sender = self.agents.get(msg.from_agent)
                sender_name = sender.config.name if sender else msg.from_agent
                context_parts.append(f"  [{sender_name}] (seq:{msg.seq}): {msg.content}")
        
        # Memory
        if cfg.remember and state.memory:
            context_parts.append(f"\nYour recent thoughts: {' | '.join(state.memory[-5:])}")
        
        # If no messages, use role-specific idle thinking (NOT dormancy)
        if not recent and not cfg.directive:
            idle_prompt = self.IDLE_THOUGHTS.get(cfg.role, "Think about the current state. What's on your mind?")
            context_parts.append(f"\n[IDLE THINK]: {idle_prompt}")
        
        context = "\n".join(context_parts)
        
        # Build the prompt based on mode
        if cfg.interaction_mode == "pipeline":
            prompt = f"{context}\n\nProcess and produce structured output."
        else:
            prompt = f"{context}\n\nRespond concisely: observation, thought, or communication."
        
        try:
            response = self._generate(state.config.model, state.config.system_prompt, 
                                       prompt, state.config.temperature, state.config.max_tokens)
        except Exception as e:
            state.status = "idle"
            return
        
        if not response.strip():
            state.status = "idle"
            return
            
        state.current_thought = response
        state.last_output = response
        state.think_count += 1
        state.status = "speaking"
        
        # Add to short-term memory
        state.memory.append(response[:200])
        if len(state.memory) > 20:
            state.memory = state.memory[-20:]
        
        # Emit thought
        socketio.emit('agent_thought', {
            'agent_id': agent_id,
            'thought': response,
            'tick': self.tick_count,
        })
        
        # Send to connected agents (if speaking is enabled)
        if not cfg.speak:
            state.status = "idle"
            socketio.emit('agent_updated', state.to_dict())
            return
            
        for target_id in state.config.connections:
            if target_id in self.agents:
                msg = Message(
                    id=uuid.uuid4().hex[:8],
                    from_agent=agent_id,
                    to_agent=target_id,
                    content=response,
                    timestamp=time.time(),
                    msg_type="thought",
                )
                self._post_message(msg)
                state.message_count += 1
        
        state.status = "idle"
        socketio.emit('agent_updated', state.to_dict())
    
    def _generate(self, model: str, system: str, prompt: str, temp: float, max_tokens: int) -> str:
        """Generate via Ollama."""
        resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model,
            "system": system,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"num_predict": max_tokens, "temperature": temp}
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        return ""
    
    def _log(self, msg: Message):
        """Log a message to the session file."""
        if self.log_file:
            self.log_file.write(json.dumps(msg.to_dict()) + "\n")
            self.log_file.flush()
    
    def _ingest_session(self):
        """Ingest session summary into RAG."""
        try:
            summary_parts = [f"# Neural Lab Session: {self.session_name}"]
            summary_parts.append(f"Mode: {self.mode}")
            summary_parts.append(f"Agents: {len(self.agents)}")
            summary_parts.append(f"Total ticks: {self.tick_count}")
            summary_parts.append(f"Messages: {len(self.messages)}")
            summary_parts.append("")
            
            for aid, state in self.agents.items():
                summary_parts.append(f"## {state.config.name} ({state.config.role})")
                summary_parts.append(f"Thinks: {state.think_count}, Messages: {state.message_count}")
                if state.last_output:
                    summary_parts.append(f"Last thought: {state.last_output[:200]}")
                summary_parts.append("")
            
            text = "\n".join(summary_parts)
            requests.post(f"{CONCIERGE_URL}/ingest", json={
                "text": text,
                "source": f"neural-lab/{self.session_id}",
                "agent": "neural-lab",
                "source_type": "neural-lab-session",
            }, timeout=10)
        except Exception as e:
            logger.error(f"RAG ingest failed: {e}")
    
    def save_snapshot(self, name: str) -> str:
        """Save current configuration as a named snapshot."""
        snap_id = f"snap-{int(time.time())}-{uuid.uuid4().hex[:4]}"
        snapshot = {
            "id": snap_id,
            "name": name,
            "created": datetime.now().isoformat(),
            "mode": self.mode,
            "agents": {aid: asdict(s.config) for aid, s in self.agents.items()},
        }
        path = SNAPSHOTS_DIR / f"{snap_id}.json"
        path.write_text(json.dumps(snapshot, indent=2))
        logger.info(f"Snapshot saved: {name} ({snap_id})")
        return snap_id
    
    def load_snapshot(self, snap_id: str) -> bool:
        """Load a saved snapshot."""
        path = SNAPSHOTS_DIR / f"{snap_id}.json"
        if not path.exists():
            return False
        snapshot = json.loads(path.read_text())
        
        with self.lock:
            self.agents.clear()
            self.messages.clear()
            
        for aid, cfg_dict in snapshot["agents"].items():
            cfg = AgentConfig(**cfg_dict)
            with self.lock:
                self.agents[aid] = AgentState(config=cfg)
        
        self.mode = snapshot.get("mode", "stopped")
        logger.info(f"Snapshot loaded: {snapshot['name']}")
        return True
    
    def list_snapshots(self) -> list:
        """List all saved snapshots."""
        snaps = []
        for f in sorted(SNAPSHOTS_DIR.glob("snap-*.json"), reverse=True):
            try:
                data = json.loads(f.read_text())
                snaps.append({
                    "id": data["id"],
                    "name": data["name"],
                    "created": data["created"],
                    "mode": data.get("mode", "?"),
                    "agent_count": len(data.get("agents", {})),
                })
            except:
                pass
        return snaps
    
    def broadcast_directive(self, directive: str, targets: dict = None):
        """
        Broadcast a directive/goal to agents.
        targets can filter by: role, region, tags, ids
        If targets is None, broadcasts to ALL agents.
        """
        count = 0
        for aid, state in self.agents.items():
            if targets:
                # Filter by criteria
                if 'ids' in targets and aid not in targets['ids']:
                    continue
                if 'roles' in targets and state.config.role not in targets['roles']:
                    continue
                if 'regions' in targets and state.config.region not in targets['regions']:
                    continue
                if 'tags' in targets:
                    if not any(t in state.config.tags for t in targets['tags']):
                        continue
            
            state.config.directive = directive
            count += 1
            
            # Also inject as a message so they see it immediately
            msg = Message(
                id=uuid.uuid4().hex[:8],
                from_agent="director",
                to_agent=aid,
                content=f"[DIRECTIVE] {directive}",
                timestamp=time.time(),
                msg_type="directive",
            )
            self._post_message(msg)
        
        socketio.emit('directive_broadcast', {
            'directive': directive,
            'targets': targets,
            'count': count,
        })
        logger.info(f"Directive broadcast to {count} agents: {directive[:80]}")
        return count
    
    def update_agents_bulk(self, updates: dict, targets: dict = None):
        """
        Bulk update agent configs.
        updates: dict of config fields to change
        targets: filter criteria (same as broadcast_directive)
        """
        count = 0
        for aid, state in self.agents.items():
            if targets:
                if 'ids' in targets and aid not in targets['ids']:
                    continue
                if 'roles' in targets and state.config.role not in targets['roles']:
                    continue
                if 'regions' in targets and state.config.region not in targets['regions']:
                    continue
                if 'tags' in targets:
                    if not any(t in state.config.tags for t in targets['tags']):
                        continue
            
            for key, val in updates.items():
                if hasattr(state.config, key):
                    setattr(state.config, key, val)
            count += 1
        
        logger.info(f"Bulk update {count} agents: {list(updates.keys())}")
        return count
    
    def set_interaction_mode(self, mode: str, targets: dict = None):
        """Set interaction mode for agents: 'community' or 'pipeline'."""
        return self.update_agents_bulk({'interaction_mode': mode}, targets)
    
    def get_agent_groups(self) -> dict:
        """Get agents grouped by role, region, and tags for the UI."""
        groups = {
            'by_role': {},
            'by_region': {},
            'by_tag': {},
        }
        for aid, state in self.agents.items():
            # By role
            role = state.config.role
            if role not in groups['by_role']:
                groups['by_role'][role] = []
            groups['by_role'][role].append(aid)
            
            # By region
            region = state.config.region or 'unassigned'
            if region not in groups['by_region']:
                groups['by_region'][region] = []
            groups['by_region'][region].append(aid)
            
            # By tag
            for tag in state.config.tags:
                if tag not in groups['by_tag']:
                    groups['by_tag'][tag] = []
                groups['by_tag'][tag].append(aid)
        
        return groups

    def inject_input(self, text: str, target: str = "wernicke-0"):
        """Inject external input (human message) into the system."""
        msg = Message(
            id=uuid.uuid4().hex[:8],
            from_agent="human",
            to_agent=target,
            content=text,
            timestamp=time.time(),
            msg_type="observation",
        )
        self._post_message(msg)
        return msg.id
    
    def ask(self, question: str, timeout: int = 30) -> dict:
        """
        Ask the brain a question — direct pipeline through regions.
        Routes: human → wernicke (comprehension) → prefrontal (reasoning) → broca (speech)
        """
        start = time.time()
        
        # Inject the question to wernicke
        self.inject_input(question, "wernicke-0")
        
        # Step 1: Wernicke's comprehension
        wernicke = next((s for s in self.agents.values() if 'wernicke' in s.config.role), None)
        comprehension = ""
        if wernicke:
            comprehension = self._generate(
                wernicke.config.model,
                wernicke.config.system_prompt,
                f"{self._get_time_context()}\n\n[HUMAN ASKS]: {question}\n\nParse this input. What is the human asking? What context is needed to answer?",
                wernicke.config.temperature, wernicke.config.max_tokens
            )
            msg = Message(id=uuid.uuid4().hex[:8], from_agent=wernicke.config.id,
                         to_agent="prefrontal-0", content=f"[COMPREHENSION] {comprehension}",
                         timestamp=time.time(), msg_type="response")
            self._post_message(msg)
        
        # Step 2: Prefrontal reasoning
        prefrontal = next((s for s in self.agents.values() if 'prefrontal' in s.config.role), None)
        reasoning = ""
        if prefrontal:
            memory_ctx = " | ".join(prefrontal.memory[-5:]) if prefrontal.memory else "No prior context"
            reasoning = self._generate(
                prefrontal.config.model,
                prefrontal.config.system_prompt,
                f"{self._get_time_context()}\n\n[HUMAN QUESTION]: {question}\n[WERNICKE'S COMPREHENSION]: {comprehension}\n[YOUR MEMORY]: {memory_ctx}\n\nReason about this and formulate a thoughtful answer.",
                prefrontal.config.temperature, 300
            )
            msg = Message(id=uuid.uuid4().hex[:8], from_agent=prefrontal.config.id,
                         to_agent="broca-0", content=f"[REASONING] {reasoning}",
                         timestamp=time.time(), msg_type="response")
            self._post_message(msg)
        
        # Step 3: Broca's speech production
        broca = next((s for s in self.agents.values() if 'broca' in s.config.role), None)
        response = ""
        if broca:
            response = self._generate(
                broca.config.model,
                "You are Broca's Area — the speech production center. Take the reasoning from Prefrontal Cortex and produce a clear, natural response to the human. Speak directly to them.",
                f"[HUMAN ASKED]: {question}\n[PREFRONTAL'S REASONING]: {reasoning}\n\nProduce a clear, helpful response:",
                broca.config.temperature, 400
            )
            msg = Message(id=uuid.uuid4().hex[:8], from_agent=broca.config.id,
                         to_agent="human", content=response,
                         timestamp=time.time(), msg_type="response")
            self._post_message(msg)
        
        elapsed = round(time.time() - start, 1)
        
        return {
            'ok': True,
            'responses': [{'agent': broca.config.id if broca else 'broca', 'name': "Broca's Area", 'text': response}],
            'primary': response,
            'elapsed': elapsed,
            'pipeline': {
                'comprehension': comprehension[:200],
                'reasoning': reasoning[:200],
                'response': response[:200],
            }
        }
    
    def rag_query(self, query: str, limit: int = 5) -> list:
        """Query the RAG knowledge store."""
        try:
            import subprocess
            result = subprocess.run(
                ["memquery", query],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
        return ""
    
    def web_search(self, query: str) -> str:
        """Search the web (via the orchestrator, not individual agents)."""
        try:
            # Use the Research Lab proxy
            resp = requests.get(
                f"http://localhost:8097/api/search?q={requests.utils.quote(query)}&limit=3",
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.error(f"Web search failed: {e}")
        return None
    
    def inject_knowledge(self, agent_id: str, query: str):
        """Pull RAG knowledge and inject it into an agent's context."""
        knowledge = self.rag_query(query)
        if knowledge:
            msg = Message(
                id=uuid.uuid4().hex[:8],
                from_agent="rag_system",
                to_agent=agent_id,
                content=f"[KNOWLEDGE] {knowledge[:1500]}",
                timestamp=time.time(),
                msg_type="knowledge",
            )
            self._post_message(msg)
            return True
        return False

    # ─── Region Documentation ───
    
    REGION_DOCS = {
        "frontal": {
            "name": "Frontal Lobe",
            "areas": ["Prefrontal Cortex", "Broca's Area"],
            "biology": "The frontal lobe is the seat of executive function — planning, decision-making, working memory, personality, and speech production. It's the most recently evolved part of the human brain and what makes us 'human'. Prefrontal cortex handles reasoning and judgment. Broca's area converts thoughts into language.",
            "our_implementation": "Prefrontal agents (3) are the central reasoning hub. They receive processed input from ALL other regions and make decisions. Broca's agents (2) produce the final speech output. Both use qwen3.5:2b (larger model) because reasoning and language production require more capability.",
            "math": "Decision weighting: Each input from other regions carries an implicit weight based on connection strength w(i→prefrontal). Prefrontal integrates: response = f(Σ w_i · input_i) where f is the LLM inference. Broca's output is constrained to be coherent language — it's the final filter.",
            "unique_trait": "Only region with 2b models (others use 0.8b). Acts as the 'conductor' — other regions provide information, frontal decides what to do with it.",
            "connections": "Receives from: Visual Cortex, Auditory Cortex, Hippocampus, Amygdala, Wernicke's. Sends to: Broca's, Cerebellum, Hippocampus.",
        },
        "temporal": {
            "name": "Temporal Lobe",
            "areas": ["Auditory Cortex", "Wernicke's Area", "Hippocampus"],
            "biology": "The temporal lobe processes auditory information, language comprehension, and memory. Auditory cortex handles sound processing. Wernicke's area understands language meaning. Hippocampus converts short-term memories to long-term storage — it's why you remember things.",
            "our_implementation": "Auditory Cortex (2) processes incoming audio/speech. Wernicke's (2) is the FIRST receiver of human input — it parses meaning and routes to appropriate regions. Hippocampus (2) manages memory consolidation and during sleep/dream mode, decides what to store long-term in RAG.",
            "math": "Memory consolidation: During sleep, hippocampus scores each memory m_i with importance(m_i) = frequency × recency × emotional_valence. High-scoring memories get promoted to RAG (long-term). Language parsing: Wernicke's extracts intent I from input text T: I = extract(T) where extract is LLM inference with comprehension-focused prompts.",
            "unique_trait": "Wernicke's is the gateway for ALL human input. Hippocampus is the only region that directly interfaces with the RAG long-term memory store. During sleep, hippocampus runs the consolidation pipeline.",
            "connections": "Wernicke's receives human input. Auditory receives sensory audio. Hippocampus receives from everyone (memory formation). All send to Prefrontal.",
        },
        "occipital": {
            "name": "Occipital Lobe",
            "areas": ["Visual Cortex"],
            "biology": "The occipital lobe is dedicated entirely to vision processing. It contains the primary visual cortex (V1) and higher visual areas that process increasingly complex features: edges → shapes → objects → scenes → faces. It's the first brain area to process what your eyes see.",
            "our_implementation": "3 Visual Cortex agents process visual input from cameras. When a camera frame arrives, it's sent to qwen3.5:4b (vision-capable model) which describes what it sees. The description becomes a real message routed to Prefrontal (for decisions) and Hippocampus (for memory).",
            "math": "Visual processing: image → vision_model(image) → description. The 4b model uses attention mechanisms over image patches: Attention(Q,K,V) = softmax(QK^T/√d_k)V where Q,K,V are derived from image patch embeddings. Multiple visual cortex agents can process different aspects in parallel.",
            "unique_trait": "Only region that uses the 4b vision model (multimodal). Directly interfaces with camera hardware via the Senses tab. Processes raw visual data that no other region can.",
            "connections": "Receives from: Camera (via /api/sense/vision). Sends to: Prefrontal Cortex, Hippocampus.",
        },
        "limbic": {
            "name": "Limbic System",
            "areas": ["Amygdala"],
            "biology": "The limbic system is the emotional center of the brain. The amygdala processes emotions — fear, reward, motivation, emotional memory. It's why you feel before you think. It can override rational thought in emergencies (fight-or-flight). It also tags memories with emotional significance.",
            "our_implementation": "2 Amygdala agents continuously assess emotional state. They tag inputs with emotional valence (positive/negative/neutral, urgency level). Their output influences Prefrontal decisions — a 'danger' tag from amygdala can override normal processing, just like real fear overrides logic.",
            "math": "Emotional valence: V(input) ∈ [-1, 1] where -1 is maximum negative, +1 maximum positive. Urgency: U(input) ∈ [0, 1]. These modulate Prefrontal response: final_response = prefrontal_output × (1 + U × sign(V)). High urgency amplifies, low urgency dampens.",
            "unique_trait": "Fastest to respond (shortest think interval). Can flag urgent messages that bypass normal processing order. Emotional tags persist in memory — emotional memories are stronger (just like in humans).",
            "connections": "Receives from: All sensory regions. Sends to: Prefrontal (emotional context), Hippocampus (emotional memory tagging).",
        },
        "hindbrain": {
            "name": "Hindbrain",
            "areas": ["Cerebellum"],
            "biology": "The cerebellum coordinates movement, balance, and procedural memory (how to ride a bike). It's also involved in timing, rhythm, and learning motor skills. Despite being small, it contains more neurons than the rest of the brain combined.",
            "our_implementation": "1 Cerebellum agent handles motor coordination and procedural workflows. It receives motion data from the phone's accelerometer/gyroscope and coordinates multi-step actions. When the brain decides to 'do' something, cerebellum plans the execution sequence.",
            "math": "Proprioceptive processing: total_acceleration = √(ax² + ay² + az²). Motion classification: still (<11), moderate (11-15), strong (>15). Tilt: θ = arctan(ay/az) for forward/backward, φ = arctan(ax/az) for left/right.",
            "unique_trait": "Only region that receives motion/proprioception data. Interfaces with the physical world through device sensors. Plans action sequences when directed by Prefrontal.",
            "connections": "Receives from: Prefrontal (action plans), Motion sensors. Sends to: (action execution).",
        },
    }
    
    def get_region_docs(self) -> dict:
        """Get documentation for all brain regions."""
        return self.REGION_DOCS
    
    # ─── Sensory Processing ───
    
    def process_vision(self, image_b64: str, camera: str = "back", model: str = "qwen3.5:4b") -> dict:
        """Process a camera frame through the Visual Cortex."""
        if not self.running:
            return {"ok": False, "error": "Brain not running"}
        
        # Send to visual cortex agents
        vc_agents = [s for s in self.agents.values() if 'visual_cortex' in s.config.role]
        if not vc_agents:
            return {"ok": False, "error": "No visual cortex agents"}
        
        results = []
        for vc in vc_agents[:2]:  # Send to first 2 visual cortex agents
            try:
                # Use Ollama vision API
                resp = requests.post(f"{OLLAMA_URL}/api/generate", json={
                    "model": model,
                    "prompt": f"You are the Visual Cortex ({camera} eye). Describe what you see in detail — objects, people, movement, colors, spatial layout. Be concise but thorough.",
                    "images": [image_b64],
                    "stream": False,
                    "options": {"temperature": 0.5, "num_predict": 200},
                }, timeout=30)
                
                if resp.ok:
                    result = resp.json().get('response', '')
                    vc.current_thought = f"[VISION-{camera}] {result}"
                    vc.last_output = result
                    vc.think_count += 1
                    vc.last_active = time.time()
                    vc.status = "speaking"
                    
                    # Route to connected agents as a real message
                    msg = Message(
                        id=uuid.uuid4().hex[:8],
                        from_agent=vc.config.id,
                        to_agent="prefrontal-0",
                        content=f"[VISUAL INPUT - {camera} camera] {result}",
                        timestamp=time.time(),
                        msg_type="observation",
                    )
                    self._post_message(msg)
                    vc.message_count += 1
                    
                    # Also send to hippocampus for memory
                    msg2 = Message(
                        id=uuid.uuid4().hex[:8],
                        from_agent=vc.config.id,
                        to_agent="hippocampus-0",
                        content=f"[VISUAL MEMORY] {result}",
                        timestamp=time.time(),
                        msg_type="observation",
                    )
                    self._post_message(msg2)
                    
                    results.append({"agent": vc.config.id, "description": result})
                    vc.status = "idle"
            except Exception as e:
                logger.error(f"Vision processing error: {e}")
                results.append({"agent": vc.config.id, "error": str(e)})
        
        return {"ok": True, "camera": camera, "results": results}
    
    def process_audio(self, text: str, source: str = "speech") -> dict:
        """Process transcribed audio through Auditory Cortex → Wernicke's."""
        if not self.running:
            return {"ok": False, "error": "Brain not running"}
        
        # Route to auditory cortex first
        ac_agents = [s for s in self.agents.values() if 'auditory_cortex' in s.config.role]
        for ac in ac_agents[:1]:
            msg = Message(
                id=uuid.uuid4().hex[:8],
                from_agent="sensory_input",
                to_agent=ac.config.id,
                content=f"[AUDIO - {source}] {text}",
                timestamp=time.time(),
                msg_type="observation",
            )
            self._post_message(msg)
        
        # Also route to Wernicke's for language comprehension
        wernicke_agents = [s for s in self.agents.values() if 'wernicke' in s.config.role]
        for w in wernicke_agents[:1]:
            msg = Message(
                id=uuid.uuid4().hex[:8],
                from_agent="sensory_input",
                to_agent=w.config.id,
                content=f"[SPEECH INPUT] {text}",
                timestamp=time.time(),
                msg_type="observation",
            )
            self._post_message(msg)
        
        return {"ok": True, "source": source, "routed_to": ["auditory_cortex", "wernicke"]}
    
    def process_motion(self, data: dict) -> dict:
        """Process accelerometer/gyroscope data through Cerebellum."""
        if not self.running:
            return {"ok": False, "error": "Brain not running"}
        
        accel = data.get('acceleration', {})
        rotation = data.get('rotation', {})
        orientation = data.get('orientation', {})
        
        motion_desc = []
        # Detect significant motion
        ax, ay, az = accel.get('x', 0), accel.get('y', 0), accel.get('z', 0)
        total_accel = (ax**2 + ay**2 + az**2) ** 0.5
        
        if total_accel > 15:
            motion_desc.append(f"Strong movement detected (accel={total_accel:.1f})")
        elif total_accel > 11:
            motion_desc.append(f"Moderate movement (accel={total_accel:.1f})")
        else:
            motion_desc.append(f"Stable/still (accel={total_accel:.1f})")
        
        alpha = orientation.get('alpha', 0)
        beta = orientation.get('beta', 0)
        gamma = orientation.get('gamma', 0)
        
        if abs(beta) > 45:
            motion_desc.append(f"Tilted {'forward' if beta > 0 else 'backward'} {abs(beta):.0f}°")
        if abs(gamma) > 30:
            motion_desc.append(f"Tilted {'right' if gamma > 0 else 'left'} {abs(gamma):.0f}°")
        
        desc = ". ".join(motion_desc)
        
        # Route to cerebellum
        cb = [s for s in self.agents.values() if 'cerebellum' in s.config.role]
        for c in cb:
            msg = Message(
                id=uuid.uuid4().hex[:8],
                from_agent="sensory_input",
                to_agent=c.config.id,
                content=f"[PROPRIOCEPTION] {desc}",
                timestamp=time.time(),
                msg_type="observation",
            )
            self._post_message(msg)
        
        return {"ok": True, "description": desc}
    
    # ─── Narrator Agent ───
    
    def _get_narrator_system_prompt(self) -> str:
        """Build the narrator's system prompt with full architecture knowledge."""
        # Load architecture doc for full context
        arch_path = Path(__file__).parent / "ARCHITECTURE.md"
        arch_summary = ""
        if arch_path.exists():
            try:
                full = arch_path.read_text()
                # Extract key sections (first ~3000 chars covers architecture + regions)
                arch_summary = full[:3000]
            except:
                pass
        
        return f"""You are the Narrator for the Neural Lab — a simulated brain made of language model agents.

YOUR ROLE: You observe everything happening in the brain and explain it to the human operator. You have FULL understanding of how this system works.

ARCHITECTURE KNOWLEDGE:
{arch_summary}

KEY FACTS:
- 17 agents across 8 brain regions (visual cortex, auditory cortex, Wernicke's, prefrontal, Broca's, hippocampus, amygdala, cerebellum)
- Each agent runs a continuous think loop: gather messages → build context → generate via Ollama → send to connected agents
- Messages have global sequence numbers (monotonically increasing) to prevent stale reads
- Plasticity: Hebbian learning (strengthen used connections), pruning (weaken unused), neurogenesis (grow new)
- Sleep/dream: hippocampus consolidates → prefrontal rationalizes → stored in RAG
- Human input goes: Wernicke's (comprehension) → Prefrontal (reasoning) → Broca's (speech production)
- All data is REAL — every message is a real LLM inference, every dot on the brain map is a real message

CONVERSATION HISTORY (your previous exchanges with the human):
{{history}}

Be specific. Reference actual agent names, regions, sequence numbers. Explain both WHAT is happening and WHY (based on the architecture). If the human asks about a feature, explain how it works technically."""
    
    def _get_narrator_history(self) -> str:
        """Get formatted narrator conversation history."""
        if not hasattr(self, '_narrator_history'):
            self._narrator_history = []
        return "\n".join(
            f"{'Human' if h['role']=='human' else 'Narrator'}: {h['content'][:200]}"
            for h in self._narrator_history[-10:]
        ) or "(No previous conversation)"
    
    def _save_narrator_exchange(self, question: str, response: str, model: str):
        """Save narrator exchange to history and ingest to RAG."""
        if not hasattr(self, '_narrator_history'):
            self._narrator_history = []
        
        self._narrator_history.append({'role': 'human', 'content': question, 'timestamp': time.time()})
        self._narrator_history.append({'role': 'narrator', 'content': response, 'model': model, 'timestamp': time.time()})
        
        # Keep last 50 exchanges
        if len(self._narrator_history) > 100:
            self._narrator_history = self._narrator_history[-100:]
        
        # Ingest to RAG with proper labeling
        try:
            requests.post(f"{CONCIERGE_URL}/ingest", json={
                "text": f"[Neural Lab Narrator Chat]\nHuman: {question}\nNarrator ({model}): {response}",
                "source": f"neural-lab-narrator-{self.session_id or 'no-session'}",
                "source_type": "neural-lab-narrator",
                "agent": "neural-lab-narrator",
            }, timeout=5)
        except:
            pass
        
        # Also save to disk
        try:
            history_path = DATA_DIR / "narrator-history.jsonl"
            with open(history_path, 'a') as f:
                f.write(json.dumps({
                    'session': self.session_id,
                    'question': question,
                    'response': response,
                    'model': model,
                    'timestamp': time.time(),
                    'brain_mode': self.mode,
                    'agent_count': len(self.agents),
                    'tick_count': self.tick_count,
                }) + '\n')
        except:
            pass
    
    def narrate(self, model: str = "qwen3.5:0.8b") -> dict:
        """
        Get a narrator summary of what the brain is currently doing.
        This watches all recent messages and explains the state in plain language.
        """
        # Gather recent messages
        with self.lock:
            recent = list(self.messages)[-30:]
        
        if not recent:
            return {"ok": True, "summary": "The brain is quiet — no recent activity.", "model": model}
        
        # Build a digest
        lines = []
        for msg in recent:
            sender = self.agents.get(msg.from_agent)
            receiver = self.agents.get(msg.to_agent)
            s_name = sender.config.name if sender else msg.from_agent
            r_name = receiver.config.name if receiver else msg.to_agent
            s_region = sender.config.region if sender else '?'
            lines.append(f"[{s_region}/{s_name} → {r_name}] ({msg.msg_type}) {msg.content[:100]}")
        
        # Region summary
        region_states = {}
        for aid, state in self.agents.items():
            r = state.config.region or 'other'
            if r not in region_states:
                region_states[r] = {'active': 0, 'total': 0, 'thoughts': []}
            region_states[r]['total'] += 1
            if state.status in ('thinking', 'speaking'):
                region_states[r]['active'] += 1
            if state.last_output:
                region_states[r]['thoughts'].append(state.last_output[:80])
        
        region_summary = "\n".join(
            f"- {r}: {d['active']}/{d['total']} active. Recent: {d['thoughts'][-1][:60] if d['thoughts'] else 'idle'}"
            for r, d in region_states.items()
        )
        
        prompt = f"""You are observing a simulated brain with {len(self.agents)} neural agents across regions.

REGION STATUS:
{region_summary}

RECENT MESSAGES ({len(lines)}):
{chr(10).join(lines[-15:])}

Explain in 3-4 sentences what the brain is doing right now. What regions are most active? What are they thinking about? Is anything interesting happening? Speak naturally, like a neuroscientist watching a live brain scan."""
        
        try:
            sys_prompt = self._get_narrator_system_prompt().replace('{{history}}', self._get_narrator_history())
            result = self._generate(model, sys_prompt, prompt, 0.7, 250)
            self._save_narrator_exchange("[auto-summary request]", result, model)
            return {"ok": True, "summary": result, "model": model, "msg_count": len(recent)}
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def get_connections_graph(self) -> dict:
        """Get the full connection graph for node visualization."""
        nodes = []
        edges = []
        
        for aid, state in self.agents.items():
            nodes.append({
                'id': aid,
                'name': state.config.name,
                'role': state.config.role,
                'region': state.config.region,
                'color': state.config.color,
                'model': state.config.model,
                'status': state.status,
                'think_count': state.think_count,
                'message_count': state.message_count,
                'enabled': state.config.enabled,
                'listen': state.config.listen,
                'speak': state.config.speak,
                'vision': state.config.vision,
                'remember': state.config.remember,
                'temperature': state.config.temperature,
                'max_tokens': state.config.max_tokens,
                'think_interval': state.config.think_interval,
                'directive': state.config.directive,
                'last_output': state.last_output[:200] if state.last_output else '',
            })
            
            for target in state.config.connections:
                if target in self.agents:
                    key = f"{aid}->{target}"
                    edges.append({
                        'from': aid,
                        'to': target,
                        'active': state.status in ('speaking', 'thinking'),
                        'strength': self.connection_strengths.get(key, 0.5),
                    })
        
        # Recent message flow for animation
        recent_flows = []
        with self.lock:
            for msg in list(self.messages)[-30:]:
                if msg.from_agent in self.agents and msg.to_agent in self.agents:
                    recent_flows.append({
                        'from': msg.from_agent,
                        'to': msg.to_agent,
                        'timestamp': msg.timestamp,
                    })
        
        return {'nodes': nodes, 'edges': edges, 'recent_flows': recent_flows}
    
    def get_state(self) -> dict:
        """Get full lab state for the UI."""
        return {
            "mode": self.mode,
            "running": self.running,
            "session_id": self.session_id,
            "session_name": self.session_name,
            "tick_count": self.tick_count,
            "agent_count": len(self.agents),
            "message_count": len(self.messages),
            "agents": {aid: s.to_dict() for aid, s in self.agents.items()},
            "recent_messages": [m.to_dict() for m in list(self.messages)[-100:]],
        }

# ─── Global Lab Instance ───
lab = NeuralLab()

# ─── API Routes ───

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"ok": True, "service": "neural-lab", "version": "0.1.0",
                    "mode": lab.mode, "agents": len(lab.agents)})

@app.route('/api/state', methods=['GET'])
def get_state():
    return jsonify(lab.get_state())

@app.route('/api/start', methods=['POST'])
def start_lab():
    data = request.get_json() or {}
    mode = data.get('mode', 'brain')
    name = data.get('name', '')
    
    if mode == 'brain':
        lab.create_brain(data.get('config'))
    elif mode == 'simulation':
        agents = data.get('agents', [])
        if not agents:
            return jsonify({"error": "No agents provided for simulation"}), 400
        lab.create_simulation(agents)
    
    success = lab.start(mode, name)
    return jsonify({"ok": success, "agents": len(lab.agents), "session": lab.session_id})

@app.route('/api/stop', methods=['POST'])
def stop_lab():
    lab.stop()
    return jsonify({"ok": True})

@app.route('/api/estop', methods=['POST'])
def emergency_stop():
    """EMERGENCY STOP — immediately kill all agents and unload models."""
    lab.emergency_stop()
    return jsonify({"ok": True, "action": "emergency_stop"})

@app.route('/api/monitoring', methods=['GET'])
def get_monitoring():
    """Detailed monitoring data."""
    return jsonify(lab.get_monitoring())

@app.route('/api/sleep', methods=['POST'])
def sleep_lab():
    """Enter sleep/dream mode — consolidate and rationalize."""
    ok = lab.sleep()
    return jsonify({"ok": ok, "mode": lab.mode})

@app.route('/api/wake', methods=['POST'])
def wake_lab():
    """Wake from sleep."""
    ok = lab.wake()
    return jsonify({"ok": ok, "mode": lab.mode})

@app.route('/api/intercept', methods=['GET'])
def intercept():
    """Get intercepted messages — everything flowing between agents."""
    limit = request.args.get('limit', 50, type=int)
    messages = list(lab.intercepted)[-limit:]
    return jsonify({"ok": True, "messages": messages, "total": len(lab.intercepted)})

@app.route('/api/inject/random', methods=['POST'])
def inject_random():
    """Inject a message into a random agent's pipeline."""
    import random
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "text required"}), 400
    if not lab.agents:
        return jsonify({"error": "no agents running"}), 400
    target = random.choice(list(lab.agents.keys()))
    msg_id = lab.inject_input(text, target)
    return jsonify({"ok": True, "target": target, "target_name": lab.agents[target].config.name, "message_id": msg_id})

@app.route('/api/dreams', methods=['GET'])
def get_dreams():
    """Get dream/sleep consolidation log."""
    return jsonify({"ok": True, "dreams": lab.sleep_log})

@app.route('/api/plasticity', methods=['GET'])
def get_plasticity():
    """Get plasticity state."""
    return jsonify({
        "ok": True,
        "enabled": lab.plasticity_enabled,
        "connection_strengths": lab.connection_strengths,
        "changes": lab.plasticity_log[-50:],
        "total_changes": len(lab.plasticity_log),
    })

@app.route('/api/plasticity', methods=['POST'])
def set_plasticity():
    """Toggle plasticity (training mode on/off)."""
    data = request.get_json() or {}
    lab.plasticity_enabled = data.get('enabled', not lab.plasticity_enabled)
    return jsonify({"ok": True, "enabled": lab.plasticity_enabled})

@app.route('/api/project', methods=['POST'])
def set_project():
    """Set project name for this session."""
    data = request.get_json() or {}
    lab.project_name = data.get('name', '')
    return jsonify({"ok": True, "project": lab.project_name})

@app.route('/api/checkpoint', methods=['POST'])
def manual_checkpoint():
    """Save a manual checkpoint."""
    data = request.get_json() or {}
    name = data.get('name', f"manual-{datetime.now().strftime('%H%M%S')}")
    if lab.project_name:
        name = f"{lab.project_name}-{name}"
    snap_id = lab.save_snapshot(name)
    lab.last_checkpoint = time.time()
    return jsonify({"ok": True, "name": name, "snapshot": snap_id})

@app.route('/api/narrate', methods=['GET'])
def narrate():
    """Get narrator summary of current brain activity."""
    model = request.args.get('model', 'qwen3.5:0.8b')
    return jsonify(lab.narrate(model))

@app.route('/api/narrator/chat', methods=['POST'])
def narrator_chat():
    """Chat with the narrator about the brain. Full context, persistent history, RAG-ingested."""
    data = request.get_json() or {}
    question = data.get('question', '')
    model = data.get('model', 'qwen3.5:0.8b')
    if not question:
        return jsonify({"error": "question required"}), 400
    
    # Build rich context
    with lab.lock:
        recent = list(lab.messages)[-20:]
    
    msg_digest = "\n".join(
        f"seq:{m.seq} [{m.from_agent} → {m.to_agent}] ({m.msg_type}) {m.content[:80]}"
        for m in recent
    )
    
    region_info = {}
    for aid, state in lab.agents.items():
        r = state.config.region or 'other'
        if r not in region_info:
            region_info[r] = {'agents': [], 'models': set()}
        region_info[r]['agents'].append(f"{state.config.name}: {state.status} ({state.think_count} thinks, {state.message_count} msgs)")
        region_info[r]['models'].add(state.config.model)
    
    # Connection strengths summary
    strong = [(k, v) for k, v in lab.connection_strengths.items() if v > 0.6]
    weak = [(k, v) for k, v in lab.connection_strengths.items() if v < 0.2]
    
    context = f"""CURRENT BRAIN STATE:
Mode: {lab.mode} | Agents: {len(lab.agents)} | Ticks: {lab.tick_count} | Messages: {len(lab.messages)}
Plasticity: {'TRAINING' if lab.plasticity_enabled else 'TESTING'} | Session: {lab.session_id}

REGIONS:
{chr(10).join(f'{r}: models={list(d["models"])}, {chr(10).join(d["agents"])}' for r, d in region_info.items())}

STRONGEST CONNECTIONS ({len(strong)}): {', '.join(f'{k}={v:.2f}' for k,v in sorted(strong, key=lambda x:-x[1])[:5])}
WEAKEST CONNECTIONS ({len(weak)}): {', '.join(f'{k}={v:.2f}' for k,v in sorted(weak, key=lambda x:x[1])[:5])}

RECENT MESSAGES (last {len(recent)}):
{msg_digest[-1500:]}

HUMAN QUESTION: {question}"""
    
    try:
        sys_prompt = lab._get_narrator_system_prompt().replace('{{history}}', lab._get_narrator_history())
        result = lab._generate(model, sys_prompt, context, 0.7, 400)
        lab._save_narrator_exchange(question, result, model)
        return jsonify({"ok": True, "response": result, "model": model})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/api/narrator/history', methods=['GET'])
def narrator_history():
    """Get narrator conversation history."""
    history = getattr(lab, '_narrator_history', [])
    return jsonify({"ok": True, "history": history[-50:], "total": len(history)})

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get detailed documentation for all brain regions."""
    return jsonify({"ok": True, "regions": lab.get_region_docs()})

# ─── Sensory Input API ───

@app.route('/api/sense/vision', methods=['POST'])
def sense_vision():
    """Process a camera frame. Expects {image: base64, camera: 'front'|'back', model: optional}."""
    data = request.get_json() or {}
    image = data.get('image', '')
    camera = data.get('camera', 'back')
    model = data.get('model', 'qwen3.5:4b')
    if not image:
        return jsonify({"error": "image (base64) required"}), 400
    # Strip data URL prefix if present
    if ',' in image:
        image = image.split(',', 1)[1]
    return jsonify(lab.process_vision(image, camera, model))

@app.route('/api/sense/audio', methods=['POST'])
def sense_audio():
    """Process transcribed audio. Expects {text: string, source: 'speech'|'ambient'}."""
    data = request.get_json() or {}
    text = data.get('text', '')
    source = data.get('source', 'speech')
    if not text:
        return jsonify({"error": "text required"}), 400
    return jsonify(lab.process_audio(text, source))

@app.route('/api/sense/motion', methods=['POST'])
def sense_motion():
    """Process motion data. Expects {acceleration: {x,y,z}, rotation: {alpha,beta,gamma}, orientation: {alpha,beta,gamma}}."""
    data = request.get_json() or {}
    return jsonify(lab.process_motion(data))

@app.route('/api/sense/transcribe', methods=['POST'])
def sense_transcribe():
    """Transcribe audio blob via Whisper, then route through brain."""
    import subprocess, tempfile, base64
    data = request.get_json() or {}
    audio_b64 = data.get('audio', '')
    if not audio_b64:
        return jsonify({"error": "audio (base64) required"}), 400
    
    # Strip data URL prefix
    if ',' in audio_b64:
        audio_b64 = audio_b64.split(',', 1)[1]
    
    try:
        with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
            f.write(base64.b64decode(audio_b64))
            tmp_path = f.name
        
        # Transcribe with whisper tiny
        result = subprocess.run(
            ['whisper', tmp_path, '--model', 'tiny', '--output_format', 'txt', '--output_dir', '/tmp'],
            capture_output=True, text=True, timeout=30
        )
        
        # Read transcription
        txt_path = tmp_path.replace('.webm', '.txt')
        import os
        text = ''
        if os.path.exists(txt_path):
            text = open(txt_path).read().strip()
            os.unlink(txt_path)
        os.unlink(tmp_path)
        
        if text:
            # Route through brain
            lab.process_audio(text, 'speech')
            return jsonify({"ok": True, "text": text, "routed": True})
        else:
            return jsonify({"ok": True, "text": "", "routed": False, "note": "No speech detected"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

@app.route('/api/checkpoint/interval', methods=['POST'])
def set_checkpoint_interval():
    """Set auto-checkpoint interval in seconds."""
    data = request.get_json() or {}
    lab.auto_checkpoint_interval = max(60, data.get('interval', 300))
    return jsonify({"ok": True, "interval": lab.auto_checkpoint_interval})

@app.route('/api/inject', methods=['POST'])
def inject():
    data = request.get_json() or {}
    text = data.get('text', '')
    target = data.get('target', 'wernicke-0')
    if not text:
        return jsonify({"error": "text required"}), 400
    msg_id = lab.inject_input(text, target)
    return jsonify({"ok": True, "message_id": msg_id})

@app.route('/api/agent/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    if agent_id not in lab.agents:
        return jsonify({"error": "not found"}), 404
    return jsonify(lab.agents[agent_id].to_dict())

@app.route('/api/agent/<agent_id>', methods=['PATCH'])
def update_agent(agent_id):
    if agent_id not in lab.agents:
        return jsonify({"error": "not found"}), 404
    data = request.get_json() or {}
    cfg = lab.agents[agent_id].config
    for key in ['temperature', 'max_tokens', 'think_interval', 'system_prompt', 
                'enabled', 'connections', 'model', 'name',
                'listen', 'speak', 'vision', 'remember', 'directive']:
        if key in data:
            setattr(cfg, key, data[key])
    return jsonify({"ok": True})

@app.route('/api/agents/add', methods=['POST'])
def add_agent():
    """Add a new agent. {role, region, name, model, connections, system_prompt}"""
    data = request.get_json() or {}
    return jsonify(lab.add_agent(data))

@app.route('/api/agents/remove', methods=['POST'])
def remove_agent():
    """Remove an agent. {id: agent_id}"""
    data = request.get_json() or {}
    agent_id = data.get('id', '')
    if not agent_id:
        return jsonify({"error": "id required"}), 400
    return jsonify(lab.remove_agent(agent_id))

@app.route('/api/snapshots', methods=['GET'])
def list_snapshots():
    return jsonify({"snapshots": lab.list_snapshots()})

@app.route('/api/snapshots', methods=['POST'])
def save_snapshot():
    data = request.get_json() or {}
    name = data.get('name', f"Snapshot {datetime.now().strftime('%H:%M')}")
    snap_id = lab.save_snapshot(name)
    return jsonify({"ok": True, "id": snap_id})

@app.route('/api/snapshots/<snap_id>/load', methods=['POST'])
def load_snapshot(snap_id):
    ok = lab.load_snapshot(snap_id)
    return jsonify({"ok": ok})

@app.route('/api/presets', methods=['GET'])
def get_presets():
    return jsonify({"presets": BRAIN_PRESETS})

@app.route('/api/directive', methods=['POST'])
def broadcast_directive():
    """Broadcast a directive to agents. Body: {directive, targets?}"""
    data = request.get_json() or {}
    directive = data.get('directive', '')
    if not directive:
        return jsonify({"error": "directive required"}), 400
    targets = data.get('targets')  # {ids?, roles?, regions?, tags?}
    count = lab.broadcast_directive(directive, targets)
    return jsonify({"ok": True, "count": count})

@app.route('/api/bulk-update', methods=['POST'])
def bulk_update():
    """Bulk update agent configs. Body: {updates: {field: value}, targets?}"""
    data = request.get_json() or {}
    updates = data.get('updates', {})
    if not updates:
        return jsonify({"error": "updates required"}), 400
    targets = data.get('targets')
    count = lab.update_agents_bulk(updates, targets)
    return jsonify({"ok": True, "count": count})

@app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set interaction mode. Body: {mode: 'community'|'pipeline', targets?}"""
    data = request.get_json() or {}
    mode = data.get('mode', 'community')
    targets = data.get('targets')
    count = lab.set_interaction_mode(mode, targets)
    return jsonify({"ok": True, "count": count})

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """Get agents grouped by role, region, tags."""
    return jsonify(lab.get_agent_groups())

@app.route('/api/ask', methods=['POST'])
def ask_brain():
    """Ask the brain a question and get a response from Broca's."""
    data = request.get_json() or {}
    question = data.get('question', '')
    timeout = data.get('timeout', 30)
    if not question:
        return jsonify({"error": "question required"}), 400
    result = lab.ask(question, timeout)
    return jsonify(result)

@app.route('/api/rag', methods=['POST'])
def rag_query():
    """Query RAG and optionally inject into an agent."""
    data = request.get_json() or {}
    query = data.get('query', '')
    agent_id = data.get('agent_id')
    if not query:
        return jsonify({"error": "query required"}), 400
    
    if agent_id:
        ok = lab.inject_knowledge(agent_id, query)
        return jsonify({"ok": ok, "injected_to": agent_id})
    else:
        result = lab.rag_query(query)
        return jsonify({"ok": True, "results": result})

@app.route('/api/search', methods=['POST'])
def web_search():
    """Search the web and optionally inject results into the brain."""
    data = request.get_json() or {}
    query = data.get('query', '')
    inject_to = data.get('inject_to')
    if not query:
        return jsonify({"error": "query required"}), 400
    results = lab.web_search(query)
    if inject_to and results:
        lab.inject_input(f"[WEB SEARCH: {query}]\n{json.dumps(results)[:1500]}", inject_to)
    return jsonify({"ok": True, "results": results})

@app.route('/api/graph', methods=['GET'])
def get_graph():
    """Get the full connection graph for node visualization."""
    return jsonify(lab.get_connections_graph())

@app.route('/api/toggle', methods=['POST'])
def toggle_capability():
    """Toggle agent capabilities. Body: {capability, value, targets?}"""
    data = request.get_json() or {}
    cap = data.get('capability')  # vision, listen, speak, remember, persistent, enabled
    val = data.get('value', True)
    targets = data.get('targets')
    if not cap:
        return jsonify({"error": "capability required"}), 400
    count = lab.update_agents_bulk({cap: val}, targets)
    return jsonify({"ok": True, "count": count, "capability": cap, "value": val})

# ═══════════════════════════════════════════
# ─── SIMULATION SANDBOX API ───
# ═══════════════════════════════════════════

sim = SimulationEngine()

def sim_tick_handler(state):
    """Emit simulation state via WebSocket."""
    socketio.emit('sim_tick', state)

sim.on_tick = sim_tick_handler

def sim_brain_callback(brain_agent_id: str, observation: dict) -> str:
    """Ask a brain agent what action to take given an observation."""
    if not lab.running or brain_agent_id not in lab.agents:
        return 'wait'
    
    state = lab.agents[brain_agent_id]
    obs_text = (
        f"[SIM] Position: ({observation['position']['x']}, {observation['position']['y']}), "
        f"Energy: {observation['energy']}, Score: {observation['score']}, "
        f"Visible agents: {observation['visible_agents']}, "
        f"Visible objects: {observation['visible_objects']}"
    )
    
    actions_list = ', '.join(ACTIONS.keys())
    prompt = (
        f"{obs_text}\n\n"
        f"Choose ONE action from: {actions_list}\n"
        f"Reply with just the action name."
    )
    
    try:
        result = lab._generate(state.config.model, state.config.system_prompt, prompt, 0.7, 20)
        # Extract action from response
        result_lower = result.strip().lower().replace(' ', '_')
        for action in ACTIONS:
            if action in result_lower:
                return action
        return 'move_forward'
    except Exception:
        return 'wait'

sim.brain_callback = sim_brain_callback

@app.route('/api/sim/environments', methods=['GET'])
def sim_environments():
    return jsonify({"ok": True, "environments": sim.get_environments()})

@app.route('/api/sim/state', methods=['GET'])
def sim_state():
    return jsonify({"ok": True, **sim.get_state()})

@app.route('/api/sim/start', methods=['POST'])
def sim_start():
    data = request.get_json() or {}
    env = data.get('environment', 'open_field')
    max_ticks = data.get('max_ticks', 1000)
    use_brain = data.get('use_brain', False)
    teams = data.get('teams', {})  # {agent_id: 'hider'|'seeker'|'neutral'}
    
    # Auto-create sim agents from brain agents if none exist
    if not sim.agents:
        colors = {'hider': '#4ecdc4', 'seeker': '#ff6b6b', 'neutral': '#ffd93d'}
        brain_agents = list(lab.agents.keys())[:6]  # Max 6 for performance
        for i, ba in enumerate(brain_agents):
            team = teams.get(ba, 'neutral')
            sim.add_agent(
                f'sim-{i}', ba, lab.agents[ba].config.name,
                team=team, color=colors.get(team, '#888')
            )
    
    if not use_brain:
        sim.brain_callback = None
    else:
        sim.brain_callback = sim_brain_callback
    
    sid = sim.start(env, max_ticks)
    return jsonify({"ok": True, "session": sid, "agents": len(sim.agents), "environment": env})

@app.route('/api/sim/stop', methods=['POST'])
def sim_stop():
    sim.stop()
    return jsonify({"ok": True})

@app.route('/api/sim/pause', methods=['POST'])
def sim_pause():
    sim.pause()
    return jsonify({"ok": True, "paused": sim.paused})

@app.route('/api/sim/agents', methods=['GET'])
def sim_agents_list():
    return jsonify({"ok": True, "agents": {k: v.to_dict() for k, v in sim.agents.items()}})

@app.route('/api/sim/agents/add', methods=['POST'])
def sim_add_agent():
    data = request.get_json() or {}
    brain_agent = data.get('brain_agent', '')
    name = data.get('name', f'Agent-{len(sim.agents)}')
    team = data.get('team', 'neutral')
    color = data.get('color', '#4ecdc4')
    sid = f'sim-{uuid.uuid4().hex[:4]}'
    agent = sim.add_agent(sid, brain_agent, name, team, color)
    return jsonify({"ok": True, "id": sid, "agent": agent.to_dict()})

@app.route('/api/sim/agents/remove', methods=['POST'])
def sim_remove_agent():
    data = request.get_json() or {}
    sim.remove_agent(data.get('id', ''))
    return jsonify({"ok": True})

@app.route('/api/sim/speed', methods=['POST'])
def sim_speed():
    data = request.get_json() or {}
    sim.tick_rate = max(0.01, min(1.0, data.get('tick_rate', 0.1)))
    return jsonify({"ok": True, "tick_rate": sim.tick_rate})

@app.route('/api/sim/reset', methods=['POST'])
def sim_reset():
    """Reset simulation but keep agents."""
    sim.stop()
    sim.tick = 0
    sim.events = []
    for agent in sim.agents.values():
        agent.energy = agent.max_energy
        agent.score = 0
        agent.alive = True
        agent.actions_taken = 0
    return jsonify({"ok": True})

@app.route('/api/sim/training', methods=['GET'])
def sim_training_stats():
    """Get RL training statistics."""
    return jsonify({"ok": True, **sim.get_training_stats()})

# ═══════════════════════════════════════════
# ─── RL TRAINING API ───
# ═══════════════════════════════════════════

rl_training = {
    'running': False,
    'model': None,
    'env': None,
    'algorithm': 'PPO',
    'total_timesteps': 0,
    'current_timesteps': 0,
    'episode': 0,
    'rewards': [],
    'best_reward': float('-inf'),
    'thread': None,
    'log': [],
    'model_path': None,
}

def _rl_train_thread(algo, environment, num_agents, total_timesteps, controlled_team):
    """Background RL training thread."""
    import torch
    from stable_baselines3 import PPO, A2C, SAC, DQN
    from stable_baselines3.common.callbacks import BaseCallback
    
    algos = {'PPO': PPO, 'A2C': A2C, 'DQN': DQN}
    AlgoClass = algos.get(algo, PPO)
    
    env = NeuralLabEnv(
        environment=environment,
        num_agents=num_agents,
        controlled_team=controlled_team,
        max_steps=500,
    )
    rl_training['env'] = env
    
    class ProgressCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.episode_rewards = []
            self.current_reward = 0
        
        def _on_step(self):
            rl_training['current_timesteps'] = self.num_timesteps
            
            # Track rewards
            if len(self.locals.get('rewards', [])) > 0:
                self.current_reward += self.locals['rewards'][0]
            
            if self.locals.get('dones', [False])[0]:
                rl_training['episode'] += 1
                rl_training['rewards'].append(round(self.current_reward, 3))
                if self.current_reward > rl_training['best_reward']:
                    rl_training['best_reward'] = self.current_reward
                
                # Keep last 100 episode rewards
                if len(rl_training['rewards']) > 100:
                    rl_training['rewards'] = rl_training['rewards'][-100:]
                
                # Emit progress via WebSocket
                socketio.emit('rl_progress', {
                    'episode': rl_training['episode'],
                    'reward': round(float(self.current_reward), 3),
                    'best': round(float(rl_training['best_reward']), 3),
                    'timesteps': self.num_timesteps,
                    'total': total_timesteps,
                })
                
                self.current_reward = 0
                
                # Log every 10 episodes
                if rl_training['episode'] % 10 == 0:
                    avg = sum(rl_training['rewards'][-10:]) / min(10, len(rl_training['rewards']))
                    rl_training['log'].append(
                        f"Ep {rl_training['episode']}: avg_reward={avg:.2f}, best={rl_training['best_reward']:.2f}"
                    )
            
            return rl_training['running']  # Return False to stop
    
    try:
        rl_training['log'].append(f"Starting {algo} training: {environment}, {num_agents} agents, {total_timesteps} steps")
        
        model = AlgoClass(
            "MlpPolicy", env,
            learning_rate=3e-4,
            verbose=0,
            device='cpu',  # Use CPU — GPU is for LLMs
        )
        rl_training['model'] = model
        rl_training['algorithm'] = algo
        rl_training['total_timesteps'] = total_timesteps
        
        model.learn(total_timesteps=total_timesteps, callback=ProgressCallback())
        
        # Save model
        save_dir = Path.home() / '.openclaw' / 'neural-lab' / 'rl-models'
        save_dir.mkdir(parents=True, exist_ok=True)
        model_path = save_dir / f"{algo.lower()}_{environment}_{int(time.time())}.zip"
        model.save(str(model_path))
        rl_training['model_path'] = str(model_path)
        rl_training['log'].append(f"Training complete. Model saved: {model_path.name}")
        
        socketio.emit('rl_complete', {
            'episodes': rl_training['episode'],
            'best_reward': round(rl_training['best_reward'], 3),
            'model_path': str(model_path),
        })
    except Exception as e:
        rl_training['log'].append(f"Training error: {e}")
        socketio.emit('rl_error', {'error': str(e)})
    finally:
        rl_training['running'] = False

@app.route('/api/rl/start', methods=['POST'])
def rl_start():
    """Start RL training. {algorithm, environment, num_agents, total_timesteps, controlled_team}"""
    if rl_training['running']:
        return jsonify({"error": "Training already running"}), 400
    
    data = request.get_json() or {}
    algo = data.get('algorithm', 'PPO')
    environment = data.get('environment', 'hide_and_seek')
    num_agents = data.get('num_agents', 4)
    total_timesteps = data.get('total_timesteps', 10000)
    controlled_team = data.get('controlled_team', 'seeker')
    
    if algo not in ['PPO', 'A2C', 'DQN']:
        return jsonify({"error": f"Unknown algorithm: {algo}"}), 400
    
    rl_training['running'] = True
    rl_training['episode'] = 0
    rl_training['rewards'] = []
    rl_training['best_reward'] = float('-inf')
    rl_training['current_timesteps'] = 0
    rl_training['log'] = []
    
    t = threading.Thread(target=_rl_train_thread, args=(algo, environment, num_agents, total_timesteps, controlled_team), daemon=True)
    rl_training['thread'] = t
    t.start()
    
    return jsonify({"ok": True, "algorithm": algo, "environment": environment, "total_timesteps": total_timesteps})

@app.route('/api/rl/stop', methods=['POST'])
def rl_stop():
    """Stop RL training."""
    rl_training['running'] = False
    return jsonify({"ok": True})

@app.route('/api/rl/status', methods=['GET'])
def rl_status():
    """Get RL training status."""
    avg_reward = 0
    if rl_training['rewards']:
        recent = rl_training['rewards'][-10:]
        avg_reward = sum(recent) / len(recent)
    
    return jsonify({
        "ok": True,
        "running": rl_training['running'],
        "algorithm": rl_training['algorithm'],
        "episode": rl_training['episode'],
        "timesteps": rl_training['current_timesteps'],
        "total_timesteps": rl_training['total_timesteps'],
        "best_reward": round(float(rl_training['best_reward']), 3),
        "avg_reward_10": round(float(avg_reward), 3),
        "rewards": [round(float(r), 3) for r in rl_training['rewards'][-50:]],
        "log": rl_training['log'][-20:],
        "model_path": rl_training.get('model_path'),
    })

@app.route('/api/rl/models', methods=['GET'])
def rl_models():
    """List saved RL models."""
    model_dir = Path.home() / '.openclaw' / 'neural-lab' / 'rl-models'
    if not model_dir.exists():
        return jsonify({"ok": True, "models": []})
    models = []
    for f in sorted(model_dir.glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True):
        models.append({
            'name': f.name,
            'path': str(f),
            'size_mb': round(f.stat().st_size / 1024 / 1024, 1),
            'modified': f.stat().st_mtime,
        })
    return jsonify({"ok": True, "models": models})

@app.route('/api/rl/evaluate', methods=['POST'])
def rl_evaluate():
    """Run a trained model for N episodes and return stats."""
    data = request.get_json() or {}
    model_path = data.get('model_path', '')
    episodes = data.get('episodes', 5)
    
    if not model_path or not Path(model_path).exists():
        return jsonify({"error": "model not found"}), 404
    
    from stable_baselines3 import PPO, A2C, DQN
    
    # Detect algo from filename
    algo_map = {'ppo': PPO, 'a2c': A2C, 'dqn': DQN}
    algo_name = Path(model_path).stem.split('_')[0]
    AlgoClass = algo_map.get(algo_name, PPO)
    
    env_name = Path(model_path).stem.split('_')[1] if '_' in Path(model_path).stem else 'hide_and_seek'
    
    env = NeuralLabEnv(environment=env_name, num_agents=4, max_steps=300)
    model = AlgoClass.load(model_path)
    
    results = []
    for ep in range(episodes):
        obs, _ = env.reset()
        total_reward = 0
        steps = 0
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            done = terminated or truncated
        results.append({'episode': ep, 'reward': round(total_reward, 3), 'steps': steps})
    
    avg = sum(r['reward'] for r in results) / len(results)
    return jsonify({"ok": True, "results": results, "avg_reward": round(avg, 3), "model": model_path})

# ═══════════════════════════════════════════
# ─── MODEL WORKSHOP API ───
# ═══════════════════════════════════════════

@app.route('/api/workshop/scan', methods=['GET'])
def workshop_scan():
    """Scan for model files."""
    models = scan_models()
    return jsonify({"ok": True, "models": models, "count": len(models)})

@app.route('/api/workshop/inspect', methods=['POST'])
def workshop_inspect():
    """Inspect a model file. {path: '/path/to/model'}"""
    data = request.get_json() or {}
    path = data.get('path', '')
    if not path or not Path(path).exists():
        return jsonify({"error": "file not found"}), 404
    info = inspect_model(path)
    return jsonify({"ok": True, **info})

# ═══════════════════════════════════════════
# ─── PLATFORM API ───
# ═══════════════════════════════════════════

@app.route('/api/platform', methods=['GET'])
def platform_info():
    """Full platform state: registry, assets, pipelines, extensions."""
    return jsonify({"ok": True, **platform.to_dict()})

@app.route('/api/platform/registry', methods=['GET'])
def platform_registry():
    """List all registered plugins. ?type=environment&tags=builtin"""
    ptype = request.args.get('type')
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None
    
    if ptype:
        try:
            pt = PluginType(ptype)
        except ValueError:
            return jsonify({"error": f"Unknown type: {ptype}"}), 400
        plugins = platform.registry.find(pt, tags)
    else:
        plugins = platform.registry.find(tags=tags)
    
    return jsonify({"ok": True, "plugins": [p.to_dict() for p in plugins], "count": len(plugins)})

@app.route('/api/platform/assets', methods=['GET'])
def platform_assets():
    """List assets. ?category=prefab&search=box"""
    category = request.args.get('category')
    search = request.args.get('search')
    tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None
    assets = platform.assets.find(category=category, tags=tags, search=search)
    return jsonify({"ok": True, "assets": [a.to_dict() for a in assets], "count": len(assets)})

@app.route('/api/platform/assets/<asset_id>', methods=['GET'])
def platform_asset_detail(asset_id):
    """Get single asset details."""
    asset = platform.assets.get(asset_id)
    if not asset:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True, **asset.to_dict()})

@app.route('/api/platform/extensions', methods=['GET'])
def platform_extensions():
    """List available extensions."""
    return jsonify({"ok": True, "extensions": platform.extensions.scan()})

@app.route('/api/platform/extensions/load', methods=['POST'])
def platform_extension_load():
    """Load an extension. {name}"""
    data = request.get_json() or {}
    name = data.get('name', '')
    result = platform.extensions.load(name)
    return jsonify(result)

@app.route('/api/platform/templates', methods=['GET'])
def platform_templates():
    """List environment templates."""
    templates = platform.assets.find(category='environment')
    return jsonify({"ok": True, "templates": [t.to_dict() for t in templates]})

@app.route('/api/platform/templates/<template_id>/apply', methods=['POST'])
def platform_template_apply(template_id):
    """Apply an environment template to the sim."""
    asset = platform.assets.get(template_id)
    if not asset:
        return jsonify({"error": "template not found"}), 404
    
    props = asset.properties
    sim.load_world({
        'environment': 'custom',
        'walls': props.get('walls', []),
        'objects': props.get('objects', []),
    })
    return jsonify({"ok": True, "template": asset.name})

@app.route('/api/workshop/duplicate', methods=['POST'])
def workshop_duplicate():
    """Duplicate a model for safe experimentation. {path, name?}"""
    data = request.get_json() or {}
    path = data.get('path', '')
    name = data.get('name', '')
    if not path or not Path(path).exists():
        return jsonify({"error": "source not found"}), 404
    result = duplicate_model(path, name)
    return jsonify(result)

@app.route('/api/workshop/explain', methods=['POST'])
def workshop_explain():
    """AI-explain a model. {path, model?}"""
    data = request.get_json() or {}
    path = data.get('path', '')
    ai_model = data.get('model', 'qwen3.5:2b')
    if not path or not Path(path).exists():
        return jsonify({"error": "file not found"}), 404
    info = inspect_model(path)
    explanation = generate_architecture_explanation(info, ai_model)
    return jsonify({"ok": True, "explanation": explanation})

# ═══════════════════════════════════════════
# ─── WORLD BUILDER API ───
# ═══════════════════════════════════════════

@app.route('/api/sim/world/add', methods=['POST'])
def sim_world_add():
    """Add an object to the world. {type: wall|box|food|flag|ramp, x, y, x2?, y2?}"""
    data = request.get_json() or {}
    obj_type = data.get('type', 'box')
    x = data.get('x', 300)
    y = data.get('y', 200)
    
    if obj_type == 'wall':
        x2 = data.get('x2', x + 80)
        y2 = data.get('y2', y)
        sim.add_wall(x, y, x2, y2)
    else:
        sim.add_object(x, y, obj_type)
    
    return jsonify({"ok": True, "type": obj_type})

@app.route('/api/sim/world/remove', methods=['POST'])
def sim_world_remove():
    """Remove object nearest to x,y. {x, y, radius?}"""
    data = request.get_json() or {}
    x = data.get('x', 0)
    y = data.get('y', 0)
    radius = data.get('radius', 20)
    removed = sim.remove_nearest(x, y, radius)
    return jsonify({"ok": True, "removed": removed})

@app.route('/api/sim/world/save', methods=['POST'])
def sim_world_save():
    """Save current world layout. {name}"""
    data = request.get_json() or {}
    name = data.get('name', f'world-{int(time.time())}')
    world_dir = Path.home() / '.openclaw' / 'neural-lab' / 'worlds'
    world_dir.mkdir(parents=True, exist_ok=True)
    
    state = sim.get_state()
    world_data = {
        'name': name,
        'environment': state.get('environment', ''),
        'walls': state.get('walls', []),
        'objects': state.get('objects', []),
        'world': state.get('world', {}),
    }
    path = world_dir / f'{name}.json'
    path.write_text(json.dumps(world_data, indent=2))
    return jsonify({"ok": True, "name": name, "path": str(path)})

@app.route('/api/sim/world/list', methods=['GET'])
def sim_world_list():
    """List saved worlds."""
    world_dir = Path.home() / '.openclaw' / 'neural-lab' / 'worlds'
    if not world_dir.exists():
        return jsonify({"ok": True, "worlds": []})
    worlds = []
    for f in sorted(world_dir.glob('*.json'), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text())
            worlds.append({
                'name': data.get('name', f.stem),
                'file': f.name,
                'walls': len(data.get('walls', [])),
                'objects': len(data.get('objects', [])),
            })
        except Exception:
            pass
    return jsonify({"ok": True, "worlds": worlds})

@app.route('/api/sim/world/load', methods=['POST'])
def sim_world_load():
    """Load a saved world. {name}"""
    data = request.get_json() or {}
    name = data.get('name', '')
    world_dir = Path.home() / '.openclaw' / 'neural-lab' / 'worlds'
    path = world_dir / f'{name}.json'
    if not path.exists():
        return jsonify({"error": "world not found"}), 404
    
    world_data = json.loads(path.read_text())
    sim.load_world(world_data)
    return jsonify({"ok": True, "name": name})

# ─── WebSocket ───

connected_clients = set()

@socketio.on('connect')
def ws_connect():
    from flask import request as flask_request
    connected_clients.add(flask_request.sid)
    emit('state', lab.get_state())
    socketio.emit('clients_count', {'count': len(connected_clients)})
    logger.info(f"Client connected: {flask_request.sid} (total: {len(connected_clients)})")

@socketio.on('disconnect')
def ws_disconnect():
    from flask import request as flask_request
    connected_clients.discard(flask_request.sid)
    socketio.emit('clients_count', {'count': len(connected_clients)})
    logger.info(f"Client disconnected (total: {len(connected_clients)})")

@app.route('/api/clients', methods=['GET'])
def get_clients():
    return jsonify({"ok": True, "count": len(connected_clients)})

# ─── Run ───

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8103, debug=False, allow_unsafe_werkzeug=True)
