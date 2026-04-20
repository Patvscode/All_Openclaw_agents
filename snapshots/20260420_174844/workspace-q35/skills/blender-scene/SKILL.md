# Blender Scene Creator Skill

Create 3D scenes in Blender using Python scripts. Renders images from procedurally generated scenes.

## Overview

This skill uses Blender's Python API to create 3D scenes programmatically and render them as images. Great for generating landscapes, architectural visualizations, product renders, and more.

## Prerequisites

- Blender 4.0+ installed (`which blender`)
- Python 3.10+ (bundled with Blender)

## Usage

### Quick Commands

```bash
# Create a mountain scene
blender-scene mountain --output ~/mountains.png

# Create a forest scene
blender-scene forest --trees 50 --output ~/forest.png

# Create a city scene
blender-scene city --buildings 100 --output ~/city.png
```

### Full Command Reference

```bash
blender-scene <scene_type> [options]

Scene Types:
  mountain    - Mountain landscape with atmospheric perspective
  forest      - Dense forest with varied trees and terrain
  city        - Urban skyline with buildings
  desert      - Desert landscape with dunes and rocks
  island      - Tropical island with beach and ocean
```

### Options

```bash
--output <path>       Output image path (default: ~/scene.png)
--width <px>          Image width (default: 1920)
--height <px>         Image height (default: 1080)
--engine <engine>     Render engine: EEVEE or CYCLES (default: EEVEE)
--samples <n>         Render samples for CYCLES (default: 128)
--seed <n>            Random seed for reproducibility (default: 42)
```

## Examples

### Mountain Scene
```bash
blender-scene mountain \
  --output ~/mountains.png \
  --width 3840 \
  --height 2160 \
  --seed 123
```

### Forest with Many Trees
```bash
blender-scene forest \
  --trees 100 \
  --output ~/dense_forest.png \
  --engine CYCLES \
  --samples 256
```

### City Skyline
```bash
blender-scene city \
  --buildings 200 \
  --output ~/skyline.png \
  --width 1920 \
  --height 1080
```

## Scene Customization

Each scene type has specific parameters:

### Mountain Scene
- Multiple mountain layers (foreground, mid-ground, background)
- Atmospheric perspective (lighter colors = farther away)
- Optional snow caps on tallest peaks
- Random tree placement in foreground

### Forest Scene
- Varied tree types (conifers, deciduous)
- Terrain displacement for natural ground
- Dense foliage with multiple layers
- Sunlight filtering through canopy

### City Scene
- Random building heights and widths
- Window patterns on facades
- Street-level perspective option
- Day/night lighting presets

## Under the Hood

### Blender Python API

The tool uses Blender's `bpy` module to:
1. Clear the default scene
2. Add geometric primitives (cones, cylinders, cubes, spheres)
3. Apply materials with node-based shaders
4. Add modifiers (displacement, subdivision)
5. Set up cameras and lighting
6. Configure render settings
7. Execute render in background mode

### Render Engines

**EEVEE** (default):
- Fast real-time rendering
- Good for quick iterations
- Lower quality but instant results

**CYCLES**:
- Ray-traced rendering
- Higher quality with realistic lighting
- Slower (adjust `--samples` for quality/speed tradeoff)

## File Structure

```
~/.openclaw/skills/blender-scene/
├── SKILL.md              # This file
├── scripts/
│   ├── blender-scene     # Main CLI tool
│   ├── mountain.py       # Mountain scene generator
│   ├── forest.py         # Forest scene generator
│   ├── city.py           # City scene generator
│   └── desert.py         # Desert scene generator
└── examples/
    ├── mountain_sample.png
    ├── forest_sample.png
    └── city_sample.png
```

## Troubleshooting

### "Blender not found"
```bash
# Install Blender
sudo apt install blender

# Verify installation
blender --version
```

### Render fails silently
```bash
# Run in verbose mode
blender-scene mountain --output ~/test.png --verbose

# Check Blender logs
blender --background --factory-startup --python script.py 2>&1 | tee blender.log
```

### Out of memory
```bash
# Reduce render resolution
blender-scene mountain --width 1280 --height 720

# Reduce samples (for CYCLES)
blender-scene mountain --engine CYCLES --samples 64
```

## Advanced Usage

### Custom Materials
Create custom material presets in `~/.config/blender-scene/materials/`:
```python
# custom_material.py
def create_material():
    mat = bpy.data.materials.new(name="Custom")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.8, 0.2, 0.1, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.5
    return mat
```

### Programmatic Scene Building
For complex scenes, write custom Python scripts:
```python
# my_scene.py
import bpy

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Add your custom objects...

# Render
bpy.context.scene.render.filepath = '/path/to/output.png'
bpy.ops.render.render(write_still=True)
```

Then run:
```bash
blender --background --factory-startup --python my_scene.py
```

## Performance Tips

1. **Use EEVEE for quick previews**, CYCLES for final renders
2. **Lower resolution** during development (1280x720)
3. **Reduce geometry** - fewer vertices = faster renders
4. **Limit displacement modifiers** - they're computationally expensive
5. **Use instancing** for repeated objects (trees, grass, etc.)

## Integration with OpenClaw

The skill integrates with OpenClaw's agent system:
```bash
# Agents can call the tool directly
comms post projects "Creating mountain render for client presentation"
blender-scene mountain --output ~/client/mountains.png
```

## License

MIT License - Free for personal and commercial use.
