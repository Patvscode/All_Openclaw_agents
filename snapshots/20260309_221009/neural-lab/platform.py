"""
Neural Lab Platform — Extensible simulation & AI research framework.

Architecture:
  Platform
  ├── Registry (plugins, assets, pipelines, environments, sensors)
  ├── Pipeline Engine (chainable processing stages)
  ├── Asset Library (objects, prefabs, materials, textures)
  ├── Extension System (load/unload at runtime)
  └── Config Manager (YAML/JSON workspace configs)

Everything is a plugin. Brain regions, sim environments, sensors,
training algorithms, world generators — all register through the same API.
"""

import json
import time
import uuid
import importlib
import importlib.util
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum


# ═══════════════════════════════════════════
# ─── REGISTRY ───
# ═══════════════════════════════════════════

class PluginType(Enum):
    ENVIRONMENT = "environment"
    SENSOR = "sensor"
    AGENT_BEHAVIOR = "agent_behavior"
    PIPELINE = "pipeline"
    ASSET = "asset"
    WORLD_GENERATOR = "world_generator"
    TRAINING_ALGO = "training_algo"
    REWARD_FUNCTION = "reward_function"
    PHYSICS_MATERIAL = "physics_material"
    OBJECT_PREFAB = "object_prefab"
    BRAIN_REGION = "brain_region"
    EXPORTER = "exporter"


@dataclass
class PluginEntry:
    id: str
    name: str
    type: PluginType
    version: str = "1.0.0"
    author: str = "neural-lab"
    description: str = ""
    config_schema: dict = field(default_factory=dict)
    factory: Callable = None  # Creates an instance
    module_path: str = ""     # For file-based plugins
    enabled: bool = True
    tags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'type': self.type.value,
            'version': self.version, 'author': self.author,
            'description': self.description, 'enabled': self.enabled,
            'tags': self.tags, 'config_schema': self.config_schema,
            'metadata': self.metadata,
        }


class Registry:
    """Central registry for all platform components."""
    
    def __init__(self):
        self._plugins: dict[str, PluginEntry] = {}
        self._hooks: dict[str, list[Callable]] = {}
    
    def register(self, entry: PluginEntry) -> str:
        self._plugins[entry.id] = entry
        self._fire('on_register', entry)
        return entry.id
    
    def unregister(self, plugin_id: str):
        if plugin_id in self._plugins:
            entry = self._plugins.pop(plugin_id)
            self._fire('on_unregister', entry)
    
    def get(self, plugin_id: str) -> Optional[PluginEntry]:
        return self._plugins.get(plugin_id)
    
    def find(self, plugin_type: PluginType = None, tags: list = None, enabled_only: bool = True) -> list[PluginEntry]:
        results = list(self._plugins.values())
        if plugin_type:
            results = [p for p in results if p.type == plugin_type]
        if tags:
            results = [p for p in results if any(t in p.tags for t in tags)]
        if enabled_only:
            results = [p for p in results if p.enabled]
        return results
    
    def create(self, plugin_id: str, config: dict = None) -> Any:
        """Create an instance from a registered plugin."""
        entry = self._plugins.get(plugin_id)
        if not entry or not entry.factory:
            raise ValueError(f"Plugin {plugin_id} not found or has no factory")
        return entry.factory(config or {})
    
    def hook(self, event: str, callback: Callable):
        self._hooks.setdefault(event, []).append(callback)
    
    def _fire(self, event: str, *args):
        for cb in self._hooks.get(event, []):
            try:
                cb(*args)
            except Exception:
                pass
    
    def to_dict(self):
        return {
            'plugins': {pid: p.to_dict() for pid, p in self._plugins.items()},
            'count': len(self._plugins),
            'by_type': {t.value: len(self.find(t)) for t in PluginType},
        }


# ═══════════════════════════════════════════
# ─── PIPELINE ENGINE ───
# ═══════════════════════════════════════════

@dataclass
class PipelineStage:
    name: str
    fn: Callable  # (input_data, config) -> output_data
    config: dict = field(default_factory=dict)
    description: str = ""


