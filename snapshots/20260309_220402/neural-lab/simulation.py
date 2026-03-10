"""
Neural Lab — Simulation Sandbox (Real Physics)
Pymunk (Chipmunk2D) physics engine + Gymnasium/PettingZoo RL interface.

Real physics: gravity, friction, elasticity, collision detection, joints.
RL-ready: observation/action spaces, reward functions, episode management.
Compatible with stable-baselines3 for PPO/A2C/SAC training.
"""

import math
import random
import time
import json
import uuid
import threading
from dataclasses import dataclass, field
from typing import Optional, Callable
import pymunk
import numpy as np

# ─── Constants ───

WORLD_W = 600
WORLD_H = 400
GRAVITY = (0, 0)  # Top-down view, no gravity
PHYSICS_DT = 1/60  # 60 Hz physics
COLLISION_TYPE_AGENT = 1
COLLISION_TYPE_WALL = 2
COLLISION_TYPE_OBJECT = 3

ACTIONS = {
    0: 'noop',
    1: 'move_forward',
    2: 'move_backward', 
    3: 'turn_left',
    4: 'turn_right',
    5: 'sprint',
    6: 'grab',
    7: 'push',
    8: 'look_around',
}
NUM_ACTIONS = len(ACTIONS)

# ─── Sim Agent ───

@dataclass
class SimAgent:
    id: str
    brain_agent: str
    name: str
    team: str = 'neutral'
    color: str = '#4ecdc4'
    speed: float = 200.0       # force applied
    turn_speed: float = 3.0    # radians/sec
    vision_range: float = 150.0
    vision_angle: float = math.pi / 2
    energy: float = 100.0
    max_energy: float = 100.0
    score: float = 0.0
    alive: bool = True
    actions_taken: int = 0
    last_action: str = 'noop'
    visible_agents: list = field(default_factory=list)
    visible_objects: list = field(default_factory=list)
    body: pymunk.Body = field(default=None, repr=False)
    shape: pymunk.Circle = field(default=None, repr=False)
    
    def to_dict(self):
        if self.body:
            px, py = float(self.body.position.x), float(self.body.position.y)
            vvx, vvy = float(self.body.velocity.x), float(self.body.velocity.y)
            ang = float(self.body.angle)
        else:
            px, py, vvx, vvy, ang = 0, 0, 0, 0, 0
        return {
            'id': self.id, 'brain_agent': self.brain_agent, 'name': self.name,
            'team': self.team, 'x': round(px, 2), 'y': round(py, 2),
            'vx': round(vvx, 2), 'vy': round(vvy, 2),
            'angle': round(ang, 3),
            'speed': self.speed, 'radius': 10,
            'color': self.color, 'energy': round(self.energy, 1),
            'max_energy': self.max_energy, 'vision_range': self.vision_range,
            'alive': self.alive, 'score': round(self.score, 2),
            'actions_taken': self.actions_taken, 'last_action': self.last_action,
            'visible_agents': self.visible_agents,
            'visible_objects': self.visible_objects,
        }

@dataclass
class SimObject:
    id: str
    obj_type: str
    color: str
    movable: bool
    body: pymunk.Body = field(default=None, repr=False)
    shape: pymunk.Shape = field(default=None, repr=False)
    width: float = 20
    height: float = 20
    
    def to_dict(self):
        if self.body:
            px, py = float(self.body.position.x), float(self.body.position.y)
        else:
            px, py = 0, 0
        return {
            'id': self.id, 'obj_type': self.obj_type, 'color': self.color,
            'movable': self.movable, 'x': round(px, 2), 'y': round(py, 2),
            'width': self.width, 'height': self.height,
        }

# ─── Environment Presets ───

