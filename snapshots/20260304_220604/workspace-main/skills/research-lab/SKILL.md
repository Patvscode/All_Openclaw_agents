# Research Lab — Agent Skill

The Research Lab is a unified research platform that connects the entire agent ecosystem. Any agent can conduct structured research while chaining together browsing, model evaluation, status reporting, and team communication — all through one API.

## When to Use

- Investigate a topic systematically (hypothesis → experiment → analysis → writeup)
- Gather information from the web and build a knowledge base
- Need smart model routing based on eval profiles
- Want to announce research progress to other agents
- Chain tools: browse → extract → store → research → experiment

## Ecosystem Integration (port 8097)

The Research Lab is the hub that connects all agent services:

| Service | Port | Integration |
|---------|------|-------------|
| Research Lab | 8097 | Core research pipeline + RAG |
| Computer Use | 8095 | Web browsing → knowledge base |
| Agent Eval | 8093 | Smart model routing per stage |
| Agent Status | 8094 | Auto-reports research activity |
| Agent Comms | 8096 | Announces progress to team |
| Ollama | 11434 | Local model inference |

## Quick Start — Smart Session (recommended)

Create a research session that auto-picks the best models, reports status, and announces to team:

```bash
curl -s http://localhost:8097/api/smart-session -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "topic": "Grokking in small transformers",
    "description": "When and why do small models suddenly generalize?",
    "agent": "main",
    "use_eval_routing": true,
    "browse_first": false
  }'
```

Then run all stages:
```bash
curl -s http://localhost:8097/api/sessions/run -X POST \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "rs-XXXXXXXX"}'
```

## Chaining Tools Together

### Research + Web Browsing
```bash
# Browse the web for research material
curl -s http://localhost:8097/api/browse -X POST \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "rs-XXX", "query": "grokking transformers recent papers"}'

# Or browse specific URLs
curl -s http://localhost:8097/api/browse -X POST \
  -H 'Content-Type: application/json' \
  -d '{"session_id": "rs-XXX", "urls": ["https://arxiv.org/abs/2201.02177"]}'

# After browsing, harvest results into knowledge base
curl -s http://localhost:8097/api/browse/harvest -X POST \
  -H 'Content-Type: application/json' \
  -d '{"browse_session_id": "task-XXXXXXXXX"}'
```

### Research + Model Evaluation
```bash
# Check which model is best for reasoning tasks
curl -s http://localhost:8097/api/ecosystem/eval/recommend/reasoning

# Get all model profiles
curl -s http://localhost:8097/api/ecosystem/eval/profiles
```

### Check Ecosystem Health
```bash
curl -s http://localhost:8097/api/ecosystem
```

## Core API Endpoints

### Sessions
- `POST /api/sessions` — Create session (manual model config)
- `POST /api/smart-session` — Create with eval-based routing + ecosystem integration
- `POST /api/sessions/run` — Run all stages (background)
- `POST /api/sessions/stage` — Run single stage
- `GET /api/sessions/<id>` — Full session state

### Integration
- `POST /api/browse` — Web browse via Computer Use → knowledge base
- `POST /api/browse/harvest` — Harvest browse results into KB
- `GET /api/ecosystem` — Service health check
- `GET /api/ecosystem/eval/profiles` — Model capabilities
- `GET /api/ecosystem/eval/recommend/<category>` — Best model for task type

### Knowledge & Intelligence
- `POST /api/narrate` — Ask 0.8b about session status
- `POST /api/quick-ask` — RAG-enhanced Q&A
- `GET /api/knowledge/search?q=...` — Semantic search
- `POST /api/knowledge/paper` — Add paper to KB

## Thinking Levels
Control reasoning depth per stage:
- `none` — Direct response, no reasoning (fast, cheap)
- `low` — Brief reasoning (4K token budget)
- `medium` — Moderate reasoning (8K budget) [default for most stages]
- `high` — Deep reasoning with reflection (16K budget)

## Model Roles
Each independently configurable:
- `reasoner` — Hypothesis generation, experiment design
- `coder` — Code generation for experiments
- `analyst` — Data analysis and interpretation
- `writer` — Report/paper writing
- `reviewer` — Peer review and critique
- `narrator` — Status summaries (0.8b, cheap)
- `vision` — Visual analysis of plots/figures
- `embedder` — RAG embeddings (nomic-embed-text)

## Example Workflow: Full Research Cycle

```python
# 1. Agent decides to research something
# 2. Smart session auto-picks models from eval profiles
session = POST /api/smart-session {"topic": "...", "use_eval_routing": true}

# 3. Optionally browse for background
POST /api/browse {"session_id": session.id, "query": "related work"}

# 4. Run the full pipeline (ideation → literature → design → experiment → analyze → write → review)
POST /api/sessions/run {"session_id": session.id}
# → Auto-reports to Agent Status dashboard
# → Auto-announces to Agent Comms #projects channel

# 5. Ask the narrator what's happening
POST /api/narrate {"session_id": session.id}

# 6. When done, results are in the session + knowledge base
GET /api/sessions/{id}
```

## Dashboard
http://100.109.173.109:8097

Tabs: Dashboard | New Research | Session View | Models & Thinking | Knowledge Base | Ecosystem
