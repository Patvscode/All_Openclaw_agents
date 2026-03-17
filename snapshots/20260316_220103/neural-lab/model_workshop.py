"""
Neural Lab — Model Workshop
Inspect, visualize, and modify neural network architectures.

Supports:
- PyTorch models (.pt, .pth, .zip from stable-baselines3)
- Safetensors models (.safetensors)
- Architecture visualization (layer graph)
- Layer inspection (weights, shapes, statistics)
- AI-powered architecture explanation
"""

import json
import os
import math
import numpy as np
from pathlib import Path
from typing import Optional

def inspect_pytorch_model(model_path: str) -> dict:
    """Inspect a PyTorch model file and return architecture details."""
    import torch
    
    result = {
        'path': model_path,
        'format': 'pytorch',
        'size_mb': round(os.path.getsize(model_path) / 1024 / 1024, 2),
        'layers': [],
        'total_params': 0,
        'trainable_params': 0,
        'architecture': '',
    }
    
    try:
        data = torch.load(model_path, map_location='cpu', weights_only=False)
        
        # Handle different formats
        state_dict = None
        if isinstance(data, dict):
            if 'model_state_dict' in data:
                state_dict = data['model_state_dict']
            elif 'state_dict' in data:
                state_dict = data['state_dict']
            elif 'policy' in data:
                # stable-baselines3 format
                result['format'] = 'stable-baselines3'
                if hasattr(data.get('policy'), 'state_dict'):
                    state_dict = data['policy'].state_dict()
            else:
                state_dict = data
        elif hasattr(data, 'state_dict'):
            state_dict = data.state_dict()
        
        if state_dict:
            for name, tensor in state_dict.items():
                if not hasattr(tensor, 'shape'):
                    continue
                shape = list(tensor.shape)
                params = int(np.prod(shape))
                result['total_params'] += params
                
                # Determine layer type from name
                layer_type = 'unknown'
                if 'weight' in name:
                    if len(shape) == 2:
                        layer_type = 'linear'
                    elif len(shape) == 4:
                        layer_type = 'conv2d'
                    elif len(shape) == 1:
                        layer_type = 'norm'
                elif 'bias' in name:
                    layer_type = 'bias'
                elif 'embed' in name:
                    layer_type = 'embedding'
                elif 'norm' in name or 'ln' in name:
                    layer_type = 'norm'
                
                stats = {}
                try:
                    t = tensor.float()
                    stats = {
                        'mean': round(float(t.mean()), 6),
                        'std': round(float(t.std()), 6),
                        'min': round(float(t.min()), 6),
                        'max': round(float(t.max()), 6),
                    }
                except Exception:
                    pass
                
                result['layers'].append({
                    'name': name,
                    'type': layer_type,
                    'shape': shape,
                    'params': params,
                    'dtype': str(tensor.dtype),
                    'stats': stats,
                })
            
            result['trainable_params'] = result['total_params']
    except Exception as e:
        result['error'] = str(e)
    
    return result


def inspect_sb3_model(zip_path: str) -> dict:
    """Inspect a stable-baselines3 model zip."""
    import torch
    import zipfile
    import io
    
    result = {
        'path': zip_path,
        'format': 'stable-baselines3',
        'size_mb': round(os.path.getsize(zip_path) / 1024 / 1024, 2),
        'layers': [],
        'total_params': 0,
        'config': {},
    }
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Read config
            if 'data' in zf.namelist():
                with zf.open('data') as f:
                    config = json.loads(f.read())
                    result['config'] = {
                        'algorithm': config.get('policy_class', ''),
                        'observation_space': str(config.get('observation_space', '')),
                        'action_space': str(config.get('action_space', '')),
                        'learning_rate': config.get('learning_rate', ''),
                        'n_steps': config.get('n_steps', ''),
                    }
            
            # Read policy weights
            if 'policy.pth' in zf.namelist():
                with zf.open('policy.pth') as f:
                    buf = io.BytesIO(f.read())
                    state_dict = torch.load(buf, map_location='cpu', weights_only=False)
                    
                    for name, tensor in state_dict.items():
                        if not hasattr(tensor, 'shape'):
                            continue
                        shape = list(tensor.shape)
                        params = int(np.prod(shape))
                        result['total_params'] += params
                        
                        layer_type = 'linear' if len(shape) == 2 else ('bias' if len(shape) == 1 else 'other')
                        
                        stats = {}
                        try:
                            t = tensor.float()
                            stats = {
                                'mean': round(float(t.mean()), 6),
                                'std': round(float(t.std()), 6),
                                'min': round(float(t.min()), 6),
                                'max': round(float(t.max()), 6),
                            }
                        except Exception:
                            pass
                        
                        result['layers'].append({
                            'name': name,
                            'type': layer_type,
                            'shape': shape,
                            'params': params,
                            'dtype': str(tensor.dtype),
                            'stats': stats,
                        })
    except Exception as e:
        result['error'] = str(e)
    
    return result