ENVIRONMENTS = {
    'open_field': {
        'name': 'Open Field',
        'description': 'Empty arena with real physics. Agents explore freely.',
        'walls': [],
        'objects': [],
    },
    'hide_and_seek': {
        'name': 'Hide & Seek',
        'description': 'Boxes and ramps with real physics. Push objects to block lines of sight.',
        'walls': [
            {'x1': 150, 'y1': 100, 'x2': 150, 'y2': 250},
            {'x1': 350, 'y1': 150, 'x2': 350, 'y2': 300},
            {'x1': 200, 'y1': 300, 'x2': 400, 'y2': 300},
        ],
        'objects': [
            {'x': 100, 'y': 200, 'type': 'box', 'movable': True, 'mass': 5},
            {'x': 250, 'y': 150, 'type': 'box', 'movable': True, 'mass': 5},
            {'x': 400, 'y': 250, 'type': 'box', 'movable': True, 'mass': 5},
            {'x': 300, 'y': 100, 'type': 'ramp', 'movable': True, 'mass': 3},
        ],
    },
    'maze': {
        'name': 'Maze',
        'description': 'Navigate corridors with collision. Find the flag.',
        'walls': [
            {'x1': 100, 'y1': 0, 'x2': 100, 'y2': 300},
            {'x1': 200, 'y1': 100, 'x2': 200, 'y2': 400},
            {'x1': 300, 'y1': 0, 'x2': 300, 'y2': 250},
            {'x1': 400, 'y1': 150, 'x2': 400, 'y2': 400},
            {'x1': 500, 'y1': 0, 'x2': 500, 'y2': 300},
        ],
        'objects': [
            {'x': 550, 'y': 350, 'type': 'flag', 'movable': False},
        ],
    },
    'foraging': {
        'name': 'Foraging',
        'description': 'Collect food with real collision. Energy management matters.',
        'walls': [],
        'objects': [
            {'x': random.randint(50, 550), 'y': random.randint(50, 350), 'type': 'food', 'movable': False}
            for _ in range(15)
        ],
    },
}

# ─── Physics Simulation ───

