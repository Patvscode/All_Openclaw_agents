---
name: remote-app-builder
description: Build and validate remote-accessible web apps for the OpenClaw/Tailscale setup. Use when creating or fixing a frontend/backend app that must work from a phone, another device, or a Tailscale URL, especially Vite + FastAPI or WebSocket apps. Covers bind addresses, same-origin config, remote validation, serviceization, and “don’t say ready until it is actually reachable.”
---

# Remote App Builder

Build apps for how this machine is actually used: phone-first, Tailscale-reachable, and reliable after the chat ends.

## Delivery rule

Do not say an app is ready until all required pieces are verified:

1. Every required process is running.
2. Every required port is listening.
3. Local HTTP checks pass.
4. Tailscale HTTP checks pass.
5. If the app uses WebSockets, connection state is visibly working.
6. If the app is meant to persist, it runs under a managed service, not only a dev shell.

A healthy backend alone is not enough if the frontend is down. A healthy frontend alone is not enough if the backend or websocket path is down.

## Default architecture choices

### Bind addresses
- Frontends for remote use: bind `0.0.0.0`
- APIs for remote use: bind `0.0.0.0`
- Model servers that should stay host-only: bind `127.0.0.1`

### Frontend-to-backend wiring
Prefer this order:

1. **Same-origin routing** via reverse proxy or unified service
2. **Environment/config-based backend URL**
3. Hardcoded IP only as a temporary debug step

Never hardcode a Tailscale IP in frontend source as the durable design unless Pat explicitly wants that.

### Service style
Prefer a stable service for anything Pat will revisit from phone. Dev servers are acceptable for short debugging, but say clearly that they are temporary.

## Build workflow

### 1. Identify the full app surface
List every moving part before claiming status:
- frontend port
- backend/API port
- websocket path
- model/runtime dependencies
- any reverse proxy or service wrapper

### 2. Check actual listeners
Use `ss -ltnp` or equivalent. If a port is not listening, the app is not up.

### 3. Verify both local and remote paths
Check at minimum:

```bash
curl -I http://127.0.0.1:<frontend-port>/
curl -I http://100.109.173.109:<frontend-port>/
curl http://127.0.0.1:<api-port>/
```

If the app is split frontend/backend, test both.

### 4. Validate websocket behavior
If the UI depends on a websocket badge or live feed, verify the websocket path, not just HTTP.

If needed, inspect browser console/network or use a local websocket test client. A backend handshake from the host does not prove the phone frontend bundle is current.

### 5. Check mobile assumptions
For phone-facing apps:
- expect stale mobile browser caches
- add explicit reconnect behavior
- expose clear connected/disconnected state
- use `visibilitychange`/foreground reconnect logic when websockets matter

### 6. Decide whether to persist it
If Pat wants ongoing use, move from ad hoc dev server to managed service.

For service work in this environment, follow the OC control rules already documented in shared guidance. Do not freehand random long-lived services.

## Vite + FastAPI pattern

### Vite dev
Use:

```bash
npm run dev -- --host 0.0.0.0 --port <port>
```

### FastAPI
Use:

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port <port>
```

### Frontend config pattern
Prefer a configurable base URL, for example via env or same-origin pathing. Avoid source like:

```ts
new WebSocket('ws://100.109.173.109:8000/ws')
```

Prefer a computed URL based on `window.location` or an env var.

## Required handoff/reporting format

When reporting status, include:
- what was broken
- which ports/processes were missing or misbound
- what was changed
- exact URLs verified
- whether the current run is temporary or persistent

Do not say “good to go” without the verification lines.

## Quick tool

Run this first for split apps:

```bash
bash skills/remote-app-builder/scripts/check_remote_app.sh \
  --frontend-port 5174 \
  --backend-port 8000 \
  --tailnet-host 100.109.173.109
```

For the full checklist and design rules, read `references/remote-app-checklist.md`.