def inspect_safetensors(path: str) -> dict:
    """Inspect a safetensors model file."""
    from safetensors import safe_open
    
    result = {
        'path': path,
        'format': 'safetensors',
        'size_mb': round(os.path.getsize(path) / 1024 / 1024, 2),
        'layers': [],
        'total_params': 0,
    }
    
    try:
        with safe_open(path, framework="pt", device="cpu") as f:
            for key in f.keys():
                tensor = f.get_tensor(key)
                shape = list(tensor.shape)
                params = int(np.prod(shape))
                result['total_params'] += params
                
                layer_type = 'unknown'
                if 'weight' in key and len(shape) == 2:
                    layer_type = 'linear'
                elif 'weight' in key and len(shape) == 4:
                    layer_type = 'conv2d'
                elif 'embed' in key:
                    layer_type = 'embedding'
                elif 'norm' in key or 'ln' in key:
                    layer_type = 'norm'
                elif 'bias' in key:
                    layer_type = 'bias'
                
                stats = {}
                try:
                    t = tensor.float()
                    stats = {
                        'mean': round(float(t.mean()), 6),
                        'std': round(float(t.std()), 6),
                        'min': round(float(t.min()), 6),
                        'max': round(float(t.max()), 6),
                    }
                except Exception:
                    pass
                
                result['layers'].append({
                    'name': key,
                    'type': layer_type,
                    'shape': shape,
                    'params': params,
                    'dtype': str(tensor.dtype),
                    'stats': stats,
                })
    except Exception as e:
        result['error'] = str(e)
    
    return result


def inspect_model(path: str) -> dict:
    """Auto-detect format and inspect model."""
    path = str(path)
    if path.endswith('.safetensors'):
        return inspect_safetensors(path)
    elif path.endswith('.zip'):
        return inspect_sb3_model(path)
    elif path.endswith('.pt') or path.endswith('.pth'):
        return inspect_pytorch_model(path)
    else:
        return {'error': f'Unknown format: {path}'}


def scan_models(directories: list[str] = None) -> list[dict]:
    """Scan directories for model files."""
    if directories is None:
        directories = [
            str(Path.home() / 'models' / 'workshop'),
            str(Path.home() / '.openclaw' / 'neural-lab' / 'rl-models'),
        ]
    
    models = []
    extensions = {'.safetensors', '.pt', '.pth', '.zip', '.gguf'}
    
    for d in directories:
        p = Path(d)
        if not p.exists():
            continue
        for f in p.rglob('*'):
            if f.suffix in extensions and f.stat().st_size > 0:
                # Use parent dir name as display name for generic filenames
                display_name = f.name
                if f.name in ('model.safetensors', 'pytorch_model.bin'):
                    display_name = f.parent.name
                # Read config.json for architecture type
                arch = ''
                config_file = f.parent / 'config.json'
                if config_file.exists():
                    try:
                        import json as _json
                        cfg = _json.loads(config_file.read_text())
                        arch = cfg.get('model_type', cfg.get('architectures', [''])[0] if cfg.get('architectures') else '')
                    except Exception:
                        pass
                
                models.append({
                    'name': display_name,
                    'path': str(f),
                    'format': f.suffix[1:],
                    'size_mb': round(f.stat().st_size / 1024 / 1024, 1),
                    'directory': str(f.parent),
                    'architecture': arch,
                })
    
    return sorted(models, key=lambda x: x['name'])


def duplicate_model(src_path: str, new_name: str = '') -> dict:
    """Create a working copy of a model for safe experimentation."""
    src = Path(src_path)
    if not src.exists():
        return {'error': 'source not found'}
    
    workshop_dir = Path.home() / 'models' / 'workshop'
    
    # Determine source directory (for safetensors with config)
    src_dir = src.parent
    base_name = src_dir.name if src.name == 'model.safetensors' else src.stem
    
    if not new_name:
        new_name = f"{base_name}-experiment-{int(time.time()) % 100000}"
    
    dest_dir = workshop_dir / new_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    import shutil
    copied = []
    # Copy all relevant files from source directory
    for ext in ['*.safetensors', '*.json', '*.txt', '*.zip']:
        for f in src_dir.glob(ext):
            dest_file = dest_dir / f.name
            shutil.copy2(str(f), str(dest_file))
            copied.append(f.name)
    
    return {
        'ok': True,
        'name': new_name,
        'path': str(dest_dir),
        'files': copied,
        'model_path': str(dest_dir / 'model.safetensors') if (dest_dir / 'model.safetensors').exists() else str(list(dest_dir.glob('*.safetensors'))[0]) if list(dest_dir.glob('*.safetensors')) else '',
    }


def save_modified_model(state_dict: dict, dest_path: str, metadata: dict = None) -> dict:
    """Save a modified state dict as safetensors."""
    from safetensors.torch import save_file
    
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure all tensors are contiguous
    clean = {k: v.clone().contiguous() for k, v in state_dict.items()}
    save_file(clean, str(dest), metadata=metadata)
    
    return {
        'ok': True,
        'path': str(dest),
        'size_mb': round(dest.stat().st_size / 1024 / 1024, 2),
        'layers': len(clean),
    }


import time

def generate_architecture_explanation(model_info: dict, ai_model: str = 'qwen3.5:2b') -> str:
    """Use a local LLM to explain the model architecture."""
    import requests
    
    layers_summary = "\n".join(
        f"  {l['name']}: {l['type']} {l['shape']} ({l['params']} params)"
        for l in model_info['layers'][:20]
    )
    
    prompt = f"""Explain this neural network architecture in plain language:

Format: {model_info['format']}
Total parameters: {model_info['total_params']:,}
Layers:
{layers_summary}

Explain:
1. What kind of network this is
2. What each major layer group does
3. Input/output dimensions
4. What this network might be designed for

Be concise (3-4 sentences)."""
    
    try:
        resp = requests.post('http://localhost:11434/api/generate', json={
            'model': ai_model,
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.3, 'num_predict': 200},
        }, timeout=30)
        data = resp.json()
        return data.get('response', 'Could not generate explanation')
    except Exception as e:
        return f'AI explanation unavailable: {e}'