class SimulationEngine:
    """Real physics simulation using pymunk (Chipmunk2D)."""
    
    def __init__(self):
        self.space: pymunk.Space = None
        self.agents: dict[str, SimAgent] = {}
        self.objects: list[SimObject] = []
        self.wall_shapes: list[pymunk.Shape] = []
        self.wall_defs: list[dict] = []
        
        self.running = False
        self.paused = False
        self.tick = 0
        self.episode = 0
        self.max_ticks = 1000
        self.tick_rate = 0.05  # 20 updates/sec to client
        self.physics_steps = 3  # physics sub-steps per tick
        self.environment = 'open_field'
        self.session_id = ''
        self.lock = threading.Lock()
        self.events: list[dict] = []
        self._thread = None
        
        self.on_tick: Callable = None
        self.brain_callback: Callable = None
        
        # RL tracking
        self.episode_rewards: dict[str, list] = {}
        self.cumulative_rewards: dict[str, float] = {}
        self.collision_log: list[dict] = []
    
    def _init_space(self):
        """Create a fresh physics space."""
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        self.space.damping = 0.8  # Friction-like damping
        
        # Collision callbacks
        self.space.on_collision(
            collision_type_a=COLLISION_TYPE_AGENT,
            collision_type_b=COLLISION_TYPE_AGENT,
            begin=self._on_collision,
        )
        self.space.on_collision(
            collision_type_a=COLLISION_TYPE_AGENT,
            collision_type_b=COLLISION_TYPE_OBJECT,
            begin=self._on_collision,
        )
        
        # Arena boundaries
        walls = [
            [(0, 0), (WORLD_W, 0)],
            [(WORLD_W, 0), (WORLD_W, WORLD_H)],
            [(WORLD_W, WORLD_H), (0, WORLD_H)],
            [(0, WORLD_H), (0, 0)],
        ]
        for a, b in walls:
            seg = pymunk.Segment(self.space.static_body, a, b, 3)
            seg.friction = 0.8
            seg.elasticity = 0.4
            seg.collision_type = COLLISION_TYPE_WALL
            self.space.add(seg)
    
    def _on_collision(self, arbiter, space, data):
        """Handle any collision."""
        agent_ids = [s.body.agent_id for s in arbiter.shapes if hasattr(s.body, 'agent_id')]
        ctype = 'agent-agent' if len(agent_ids) == 2 else 'agent-object' if len(agent_ids) == 1 else 'other'
        self.collision_log.append({'tick': self.tick, 'type': ctype})
    
    def _create_agent_body(self, agent: SimAgent, x: float, y: float):
        """Create physics body for an agent."""
        mass = 1.0
        radius = 10
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        body.angle = random.uniform(0, 2 * math.pi)
        body.agent_id = agent.id  # Tag for collision detection
        
        shape = pymunk.Circle(body, radius)
        shape.friction = 0.7
        shape.elasticity = 0.3
        shape.collision_type = COLLISION_TYPE_AGENT
        
        self.space.add(body, shape)
        agent.body = body
        agent.shape = shape
    
    def _create_object_body(self, obj_def: dict) -> SimObject:
        """Create physics body for an object."""
        x, y = obj_def['x'], obj_def['y']
        obj_type = obj_def.get('type', 'box')
        movable = obj_def.get('movable', True)
        mass = obj_def.get('mass', 5)
        
        colors = {'box': '#8B4513', 'ramp': '#DAA520', 'food': '#32CD32', 'flag': '#FF4444'}
        
        if movable:
            size = 15 if obj_type == 'ramp' else 12
            moment = pymunk.moment_for_box(mass, (size, size))
            body = pymunk.Body(mass, moment)
            body.position = (x, y)
            shape = pymunk.Poly.create_box(body, (size, size))
            shape.friction = 0.9
            shape.elasticity = 0.2
            shape.collision_type = COLLISION_TYPE_OBJECT
            self.space.add(body, shape)
        else:
            body = self.space.static_body
            if obj_type == 'food':
                shape = pymunk.Circle(body, 5, offset=(x, y))
            else:
                shape = pymunk.Poly.create_box(body, (10, 10), transform=pymunk.Transform.translation(x, y))
            shape.friction = 0.5
            shape.collision_type = COLLISION_TYPE_OBJECT
            self.space.add(shape)
            # Static body - create a wrapper body for position tracking
            wrapper = pymunk.Body(body_type=pymunk.Body.STATIC)
            wrapper.position = (x, y)
            body = wrapper
        
        obj = SimObject(
            id=f'obj-{len(self.objects)}', obj_type=obj_type,
            color=colors.get(obj_type, '#888'), movable=movable,
            body=body, shape=shape, width=15, height=15,
        )
        return obj
    
    def _create_walls(self, wall_defs: list):
        """Create wall segments."""
        self.wall_defs = wall_defs
        for w in wall_defs:
            seg = pymunk.Segment(self.space.static_body, (w['x1'], w['y1']), (w['x2'], w['y2']), 3)
            seg.friction = 0.8
            seg.elasticity = 0.3
            seg.collision_type = COLLISION_TYPE_WALL
            self.space.add(seg)
            self.wall_shapes.append(seg)
    
    def load_environment(self, env_name: str):
        """Load environment with physics."""
        env = ENVIRONMENTS.get(env_name, ENVIRONMENTS['open_field'])
        self.environment = env_name
        self._init_space()
        self._create_walls(env.get('walls', []))
        
        self.objects = []
        for obj_def in env.get('objects', []):
            obj = self._create_object_body(obj_def)
            self.objects.append(obj)
    
    def add_agent(self, agent_id: str, brain_agent: str, name: str,
                  team: str = 'neutral', color: str = '#4ecdc4') -> SimAgent:
        agent = SimAgent(id=agent_id, brain_agent=brain_agent, name=name, team=team, color=color)
        self.agents[agent_id] = agent
        self.episode_rewards[agent_id] = []
        self.cumulative_rewards[agent_id] = 0
        return agent
    
    def remove_agent(self, agent_id: str):
        agent = self.agents.pop(agent_id, None)
        if agent and agent.body and agent.shape and self.space:
            try:
                self.space.remove(agent.body, agent.shape)
            except Exception:
                pass
    
    def start(self, environment: str = 'open_field', max_ticks: int = 1000):
        """Start simulation with real physics."""
        self.load_environment(environment)
        self.max_ticks = max_ticks
        self.tick = 0
        self.episode += 1
        self.events = []
        self.collision_log = []
        self.session_id = f"sim-{int(time.time())}-{uuid.uuid4().hex[:4]}"
        
        # Place agents in physics space
        for agent in self.agents.values():
            x = random.uniform(50, WORLD_W - 50)
            y = random.uniform(50, WORLD_H - 50)
            self._create_agent_body(agent, x, y)
            agent.energy = agent.max_energy
            agent.alive = True
            agent.score = 0
            agent.actions_taken = 0
            self.cumulative_rewards[agent.id] = 0
        
        self.running = True
        self.paused = False
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        return self.session_id
    
    def stop(self):
        self.running = False
    
    def pause(self):
        self.paused = not self.paused
    
    def _run_loop(self):
        """Main loop: get actions → apply forces → step physics → compute rewards."""
        while self.running and self.tick < self.max_ticks:
            if self.paused:
                time.sleep(0.05)
                continue
            
            self.tick += 1
            
            # 1) Update vision (raycasting)
            for agent in self.agents.values():
                if agent.alive:
                    self._update_vision(agent)
            
            # 2) Get and apply actions
            for agent in self.agents.values():
                if agent.alive:
                    action = self._get_action(agent)
                    self._apply_action(agent, action)
            
            # 3) Step physics (multiple sub-steps for stability)
            for _ in range(self.physics_steps):
                self.space.step(PHYSICS_DT)
            
            # 4) Calculate rewards
            self._calculate_rewards()
            
            # 5) Broadcast state
            if self.on_tick:
                self.on_tick(self.get_state())
            
            time.sleep(self.tick_rate)
        
        self.running = False
    
    def _update_vision(self, agent: SimAgent):
        """Raycast-based vision using pymunk segment queries."""
        agent.visible_agents = []
        agent.visible_objects = []
        
        if not agent.body:
            return
        
        pos = agent.body.position
        angle = agent.body.angle
        
        # Check other agents
        for other in self.agents.values():
            if other.id == agent.id or not other.alive or not other.body:
                continue
            opos = other.body.position
            dist = pos.get_distance(opos)
            if dist > agent.vision_range:
                continue
            
            # Check angle
            angle_to = math.atan2(opos.y - pos.y, opos.x - pos.x)
            angle_diff = abs(((angle_to - angle + math.pi) % (2 * math.pi)) - math.pi)
            if angle_diff <= agent.vision_angle / 2:
                # Raycast for line-of-sight
                query = self.space.segment_query_first(pos, opos, 1, pymunk.ShapeFilter())
                if query is None or (hasattr(query.shape.body, 'agent_id') and query.shape.body.agent_id == other.id):
                    agent.visible_agents.append({
                        'id': other.id, 'name': other.name, 'team': other.team,
                        'dist': round(dist, 1), 'angle': round(angle_to, 3),
                    })
        
        # Check objects
        for obj in self.objects:
            if not obj.body:
                continue
            opos = obj.body.position
            dist = pos.get_distance(opos)
            if dist > agent.vision_range:
                continue
            angle_to = math.atan2(opos.y - pos.y, opos.x - pos.x)
            angle_diff = abs(((angle_to - angle + math.pi) % (2 * math.pi)) - math.pi)
            if angle_diff <= agent.vision_angle / 2:
                agent.visible_objects.append({
                    'id': obj.id, 'type': obj.obj_type, 'dist': round(dist, 1),
                    'x': round(opos.x, 1), 'y': round(opos.y, 1),
                })
    
    def _get_action(self, agent: SimAgent) -> int:
        """Get action from brain or built-in AI."""
        if self.brain_callback:
            obs = self._build_observation(agent)
            result = self.brain_callback(agent.brain_agent, obs)
            if isinstance(result, int) and 0 <= result < NUM_ACTIONS:
                return result
            if isinstance(result, str):
                for k, v in ACTIONS.items():
                    if v == result:
                        return k
        
        # Built-in AI
        if agent.team == 'seeker':
            if agent.visible_agents:
                return 5  # sprint toward visible
            return random.choice([1, 3, 4])  # explore
        elif agent.team == 'hider':
            if agent.visible_agents:
                return random.choice([3, 4, 5])  # evade
            return random.choice([1, 0, 3])
        return random.randint(0, NUM_ACTIONS - 1)
    
    def _build_observation(self, agent: SimAgent) -> dict:
        """Build observation vector for RL."""
        pos = agent.body.position if agent.body else (0, 0)
        vel = agent.body.velocity if agent.body else (0, 0)
        return {
            'position': {'x': round(pos.x, 1), 'y': round(pos.y, 1)},
            'velocity': {'x': round(vel.x, 1), 'y': round(vel.y, 1)},
            'angle': round(agent.body.angle if agent.body else 0, 3),
            'energy': round(agent.energy, 1),
            'score': round(agent.score, 2),
            'visible_agents': agent.visible_agents,
            'visible_objects': agent.visible_objects,
            'tick': self.tick,
            'team': agent.team,
        }
    
    def _apply_action(self, agent: SimAgent, action: int):
        """Apply force/torque to agent body."""
        if not agent.body:
            return
        
        energy_costs = {0: 0.01, 1: 0.1, 2: 0.15, 3: 0.05, 4: 0.05, 5: 0.4, 6: 0.2, 7: 0.3, 8: 0.02}
        cost = energy_costs.get(action, 0.1)
        agent.energy = max(0, agent.energy - cost)
        agent.actions_taken += 1
        agent.last_action = ACTIONS.get(action, 'noop')
        
        if agent.energy <= 0:
            agent.alive = False
            return
        
        body = agent.body
        angle = body.angle
        
        if action == 1:  # forward
            fx = math.cos(angle) * agent.speed
            fy = math.sin(angle) * agent.speed
            body.apply_force_at_local_point((fx, fy), (0, 0))
        elif action == 2:  # backward
            fx = -math.cos(angle) * agent.speed * 0.6
            fy = -math.sin(angle) * agent.speed * 0.6
            body.apply_force_at_local_point((fx, fy), (0, 0))
        elif action == 3:  # turn left
            body.angle -= agent.turn_speed * PHYSICS_DT * self.physics_steps
        elif action == 4:  # turn right
            body.angle += agent.turn_speed * PHYSICS_DT * self.physics_steps
        elif action == 5:  # sprint
            fx = math.cos(angle) * agent.speed * 2.5
            fy = math.sin(angle) * agent.speed * 2.5
            body.apply_force_at_local_point((fx, fy), (0, 0))
        elif action == 7:  # push
            push_dir = pymunk.Vec2d(math.cos(angle), math.sin(angle))
            push_end = body.position + push_dir * 30
            query = self.space.segment_query_first(body.position, push_end, 5, pymunk.ShapeFilter())
            if query and query.shape.body.body_type == pymunk.Body.DYNAMIC:
                push_force = push_dir * 500
                query.shape.body.apply_force_at_world_point(push_force, query.point)
                self.events.append({'tick': self.tick, 'agent': agent.id, 'action': 'push'})
        
        # Energy regen
        agent.energy = min(agent.max_energy, agent.energy + 0.03)
    
    def _calculate_rewards(self):
        """Calculate rewards based on game mode."""
        for agent in self.agents.values():
            if not agent.alive:
                continue
            
            reward = 0
            
            if self.environment == 'hide_and_seek':
                if agent.team == 'hider':
                    seen = any(
                        agent.id in [va['id'] for va in other.visible_agents]
                        for other in self.agents.values()
                        if other.team == 'seeker' and other.alive
                    )
                    reward = 0 if seen else 0.1
                elif agent.team == 'seeker':
                    for va in agent.visible_agents:
                        target = self.agents.get(va['id'])
                        if target and target.team == 'hider':
                            reward += 0.5
            
            elif self.environment == 'foraging':
                if agent.body:
                    for obj in self.objects:
                        if obj.obj_type == 'food' and obj.body:
                            dist = agent.body.position.get_distance(obj.body.position)
                            if dist < 20:
                                reward += 1.0
                                # Respawn food
                                obj.body.position = (random.uniform(50, WORLD_W-50), random.uniform(50, WORLD_H-50))
            
            elif self.environment == 'maze':
                # Reward proximity to flag
                for obj in self.objects:
                    if obj.obj_type == 'flag' and agent.body:
                        dist = agent.body.position.get_distance(obj.body.position)
                        reward += max(0, (WORLD_W - dist) / WORLD_W * 0.01)
                        if dist < 25:
                            reward += 10.0  # Found it!
            
            agent.score += reward
            self.cumulative_rewards[agent.id] = agent.score
    
    def get_observation_space_size(self) -> int:
        """Size of flat observation vector for RL."""
        # pos(2) + vel(2) + angle(1) + energy(1) + visible_agents(5*4) + visible_objects(5*3) = 41
        return 41
    
    def get_flat_observation(self, agent: SimAgent) -> np.ndarray:
        """Flat numpy observation for RL training."""
        obs = np.zeros(self.get_observation_space_size(), dtype=np.float32)
        if not agent.body:
            return obs
        
        pos = agent.body.position
        vel = agent.body.velocity
        obs[0] = pos.x / WORLD_W
        obs[1] = pos.y / WORLD_H
        obs[2] = vel.x / 500
        obs[3] = vel.y / 500
        obs[4] = agent.body.angle / (2 * math.pi)
        obs[5] = agent.energy / agent.max_energy
        
        # Visible agents (up to 5)
        for i, va in enumerate(agent.visible_agents[:5]):
            base = 6 + i * 4
            obs[base] = va['dist'] / agent.vision_range
            obs[base + 1] = va['angle'] / (2 * math.pi)
            obs[base + 2] = 1.0 if va['team'] == 'hider' else 0.0
            obs[base + 3] = 1.0 if va['team'] == 'seeker' else 0.0
        
        # Visible objects (up to 5)
        for i, vo in enumerate(agent.visible_objects[:5]):
            base = 26 + i * 3
            obs[base] = vo['dist'] / agent.vision_range
            obs[base + 1] = vo.get('x', 0) / WORLD_W
            obs[base + 2] = vo.get('y', 0) / WORLD_H
        
        return obs
    
    def get_state(self) -> dict:
        """Full state for UI rendering."""
        return {
            'tick': self.tick,
            'episode': self.episode,
            'max_ticks': self.max_ticks,
            'running': self.running,
            'paused': self.paused,
            'environment': self.environment,
            'world': {'width': WORLD_W, 'height': WORLD_H},
            'agents': {aid: a.to_dict() for aid, a in self.agents.items()},
            'walls': self.wall_defs,
            'objects': [o.to_dict() for o in self.objects],
            'events': self.events[-20:],
            'collisions': len(self.collision_log),
            'physics': {
                'engine': 'pymunk (Chipmunk2D)',
                'dt': PHYSICS_DT,
                'substeps': self.physics_steps,
                'damping': self.space.damping if self.space else 0,
            },
        }
    
    def add_wall(self, x1, y1, x2, y2):
        """Add a wall to the current world."""
        self.wall_defs.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
        if self.space:
            self._create_wall_body(x1, y1, x2, y2)
    
    def _create_wall_body(self, x1, y1, x2, y2):
        """Create a pymunk static body for a wall segment."""
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, (x1, y1), (x2, y2), 3)
        shape.friction = 0.8
        shape.elasticity = 0.3
        self.space.add(body, shape)
    
    def add_object(self, x, y, obj_type='box'):
        """Add an object to the current world."""
        colors = {'box': '#8B4513', 'food': '#32CD32', 'flag': '#FF4444', 'ramp': '#DAA520'}
        oid = f'obj-{len(self.objects)}-{int(time.time()) % 10000}'
        movable = obj_type in ('box', 'ramp')
        size = 12 if obj_type != 'food' else 6
        
        obj = SimObject(
            id=oid,
            obj_type=obj_type,
            color=colors.get(obj_type, '#888888'),
            movable=movable,
            width=size,
            height=size,
        )
        
        if self.space and movable:
            mass = 5.0
            body = pymunk.Body(mass, pymunk.moment_for_box(mass, (size, size)))
            body.position = (x, y)
            shape = pymunk.Poly.create_box(body, (size, size))
            shape.friction = 0.7
            shape.elasticity = 0.2
            self.space.add(body, shape)
            obj.body = body
            obj.shape = shape
        elif self.space:
            # Static objects (food, flag) — static body so they show position
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            shape = pymunk.Circle(body, size / 2)
            shape.sensor = True  # Don't collide, just track position
            self.space.add(body, shape)
            obj.body = body
            obj.shape = shape
        else:
            # No space yet — create a simple body for position tracking
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (x, y)
            obj.body = body
        
        self.objects.append(obj)
    
    def remove_nearest(self, x, y, radius=20):
        """Remove the nearest object/wall within radius. Returns what was removed."""
        # Check objects
        best_dist = radius
        best_idx = -1
        for i, obj in enumerate(self.objects):
            pos = obj.body.position if obj.body else (obj.x, obj.y)
            dx, dy = pos[0] - x, pos[1] - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_idx = i
        
        if best_idx >= 0:
            obj = self.objects.pop(best_idx)
            if obj.body and self.space:
                for shape in obj.body.shapes.copy():
                    self.space.remove(shape)
                self.space.remove(obj.body)
            return f'object:{obj.obj_type}'
        
        # Check walls
        best_dist = radius
        best_wall = -1
        for i, w in enumerate(self.wall_defs):
            mx, my = (w['x1']+w['x2'])/2, (w['y1']+w['y2'])/2
            dx, dy = mx - x, my - y
            dist = (dx*dx + dy*dy) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best_wall = i
        
        if best_wall >= 0:
            self.wall_defs.pop(best_wall)
            # Rebuild space walls (simplest approach)
            return 'wall'
        
        return None
    
    def move_object(self, obj_id, new_x, new_y):
        """Move an object to a new position by its ID."""
        for obj in self.objects:
            if obj.id == obj_id:
                if obj.body:
                    obj.body.position = (new_x, new_y)
                    obj.body.velocity = (0, 0)  # Stop any motion
                return True
        return False
    
    def load_world(self, world_data):
        """Load a saved world layout."""
        env = world_data.get('environment', self.environment)
        self.wall_defs = world_data.get('walls', [])
        self.objects = []
        for o in world_data.get('objects', []):
            obj_type = o.get('obj_type') or o.get('type', 'box')
            self.add_object(o['x'], o['y'], obj_type)
        # Rebuild physics walls
        if self.space:
            for w in self.wall_defs:
                self._create_wall_body(w['x1'], w['y1'], w['x2'], w['y2'])
    
    def get_environments(self) -> dict:
        return {k: {'name': v['name'], 'description': v['description']} for k, v in ENVIRONMENTS.items()}
    
    def get_training_stats(self) -> dict:
        """Get RL training statistics."""
        return {
            'episode': self.episode,
            'tick': self.tick,
            'cumulative_rewards': dict(self.cumulative_rewards),
            'collisions': len(self.collision_log),
            'environment': self.environment,
            'agents': {aid: {'score': a.score, 'actions': a.actions_taken, 'alive': a.alive}
                      for aid, a in self.agents.items()},
        }