class Pipeline:
    """Chainable processing pipeline. Stages run sequentially, each receiving the previous output."""
    
    def __init__(self, name: str, description: str = ""):
        self.id = f"pipeline-{uuid.uuid4().hex[:8]}"
        self.name = name
        self.description = description
        self.stages: list[PipelineStage] = []
        self.history: list[dict] = []
    
    def add_stage(self, name: str, fn: Callable, config: dict = None, description: str = ""):
        self.stages.append(PipelineStage(name=name, fn=fn, config=config or {}, description=description))
        return self
    
    def run(self, input_data: Any = None) -> dict:
        """Run the full pipeline."""
        data = input_data
        results = []
        start = time.time()
        
        for i, stage in enumerate(self.stages):
            stage_start = time.time()
            try:
                data = stage.fn(data, stage.config)
                results.append({
                    'stage': stage.name,
                    'status': 'ok',
                    'duration_ms': round((time.time() - stage_start) * 1000),
                })
            except Exception as e:
                results.append({
                    'stage': stage.name,
                    'status': 'error',
                    'error': str(e),
                    'duration_ms': round((time.time() - stage_start) * 1000),
                })
                break
        
        run_result = {
            'pipeline': self.name,
            'stages': results,
            'total_ms': round((time.time() - start) * 1000),
            'output': data if not isinstance(data, (bytes, bytearray)) else f'<binary {len(data)} bytes>',
        }
        self.history.append(run_result)
        return run_result
    
    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'description': self.description,
            'stages': [{'name': s.name, 'description': s.description, 'config': s.config} for s in self.stages],
            'runs': len(self.history),
        }


# ═══════════════════════════════════════════
# ─── ASSET LIBRARY ───
# ═══════════════════════════════════════════

@dataclass
class Asset:
    id: str
    name: str
    category: str  # object, material, texture, prefab, environment
    properties: dict = field(default_factory=dict)
    thumbnail: str = ""
    tags: list = field(default_factory=list)
    
    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'category': self.category,
            'properties': self.properties, 'thumbnail': self.thumbnail,
            'tags': self.tags,
        }


