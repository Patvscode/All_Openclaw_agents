# Lessons Learned

## 2026-03-02

### Card-002: Message Priority Tags
- Built a reusable Python module for visual priority tagging
- Supports 3 output formats: ANSI (terminal colors), HTML (web rendering), plain text
- Color scheme: Critical=Red, High=Yellow, Normal=Green, Low=Gray
- Can be integrated into messaging systems for visual priority indication

### Card-002: Message Priority Tags (Final Implementation)
- Backend (server.py) already had priority tag parsing in `parse_messages()` - extracts [critical]/[action]/[info] and strips from body
- Frontend (index.html) implementation:
  - CSS: colored left borders for messages (red=#e74c3c critical, orange=#f39c12 action, blue=#3498db info)
  - Header: filter toggles for each priority level
  - JS: `filterMessages()` function to show/hide by priority
  - Updated API endpoint to `http://127.0.0.1:8096/api` (comms server, not hub)
- E2E test passed: posted test message, verified backend parsing, UI renders correctly
- Lesson: Always verify backend/frontend sync - backend was working but UI needed implementation

### Autonomy Engine
- Script has syntax errors in line 24 (`[[: 5\n0:`) - should be investigated
- Chain watchdog also has similar syntax issue in line 8
- These are minor but worth fixing for clean operation
### Card-003: Agent Status Indicators (Final Implementation)
- Backend: Added `/api/agents` endpoint to CommsHandler
  - `get_agent_status()` returns known agents with status/last_seen
  - Currently marks all as online (they've been active today)
  - Future: Could integrate with heartbeat/activity tracking
- Frontend:
  - CSS: Status dots (gray=offline, green+pulse=online)
  - Client-side: Loads agent status in `loadAll()`, renders dots in channel/DM lists
  - Tooltips: Show "Last seen X ago" for offline agents
- API: Running on port 8097 (port 8096 still in use by other process)
- Lesson: Need to properly clean up old server processes before restarting

### Card-002: Message Priority Tags (Recap)
- Backend: Already had priority tag parsing in `parse_messages()`
- Frontend: Added colored left borders (red/orange/blue), filter toggles, client-side filtering
- Lesson: Always verify backend/frontend sync - backend was working but UI needed implementation

### Card-e456ed: AI-Scientist Environment Setup (Progress Update)
- Created isolated workspace at `~/.openclaw/workspace-research`
- Built nanoGPT and grokking experiment templates with runtime health checks
- Implemented experiment runner with timestamped logging
- Guardrails: 70% runtime threshold, 2-hour budget, artifact logging
- Lesson: Always validate runtime health before starting experiments to avoid resource starvation
- Next steps: Test templates, integrate with autonomous scheduler, add metrics/plots capture

## 2026-03-03: Memory Coprocessor Model Selection

**Lesson:** When Jess main model (35B) is active, only the smallest helper models (0.8b) fit in available memory. Larger models (2b-9b) hit 60s timeouts due to memory pressure.

**Key finding:** 
- qwen3.5:0.8b: 48.8s, produces 3 valid structured text units
- qwen3.5:2b/4b/9b: 60s timeouts (exceeds ~59GB available memory)

**Recommendation:** Use 0.8b model with simple text format (not JSON) for keeper extraction. Format works reliably:
```
type: fact
content: Jess working on Memory Coprocessor
importance: 5
```

**Next:** Implement keeper v1 with 0.8b, add RAM guardrails before runs.
