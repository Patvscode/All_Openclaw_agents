# Computer Use Skill

Full computer use: browser automation AND desktop control via vision-driven agents.

## Two Modes

### Browser Mode (websites)
Headless Playwright — navigate, click, type, scroll on any website.
```bash
cd ~/.openclaw/workspace-main/tools/computer-use
python3 agent.py "Find trending repos on GitHub" --mode browser --url https://github.com
```

### Desktop Mode (full computer use)
X11 desktop control — any app, any window, real cursor movement via xdotool.
```bash
python3 agent.py "Open a terminal and check disk space" --mode desktop
python3 agent.py "Take a screenshot of the desktop" --mode desktop
```

## Agent Integration

### Option 1: Let the small model handle it (autonomous)
The default — qwen3.5:4b does vision + planning. Your agent just kicks it off and reads the result.
```bash
python3 run.py "Search Wikipedia for quantum computing" --url https://en.wikipedia.org
```

### Option 2: Use your own model as planner (agent takes over thinking)
Your agent's model (Opus, GPT-5.3, 35b, etc.) does the planning. 4b still does vision.
```bash
# Override the planner model
python3 agent.py "Complex multi-step research task" --model qwen3.5:35b --mode browser
```

### Option 3: Direct action via API (full agent control)
Your agent issues individual actions directly. Complete control.
```bash
# Start a session, then issue actions yourself
curl -X POST http://localhost:8095/api/action -H 'Content-Type: application/json' \
  -d '{"mode": "desktop", "action": {"action": "click", "params": {"x": 500, "y": 300}}}'

# Or via browser
curl -X POST http://localhost:8095/api/action -H 'Content-Type: application/json' \
  -d '{"mode": "browser", "action": {"action": "goto", "params": {"url": "https://example.com"}}}'
```

### Option 4: Mix — start autonomous, intervene when needed
Start a task with 4b driving, then inject direct actions via `/api/action` if needed.

## API (port 8095)

### Run a task
```bash
curl -X POST http://localhost:8095/api/run -H 'Content-Type: application/json' -d '{
  "task": "Find the weather in NYC",
  "url": "https://weather.com",
  "mode": "browser",
  "agent": "main",
  "planner_model": null,
  "collect_training": true,
  "max_steps": 15
}'
```

### Direct action (agent takes control)
```bash
curl -X POST http://localhost:8095/api/action -H 'Content-Type: application/json' -d '{
  "session_id": "optional-to-track",
  "mode": "desktop",
  "action": {"action": "click", "params": {"x": 640, "y": 360}}
}'
```

### Training data
```bash
# Toggle collection
curl -X POST http://localhost:8095/api/config/training -d '{"enabled": false}'

# Export for fine-tuning
curl -X POST http://localhost:8095/api/training/export -d '{"format": "pairs"}'   # observation-action pairs
curl -X POST http://localhost:8095/api/training/export -d '{"format": "openai"}'  # OpenAI fine-tune format
curl -X POST http://localhost:8095/api/training/export -d '{"format": "jsonl"}'   # raw records
```

### Research library
```bash
# Create category
curl -X POST http://localhost:8095/api/library/category -d '{"name": "AI Papers", "icon": "📄"}'

# Add item
curl -X POST http://localhost:8095/api/library/category/<id>/item -d '{
  "title": "Attention Is All You Need",
  "url": "https://arxiv.org/abs/1706.03762",
  "tags": ["transformer", "attention"],
  "agent": "main"
}'
```

## CLI Options
```
python3 agent.py <task>
  --mode browser|desktop     Control mode (default: browser)
  --url <URL>                Starting URL (browser mode)
  --model <model>            Override planner model
  --max-steps <N>            Max actions (default: 15)
  --no-training              Disable training data collection
  --agent <name>             Agent name for tracking
  --quiet                    Suppress step output
```

## Desktop Actions
| Action | Params | Description |
|--------|--------|-------------|
| click | x, y | Left-click at coordinates |
| double_click | x, y | Double-click |
| right_click | x, y | Right-click |
| type | text | Type text in focused app |
| press_key | key | Press key (Return, ctrl+c, alt+F4, super) |
| scroll | direction, clicks, x, y | Scroll at position |
| drag | from_x, from_y, to_x, to_y | Drag between points |
| focus_window | name | Focus window by title |
| open_app | command | Launch an application |
| move_mouse | x, y | Move cursor |

## Browser Actions
| Action | Params | Description |
|--------|--------|-------------|
| goto | url | Navigate to URL |
| click | text/selector/position | Click element |
| type | selector, text, press_enter | Type into field |
| scroll | direction, amount | Scroll page |
| press_key | key | Press keyboard key |
| hover | selector/position | Hover element |

## Dashboard
http://100.109.173.109:8090/22-computer-use/
- **Live** — Watch sessions in real-time with screenshot stream
- **Training** — Browse/export/delete training data
- **Library** — Categorized research storage
- **Skills** — Auto-discovered skill patterns

## Training Pipeline
Every successful task saves:
1. Task description + result
2. Screenshots at every step
3. Vision analysis → action pairs (fine-tuning format)
4. Export as: raw JSONL, OpenAI fine-tune format, or observation-action pairs

Toggle collection on/off per-task (--no-training) or globally via API.