class AssetLibrary:
    """Manages reusable objects, materials, prefabs."""
    
    def __init__(self, storage_dir: str = None):
        self.storage_dir = Path(storage_dir or Path.home() / '.openclaw' / 'neural-lab' / 'assets')
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._assets: dict[str, Asset] = {}
        self._load_builtin()
    
    def _load_builtin(self):
        """Register built-in assets."""
        # Object prefabs
        prefabs = [
            ("wall-short", "Short Wall", {"width": 60, "height": 40, "thickness": 4, "color": "#8888aa", "physics": "static"}),
            ("wall-long", "Long Wall", {"width": 120, "height": 40, "thickness": 4, "color": "#8888aa", "physics": "static"}),
            ("wall-L", "L-Shaped Wall", {"segments": [{"x1": 0, "y1": 0, "x2": 60, "y2": 0}, {"x1": 60, "y1": 0, "x2": 60, "y2": 60}], "color": "#8888aa"}),
            ("box-small", "Small Box", {"width": 10, "height": 10, "color": "#8B4513", "mass": 3, "physics": "dynamic"}),
            ("box-large", "Large Box", {"width": 25, "height": 25, "color": "#654321", "mass": 10, "physics": "dynamic"}),
            ("box-heavy", "Heavy Box", {"width": 20, "height": 20, "color": "#444444", "mass": 50, "physics": "dynamic"}),
            ("ramp-small", "Small Ramp", {"width": 20, "height": 10, "color": "#DAA520", "physics": "dynamic"}),
            ("food-apple", "Apple", {"radius": 5, "color": "#ff4444", "energy": 10, "physics": "sensor"}),
            ("food-berry", "Berry", {"radius": 3, "color": "#8844ff", "energy": 5, "physics": "sensor"}),
            ("food-mushroom", "Mushroom", {"radius": 4, "color": "#ff8800", "energy": 15, "physics": "sensor"}),
            ("flag-red", "Red Flag", {"color": "#ff4444", "height": 25, "physics": "static"}),
            ("flag-blue", "Blue Flag", {"color": "#4444ff", "height": 25, "physics": "static"}),
            ("flag-green", "Green Flag", {"color": "#44ff44", "height": 25, "physics": "static"}),
            ("beacon", "Beacon", {"radius": 8, "color": "#ffdd00", "emissive": True, "pulse": True, "physics": "static"}),
            ("portal-in", "Portal Entry", {"radius": 10, "color": "#00ffff", "linked_to": "", "physics": "sensor"}),
            ("portal-out", "Portal Exit", {"radius": 10, "color": "#ff00ff", "linked_to": "", "physics": "sensor"}),
            ("trap-spike", "Spike Trap", {"width": 15, "height": 2, "damage": 20, "color": "#cc0000", "physics": "sensor"}),
            ("shelter", "Shelter", {"width": 40, "height": 30, "color": "#336633", "roof": True, "physics": "static"}),
            ("water", "Water Zone", {"width": 50, "height": 50, "color": "#2266aa", "slow_factor": 0.5, "physics": "sensor"}),
            ("mud", "Mud Zone", {"width": 40, "height": 40, "color": "#664422", "slow_factor": 0.3, "physics": "sensor"}),
        ]
        
        for pid, name, props in prefabs:
            self._assets[pid] = Asset(
                id=pid, name=name, category='prefab',
                properties=props, tags=['builtin'],
            )
        
        # Materials
        materials = [
            ("mat-concrete", "Concrete", {"friction": 0.8, "elasticity": 0.1, "color": "#888888"}),
            ("mat-ice", "Ice", {"friction": 0.05, "elasticity": 0.2, "color": "#aaddff"}),
            ("mat-rubber", "Rubber", {"friction": 0.95, "elasticity": 0.8, "color": "#333333"}),
            ("mat-wood", "Wood", {"friction": 0.6, "elasticity": 0.3, "color": "#8B6914"}),
            ("mat-metal", "Metal", {"friction": 0.4, "elasticity": 0.5, "color": "#aaaacc"}),
            ("mat-sand", "Sand", {"friction": 0.9, "elasticity": 0.0, "color": "#ddc88a"}),
        ]
        
        for mid, name, props in materials:
            self._assets[mid] = Asset(
                id=mid, name=name, category='material',
                properties=props, tags=['builtin'],
            )
        
        # Environment templates
        templates = [
            ("env-arena", "Empty Arena", {"width": 600, "height": 400, "walls": [], "objects": []}),
            ("env-maze-simple", "Simple Maze", {"width": 600, "height": 400, "walls": [
                {"x1":100,"y1":0,"x2":100,"y2":280},{"x1":200,"y1":120,"x2":200,"y2":400},
                {"x1":300,"y1":0,"x2":300,"y2":280},{"x1":400,"y1":120,"x2":400,"y2":400},
            ], "objects": [{"x":550,"y":350,"type":"flag"}]}),
            ("env-capture-flag", "Capture the Flag", {"width": 600, "height": 400, "walls": [
                {"x1":300,"y1":50,"x2":300,"y2":350},
            ], "objects": [
                {"x":50,"y":200,"type":"flag","color":"#4444ff"},
                {"x":550,"y":200,"type":"flag","color":"#ff4444"},
            ]}),
            ("env-obstacle-course", "Obstacle Course", {"width": 800, "height": 400, "walls": [
                {"x1":150,"y1":100,"x2":150,"y2":300},{"x1":300,"y1":0,"x2":300,"y2":200},
                {"x1":450,"y1":200,"x2":450,"y2":400},{"x1":600,"y1":0,"x2":600,"y2":300},
            ], "objects": [
                {"x":100,"y":50,"type":"food"},{"x":250,"y":350,"type":"food"},
                {"x":375,"y":100,"type":"food"},{"x":525,"y":350,"type":"food"},
                {"x":750,"y":200,"type":"flag"},
            ]}),
            ("env-foraging-dense", "Dense Foraging", {"width": 600, "height": 400, "objects": [
                {"x": 50+i*50, "y": 50+j*50, "type": "food"}
                for i in range(11) for j in range(7)
            ], "walls": []}),
        ]
        
        for tid, name, props in templates:
            self._assets[tid] = Asset(
                id=tid, name=name, category='environment',
                properties=props, tags=['builtin', 'template'],
            )
    
    def add(self, asset: Asset):
        self._assets[asset.id] = asset
        # Persist custom assets
        if 'builtin' not in asset.tags:
            path = self.storage_dir / f'{asset.id}.json'
            path.write_text(json.dumps(asset.to_dict(), indent=2))
    
    def get(self, asset_id: str) -> Optional[Asset]:
        return self._assets.get(asset_id)
    
    def find(self, category: str = None, tags: list = None, search: str = None) -> list[Asset]:
        results = list(self._assets.values())
        if category:
            results = [a for a in results if a.category == category]
        if tags:
            results = [a for a in results if any(t in a.tags for t in tags)]
        if search:
            s = search.lower()
            results = [a for a in results if s in a.name.lower() or s in a.id]
        return sorted(results, key=lambda a: a.name)
    
    def to_dict(self):
        by_cat = {}
        for a in self._assets.values():
            by_cat.setdefault(a.category, []).append(a.to_dict())
        return {'assets': by_cat, 'count': len(self._assets)}


