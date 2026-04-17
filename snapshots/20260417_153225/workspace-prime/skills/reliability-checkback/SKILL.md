---
name: reliability-checkback
description: Lightweight triage to decide how often to re-check critical work (services, agents, runtimes) while changes are in-flight. Use to avoid forgetting fragile tasks.
---

# Reliability Checkback

Use this when working on unstable or high-impact changes.

## Quick score
```bash
checkback-score <criticality 1-5> <instability 1-5> <blast_radius 1-5> <recency_risk 1-5>
```

Example:
```bash
checkback-score 5 4 4 4
```

## Input guide
- **criticality**: how important the service/workflow is
- **instability**: current failure frequency
- **blast_radius**: how many agents/users are affected
- **recency_risk**: how recently major changes were made

## Action
- Follow returned cadence (e.g., 30 min) until issue is closed.
- Each checkback: health endpoint + tiny functional test + status post if changed.
