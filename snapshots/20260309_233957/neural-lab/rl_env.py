"""
Neural Lab — Gymnasium RL Environment
Wraps the pymunk simulation as a proper Gymnasium env for training with stable-baselines3.

Usage:
    from rl_env import NeuralLabEnv
    env = NeuralLabEnv(environment='hide_and_seek', num_agents=4)
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=50000)
"""

import math
import random
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from simulation import SimulationEngine, ACTIONS, NUM_ACTIONS, WORLD_W, WORLD_H

class NeuralLabEnv(gym.Env):
    """Single-agent Gymnasium environment wrapping the pymunk simulation."""
    
    metadata = {"render_modes": ["human", "rgb_array"]}
    
    def __init__(self, environment='hide_and_seek', num_agents=4, 
                 controlled_team='seeker', max_steps=500, render_mode=None):
        super().__init__()
        
        self.sim = SimulationEngine()
        self.environment = environment
        self.num_agents = num_agents
        self.controlled_team = controlled_team
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.step_count = 0
        
        # Observation: 41-dim vector (see simulation.py get_flat_observation)
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0,
            shape=(self.sim.get_observation_space_size(),),
            dtype=np.float32
        )
        
        # Action: discrete
        self.action_space = spaces.Discrete(NUM_ACTIONS)
        
        self._controlled_agent_id = None
        self._setup_agents()
    
    def _setup_agents(self):
        """Create agents for the environment."""
        self.sim.agents.clear()
        
        teams = ['hider', 'seeker'] if self.environment == 'hide_and_seek' else ['neutral']
        colors = {'hider': '#4ecdc4', 'seeker': '#ff6b6b', 'neutral': '#ffd93d'}
        
        for i in range(self.num_agents):
            if self.environment == 'hide_and_seek':
                team = 'hider' if i < self.num_agents // 2 else 'seeker'
            else:
                team = 'neutral'
            
            aid = f'rl-{i}'
            self.sim.add_agent(aid, aid, f'Agent-{i}', team=team, color=colors.get(team, '#888'))
            
            if team == self.controlled_team and self._controlled_agent_id is None:
                self._controlled_agent_id = aid
        
        # If no controlled team found, control first agent
        if self._controlled_agent_id is None:
            self._controlled_agent_id = list(self.sim.agents.keys())[0]
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        self.step_count = 0
        self.sim.load_environment(self.environment)
        
        # Place agents
        for agent in self.sim.agents.values():
            x = random.uniform(50, WORLD_W - 50)
            y = random.uniform(50, WORLD_H - 50)
            self.sim._create_agent_body(agent, x, y)
            agent.energy = agent.max_energy
            agent.alive = True
            agent.score = 0
            agent.actions_taken = 0
        
        self.sim.tick = 0
        self.sim.collision_log = []
        self.sim.events = []
        
        controlled = self.sim.agents[self._controlled_agent_id]
        obs = self.sim.get_flat_observation(controlled)
        return obs, {}
    
    def step(self, action):
        self.step_count += 1
        self.sim.tick += 1
        
        controlled = self.sim.agents[self._controlled_agent_id]
        prev_score = controlled.score
        
        # Update vision for all
        for agent in self.sim.agents.values():
            if agent.alive:
                self.sim._update_vision(agent)
        
        # Apply controlled agent's action
        self.sim._apply_action(controlled, int(action))
        
        # Other agents use built-in AI
        for agent in self.sim.agents.values():
            if agent.id != self._controlled_agent_id and agent.alive:
                ai_action = self.sim._get_action(agent)
                self.sim._apply_action(agent, ai_action)
        
        # Step physics
        for _ in range(self.sim.physics_steps):
            self.sim.space.step(1/60)
        
        # Calculate rewards
        self.sim._calculate_rewards()
        
        # Get observation
        obs = self.sim.get_flat_observation(controlled)
        reward = controlled.score - prev_score
        
        # Termination conditions
        terminated = not controlled.alive
        truncated = self.step_count >= self.max_steps
        
        info = {
            'score': controlled.score,
            'energy': controlled.energy,
            'step': self.step_count,
            'collisions': len(self.sim.collision_log),
        }
        
        return obs, reward, terminated, truncated, info
    
    def get_state_for_render(self):
        """Get state dict for 3D rendering in the UI."""
        return self.sim.get_state()


class MultiAgentNeuralLabEnv:
    """PettingZoo-style multi-agent environment for future use."""
    
    def __init__(self, environment='hide_and_seek', num_agents=4, max_steps=500):
        self.sim = SimulationEngine()
        self.environment = environment
        self.num_agents = num_agents
        self.max_steps = max_steps
        self.agents_list = []
        
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0,
            shape=(self.sim.get_observation_space_size(),),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(NUM_ACTIONS)
        self._setup()
    
    def _setup(self):
        self.sim.agents.clear()
        teams = {'hider': '#4ecdc4', 'seeker': '#ff6b6b'}
        for i in range(self.num_agents):
            team = 'hider' if i < self.num_agents // 2 else 'seeker'
            aid = f'rl-{i}'
            self.sim.add_agent(aid, aid, f'Agent-{i}', team=team, color=teams.get(team, '#888'))
            self.agents_list.append(aid)
    
    def reset(self):
        self.sim.load_environment(self.environment)
        for agent in self.sim.agents.values():
            x = random.uniform(50, WORLD_W - 50)
            y = random.uniform(50, WORLD_H - 50)
            self.sim._create_agent_body(agent, x, y)
            agent.energy = agent.max_energy
            agent.alive = True
            agent.score = 0
        self.sim.tick = 0
        return {aid: self.sim.get_flat_observation(self.sim.agents[aid]) for aid in self.agents_list}
    
    def step(self, actions: dict):
        """actions: {agent_id: action_int}"""
        self.sim.tick += 1
        
        for agent in self.sim.agents.values():
            if agent.alive:
                self.sim._update_vision(agent)
        
        prev_scores = {aid: self.sim.agents[aid].score for aid in self.agents_list}
        
        for aid, action in actions.items():
            if aid in self.sim.agents and self.sim.agents[aid].alive:
                self.sim._apply_action(self.sim.agents[aid], int(action))
        
        for _ in range(self.sim.physics_steps):
            self.sim.space.step(1/60)
        
        self.sim._calculate_rewards()
        
        obs = {}
        rewards = {}
        dones = {}
        for aid in self.agents_list:
            agent = self.sim.agents[aid]
            obs[aid] = self.sim.get_flat_observation(agent)
            rewards[aid] = agent.score - prev_scores[aid]
            dones[aid] = not agent.alive or self.sim.tick >= self.max_steps
        
        return obs, rewards, dones, {}