# ═══════════════════════════════════════════
# ─── EXTENSION LOADER ───
# ═══════════════════════════════════════════

class ExtensionLoader:
    """Loads .py extensions from a directory at runtime."""
    
    def __init__(self, registry: Registry, extensions_dir: str = None):
        self.registry = registry
        self.extensions_dir = Path(extensions_dir or Path.home() / '.openclaw' / 'neural-lab' / 'extensions')
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        self._loaded: dict[str, Any] = {}
    
    def scan(self) -> list[dict]:
        """Scan for available extensions."""
        found = []
        for f in self.extensions_dir.glob('*.py'):
            found.append({
                'file': f.name,
                'name': f.stem,
                'loaded': f.stem in self._loaded,
                'size_kb': round(f.stat().st_size / 1024, 1),
            })
        return found
    
    def load(self, name: str) -> dict:
        """Load an extension by filename (without .py)."""
        path = self.extensions_dir / f'{name}.py'
        if not path.exists():
            return {'error': f'Extension not found: {name}'}
        
        try:
            spec = importlib.util.spec_from_file_location(f'neural_lab_ext_{name}', str(path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            # Extension must have a register(registry) function
            if hasattr(mod, 'register'):
                mod.register(self.registry)
            
            self._loaded[name] = mod
            return {'ok': True, 'name': name}
        except Exception as e:
            return {'error': str(e)}
    
    def unload(self, name: str) -> dict:
        if name in self._loaded:
            mod = self._loaded.pop(name)
            if hasattr(mod, 'unregister'):
                mod.unregister(self.registry)
            return {'ok': True}
        return {'error': 'not loaded'}


# ═══════════════════════════════════════════
# ─── REWARD FUNCTIONS ───
# ═══════════════════════════════════════════

def reward_foraging(agent, env_state) -> float:
    """Reward for collecting food."""
    return agent.score  # Score increases when food collected

def reward_exploration(agent, env_state) -> float:
    """Reward for visiting new cells."""
    visited = getattr(agent, '_visited_cells', set())
    cell = (int(agent.body.position.x / 50), int(agent.body.position.y / 50))
    if cell not in visited:
        visited.add(cell)
        agent._visited_cells = visited
        return 1.0
    return -0.01  # Small penalty for staying in explored areas

def reward_survival(agent, env_state) -> float:
    """Reward for staying alive with energy."""
    return 0.1 if agent.alive and agent.energy > 20 else -0.5

def reward_team_score(agent, env_state) -> float:
    """Reward based on team performance."""
    team_scores = {}
    for a in env_state.get('agents', {}).values():
        team_scores.setdefault(a.get('team', 'none'), 0)
        team_scores[a.get('team', 'none')] += a.get('score', 0)
    return team_scores.get(agent.team, 0) / max(1, len([a for a in env_state.get('agents', {}).values() if a.get('team') == agent.team]))


# ═══════════════════════════════════════════
# ─── PLATFORM ───
# ═══════════════════════════════════════════

class NeuralLabPlatform:
    """The central platform instance. Manages registry, assets, pipelines, extensions."""
    
    def __init__(self):
        self.registry = Registry()
        self.assets = AssetLibrary()
        self.extensions = ExtensionLoader(self.registry)
        self.pipelines: dict[str, Pipeline] = {}
        self._register_builtins()
    
    def _register_builtins(self):
        """Register all built-in plugins."""
        # Training algorithms
        for algo_id, name, desc in [
            ('ppo', 'PPO', 'Proximal Policy Optimization — stable, general-purpose'),
            ('a2c', 'A2C', 'Advantage Actor-Critic — fast, good for simple tasks'),
            ('dqn', 'DQN', 'Deep Q-Network — discrete actions, value-based'),
        ]:
            self.registry.register(PluginEntry(
                id=f'algo-{algo_id}', name=name, type=PluginType.TRAINING_ALGO,
                description=desc, tags=['builtin', 'rl'],
                config_schema={'learning_rate': 3e-4, 'n_steps': 2048, 'batch_size': 64},
            ))
        
        # Reward functions
        for rid, name, fn, desc in [
            ('foraging', 'Foraging Reward', reward_foraging, 'Score from food collection'),
            ('exploration', 'Exploration Reward', reward_exploration, 'Reward new cells visited'),
            ('survival', 'Survival Reward', reward_survival, 'Stay alive with energy'),
            ('team-score', 'Team Score', reward_team_score, 'Team-averaged performance'),
        ]:
            self.registry.register(PluginEntry(
                id=f'reward-{rid}', name=name, type=PluginType.REWARD_FUNCTION,
                description=desc, factory=lambda cfg, f=fn: f, tags=['builtin'],
            ))
        
        # Sensors
        for sid, name, desc, schema in [
            ('vision-cone', 'Vision Cone', 'Raycast vision with configurable FOV and range',
             {'fov': 120, 'range': 150, 'rays': 5}),
            ('proximity', 'Proximity Sensor', 'Detect nearby agents/objects within radius',
             {'radius': 50}),
            ('audio', 'Audio Sensor', 'Detect sounds/communications from other agents',
             {'range': 200}),
            ('compass', 'Compass', 'Provides heading to a target',
             {'target': 'nearest_food'}),
            ('energy-meter', 'Energy Meter', 'Reports own energy level',
             {}),
        ]:
            self.registry.register(PluginEntry(
                id=f'sensor-{sid}', name=name, type=PluginType.SENSOR,
                description=desc, config_schema=schema, tags=['builtin'],
            ))
        
        # Physics materials (from asset library)
        for asset in self.assets.find(category='material'):
            self.registry.register(PluginEntry(
                id=f'material-{asset.id}', name=asset.name,
                type=PluginType.PHYSICS_MATERIAL,
                description=f'Friction: {asset.properties.get("friction")}, Elasticity: {asset.properties.get("elasticity")}',
                metadata=asset.properties, tags=['builtin', 'material'],
            ))
        
        # Object prefabs (from asset library)
        for asset in self.assets.find(category='prefab'):
            self.registry.register(PluginEntry(
                id=f'prefab-{asset.id}', name=asset.name,
                type=PluginType.OBJECT_PREFAB,
                metadata=asset.properties, tags=['builtin', 'prefab'],
            ))
    
    def create_pipeline(self, name: str, description: str = "") -> Pipeline:
        p = Pipeline(name, description)
        self.pipelines[p.id] = p
        return p
    
    def to_dict(self):
        return {
            'registry': self.registry.to_dict(),
            'assets': self.assets.to_dict(),
            'pipelines': {pid: p.to_dict() for pid, p in self.pipelines.items()},
            'extensions': self.extensions.scan(),
        }


# Singleton
platform = NeuralLabPlatform()
