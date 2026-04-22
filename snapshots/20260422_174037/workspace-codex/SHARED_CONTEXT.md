# SHARED_CONTEXT.md — Cross-Agent Shared State

## ACTIVE OPS REPAIR: Agent Comms Jess sidebar contact (2026-04-21)
- 2026-04-21 20:37 EDT: Pat asked Codex to fix the current break. Traced the vague request to board card `card-e965b1`: Jess/q35 missing from the Agent Comms direct-message sidebar.
- Verified live backend on `:8096` already had the right data: `/api/profiles` includes `q35 -> Jess`, and `/api/channels?user=pat` returns DM pairs containing `q35`.
- Root cause was the live frontend regression in `/home/pmello/.openclaw/hub/21-agent-comms/index.html`: it fetched `/channels` without `?user=...` and built DM entries from first-seen raw `dm.pair` values instead of choosing a canonical pair per contact.
- Applied a targeted live-file patch and saved backup `/home/pmello/.openclaw/hub/21-agent-comms/index.html.bak-jess-sidebar-20260421-2033`.
- Verification: served source on `:8090/21-agent-comms/index.html` now contains the restored `?user=` fetch and `choosePair(...)` DM-selection logic; simulation against live API payload confirms `HAS_Q35 True` and resolves `q35` to display name `Jess`.
- Remaining cleanup candidate: canonicalize the noisy DM folder namespace on the comms backend so the UI no longer has to score around legacy pair names.

Last updated: 2026-04-21 20:09 EDT by codex

## ACTIVE PROJECT: Workout tracker app UX compression (2026-04-21)
- 2026-04-21 20:42 EDT: Pat reported the first ForgeTrack pass required too much scrolling.
- Updated `/home/pmello/.openclaw/workspace-codex/exports/workout-tracker-app/app/index.html` to reduce page-level scrolling on larger screens by tightening shell/panel spacing, widening the canvas slightly, making the project rail sticky, and moving long project/schedule/session/goals/recovery/history areas into internal scroll zones.
- 2026-04-21 21:10 EDT: Follow-up architecture pass completed after Pat clarified the app needed real tabs instead of one overloaded surface. The file now has four top-level screens: `Today`, `Workout`, `Plan`, and `Progress`.
- The new `Workout` tab automatically syncs to the current weekday's routine, so opening it lands on Tuesday/Wednesday/etc. instead of forcing users to hunt through the page. `Today` is now a summary/launch screen, `Plan` holds project management, and `Progress` holds goals/recovery/history.
- 2026-04-21 21:31 EDT: Second usability pass completed after Pat asked to “make the app good.” `Workout` now has selected-day session notes plus complete/reopen/reset controls, and `Plan` now includes a real in-app day editor and exercise builder so blank project shells can become usable programs without source edits.
- Added state helpers for compliance-goal syncing, selected-day completion/reset flows, session-note persistence, and exercise add/remove handling. This closes the biggest gap from the earlier pass, where the app was structured better but still too static to manage from the UI.
- 2026-04-21 21:40 EDT: Pat flagged the UI as still too wordy and clunky on mobile. Tightened the ForgeTrack header/workout copy in `/home/pmello/.openclaw/workspace-codex/exports/workout-tracker-app/app/index.html`, shortened several Today/Workout labels, changed the day-card CTA from `View` to `Open`, and fixed the actual mobile layout issue by stacking the header, turning the top nav into a 2-column grid, making screen actions full-width, and reducing card padding on small screens.
- The app remains live at `http://100.109.173.109:8765`.
- Verification in this session was source/syntax based: the inline app script was extracted and passed `node --check`, and the updated HTML now includes the primary nav tab markup plus screen-state logic.

## ACTIVE PROJECT: Workout tracker app (2026-04-21)
- 2026-04-21 20:09 EDT: Built a new standalone static app at `/home/pmello/.openclaw/workspace-codex/exports/workout-tracker-app/` for Pat.
- App ships as `app/index.html` plus README; it uses localStorage only, so it runs without backend setup.
- Product shape: projects for workout plans, weekly schedule, day/session detail, exercise-level logging, goals, recovery checklist, and recent history.
- Seeded first project directly from Pat's provided weekly split: Back / Chest & Biceps / Hamstrings & Glutes / Shoulders & Triceps / Quads / Rest / Rest.
- Verification: inline script compiled with `node` (`INLINE_SCRIPT_OK`), local static serve on `python3 -m http.server 8765` returned `HTTP/1.0 200 OK`, and HTTP fetch confirmed expected `ForgeTrack`, `Workout plans`, and `Outcome tracker` markup.
- Next step if Pat wants more: add exercise editing inside the UI, export/import, or a lightweight backend sync layer.


## ACTIVE OPS: Midday AI discovery scan (2026-04-21)
- 2026-04-21 11:58 EDT: Daily midday AI discovery scan completed and report saved to `/home/pmello/.openclaw/workspace-codex/reports/improvement_loop/ai/2026-04-21.md`.
- Strongest practical external signals were: Mem0-style hybrid/entity retrieval, Browser Use grounding/privacy/indexed browser state, OpenHands task visibility/planning, and vLLM Gemma 4 serving improvements.
- Main recommendation did **not** change: keep the OpenClaw stable upgrade to `2026.4.15` and local hardening ahead of adopting outside frameworks or swapping browser/memory stacks.
- Best follow-up candidates after the stable baseline remain a browser mini-benchmark and a memory retrieval bakeoff on real OpenClaw incidents.
- Cron sandbox note: direct `comms`, `board`, `memquery`, and `openclaw status` calls were blocked again by `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so this scan used local config plus the morning OpenClaw report for system grounding.

Last updated: 2026-04-21 09:37 EDT by codex

## ACTIVE OPS: OpenClaw morning improvement scan (2026-04-21)
- 2026-04-21 09:35 EDT: Daily OpenClaw upstream scan completed and report saved to `/home/pmello/.openclaw/workspace-codex/reports/improvement_loop/openclaw/2026-04-21.md`.
- Main recommendation remains upgrade to stable `2026.4.15`, then pilot `agents.defaults.experimental.localModelLean` / tool narrowing on `gemma` only.
- Local config evidence rechecked: `/home/pmello/.openclaw/openclaw.json` still shows `2026.4.14`, Telegram group policy broadly `open`, `gemma` on `tools.profile="full"`, and `q35` already narrowed.
- Important unresolved upstream watch items for post-upgrade smoke tests: issue `#69719` (auth failures do not trigger fallbacks) and issue `#69715` (stale `skillsSnapshot` after restart).
- Cron sandbox note: direct `openclaw status` and `openclaw cron list --json` collection was blocked in this run by `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so follow-up live CLI verification should happen in an interactive session.
- 2026-04-21 09:37 EDT: Detached runner `python3 tools/improvement_loop/codex_improvement_loop.py` exited cleanly; continuity state synced, no additional remediation required from the cron lane.


## ACTIVE PROJECT: Side Street Arcade standalone site
- 2026-04-20 22:05 EDT: Pat asked for a new website separate from Clawboard, with an arcade feel centered on street-sports/city-energy concepts like skateboarding, baseball, and related mini-games.
- Created standalone project folder: `/home/pmello/.openclaw/workspace-codex/projects/arcade-site`.
- First pass shipped as a static branded shell with `index.html`, `styles.css`, and `app.js`.
- 2026-04-20 22:14 EDT: Continued the build and turned `Skate Riot` into a real embedded playable prototype instead of keeping the site shell-only.
- 2026-04-20 22:21 EDT: Deepened `Skate Riot` into a more skate-specific cabinet rather than splitting to a second game yet.
- Current site includes: bold urban arcade landing page, animated city-stage hero, cabinet grid for `Skate Riot`, `Midnight Derby`, `Street Run`, `Rooftop Dash`, and `Cage Heat`, a live spotlight panel that updates on click/keyboard selection, and a `Play` section with a canvas cabinet for `Skate Riot`.
- Playable prototype details now include: jumping, lateral movement, obstacle dodging, spark pickups, combo meter, air tricks via keyboard/touch, manual landing windows, spawned rails with grind locking, score/best-score HUD, action buttons, and touch controls. Best score persists via `localStorage`.
- Verification: `node --check app.js` passed, HTML parser check returned `HTML_OK`, and local preview served over `python3 -m http.server 8787`; HTTP fetch confirmed the live page contains the new trick control and updated prototype instructions.
- Important framing: this is now a real arcade anchor, not just a shell. `Skate Riot` is playable with a distinct score loop, while the other cabinets remain concept slots.
- Next step: either add more juice/variation to `Skate Riot` or start a second playable cabinet using the same shell and UI pattern.

## ACTIVE OPS REPAIR: Codex context reset metadata
- 2026-04-20 16:34 EDT: Pat reported Codex context clearing still did not work. Screenshot/status showed `agent:codex:main` on `codex/gpt-5.4` with `Context: 1.2m/200k (598%)`, `Compactions: 0`, and a stale active CLI task from 2026-04-11 (`Reply with exactly: GS_OK`).
- Diagnosis: the active Codex direct and Telegram group session files were tiny (`fa234450...jsonl` about 4.3 KB and `36a611ea...jsonl` about 3.5 KB), but `/home/pmello/.openclaw/agents/codex/sessions/sessions.json` carried inherited token telemetry around 1.1M-1.2M tokens plus large stale prompt snapshots. This made `/status` report over-limit context even after `/new`/clear.
- Repair: backed up `sessions.json` to `/home/pmello/.openclaw/agents/codex/sessions/sessions.json.bak-context-reset-20260420T163253-0400`; cancelled stale CLI tasks `7263a818-a397-472f-b861-d4d55eeac2d2` and `fd92d564-55c0-4203-a570-55b25a211edc`; ran `openclaw tasks maintenance --apply`; normalized `agent:codex:main` and `agent:codex:telegram:group:-5257163977` metadata to 6.5k/200k and pruned stale `skillsSnapshot`, `systemPromptReport`, `pluginDebugEntries`, and compaction checkpoint blobs.
- Verification: `openclaw sessions --agent codex --active 120 --json` now reports both active Codex lanes at `inputTokens=6500`, `totalTokens=6500`, `contextTokens=200000`; `openclaw tasks list --runtime cli --status running --json` reports zero running CLI tasks. The in-process `session_status` call during the same already-started turn may still show old cached context until the next inbound turn.

## ACTIVE PROJECT: Clawboard revamp Phase 0 registry/audit
- 2026-04-19 22:48 EDT: Pat approved proceeding after the Clawboard proposal and asked Codex to back everything up, document locations, and centralize files where they are easy to find.
- Manual backup completed first: local snapshot `/home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots/20260419_224303`; log says remote push failed with existing auth/remote issue.
- Follow-up backup after docs/scripts: local snapshot `/home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots/20260419_224938`; remote push also failed with existing auth/remote issue.
- Central shared project folder created: `/home/pmello/.openclaw/projects/clawboard-revamp` (also reachable from Codex as `projects/clawboard-revamp`).
- Key docs/artifacts now live there: `README.md`, `CODEBASE_INDEX.md`, `registry/clawboard-app-registry.draft.json`, `reports/clawboard-inventory.md`, `reports/clawboard-inventory.json`, and `scripts/build_clawboard_inventory.py`.
- First audit parsed 47 cards from `/home/pmello/.openclaw/hub/index.html`, grouped them into 6 proposed workspaces, and found 0 missing local filesystem routes.
- Important rule: do not move live hub/runtime trees during Phase 0; the central folder is an index/working area until service migration is intentionally planned.
- 2026-04-19 22:56 EDT: Registry audit dependency pass completed. `scripts/build_clawboard_inventory.py` now maps all 47 homepage cards to dependencies with zero unmapped dependencies, records `serviceGroupHealth`, writes a full `unitStatusSnapshot`, and includes service-group definitions derived from the Mission Control app-group model. Regenerated `registry/clawboard-app-registry.draft.json` and `reports/clawboard-inventory.*`; verification found 0 missing local routes and 0 HTTP failures while hub was reachable.
- 2026-04-20 17:49 EDT: Follow-up pass completed after Pat asked to keep working. Confirmed the canonical live registry now lives at `/home/pmello/.openclaw/hub/app-registry.json` and the live homepage renders from it. Updated `scripts/build_clawboard_inventory.py` so it reads the live registry first, falls back to static homepage parsing only for old backups, enriches dependency health from endpoint probes, and writes `registry/live-registry-manifest.json` plus `registry/app-registry.live.snapshot.json` for change detection/versioning. Regenerated reports: 47 apps, sourceMode `live-registry`, 0 missing local routes, 0 HTTP route failures, 0 unmapped dependencies, 5/15 endpoints reachable.
- 2026-04-20 17:49 EDT: Fixed mobile/remote health truth by adding same-origin hub endpoint `/api/clawboard/health` in `/home/pmello/.openclaw/hub/serve.py` and changing `/home/pmello/.openclaw/hub/index.html` to fetch that endpoint instead of probing `127.0.0.1` from the browser. Restarted `max-web-gallery.service`; verified service active, homepage loads, registry has 47 apps/15 endpoints, health endpoint returns ok with 5/15 services reachable. Post-change backup succeeded and pushed: `/home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots/20260420_174844`.
- 2026-04-20 18:10 EDT: Added live homepage health legend/filter chips in `/home/pmello/.openclaw/hub/index.html` for All, Reachable, Degraded, Down, and Static. The filter composes with workspace tabs and text search, and card state is derived from the same `/api/clawboard/health` data used by the health dots. Verification: live HTTP served the new markup, registry JSON parsed, `/api/clawboard/health` returned ok with 5/15 services reachable, extracted page JS passed `node --check`, and classifier counts are 14 reachable / 11 degraded / 8 down / 14 static / 0 unknown. Browser automation was attempted but blocked because the Playwright wrapper expected a missing Chrome binary. Post-change backup succeeded and pushed: `/home/pmello/.openclaw/backups/All_Openclaw_agents/snapshots/20260420_181138`.
- 2026-04-21 22:24 EDT: Pat asked to get `clapboard` back online. Verified the live target is the `Clawboard` shell on `max-web-gallery.service`. Service was already active, but Codex performed a clean restart anyway and rechecked local `http://127.0.0.1:8090/`, remote `http://100.109.173.109:8090/`, and `/api/clawboard/health`. Current truth: the board shell is online after restart; dependency health remains `5/15` reachable, so several internal cards are still degraded even though the board itself is back.
- 2026-04-21 23:06 EDT: Pat asked for an automation flow to group offline apps and make recovery/edit targeting easier. Updated `/home/pmello/.openclaw/hub/index.html` to add a dynamic `Offline` tab, per-card `Recover` and `Edit` checkboxes, and an `Action Queue` panel that persists selections in browser `localStorage` and composes copyable prompts for turn-on/edit requests. Verification: extracted inline JS passed `node --check`, and live fetch from `:8090` confirms the new `Action Queue`, `Offline`, `Recover`, and `Edit` UI text is being served.
- 2026-04-21 23:11 EDT: Pat reported the new buttons were not working. Root cause was likely the control labels inside clickable app-card anchors calling `preventDefault()`, which can suppress checkbox toggling. Patched `/home/pmello/.openclaw/hub/index.html` so the card controls only stop propagation and the queue toggle handler no longer calls `preventDefault()`. Verification: live served source now shows `onclick="event.stopPropagation();"` on the checkbox controls, and the inline script still passes `node --check`.
- 2026-04-21 23:19 EDT: Pat asked for the queue to work like a real shared operator list and include explanation text. Added `/api/clawboard/queue` to `/home/pmello/.openclaw/hub/serve.py`, backed by `/home/pmello/.openclaw/hub/tmp/clawboard-queue.json`. Updated `/home/pmello/.openclaw/hub/index.html` so `Recover`/`Edit` selections load and save through that API, added shared status text plus `What is wrong` / `What needs work` note fields, and included those notes in the generated request previews. Restarted `max-web-gallery.service`; verification confirmed the queue API responds and the live page serves the new shared-queue UI. Temporary test queue data used during verification was cleared immediately.
- Next step: if desired, add per-app notes or a dedicated queue history view for Clawboard triage.

## ACTIVE OPS REPAIR: Main bot model fallback
- 2026-04-20 15:45 EDT: Codex repaired `agent:main:main` durable model config after Pat asked to take care of the pending bot issue. Backups: `/home/pmello/.openclaw/openclaw.json.bak-main-fallback-2026-04-20T19-39-39-850Z` and `/home/pmello/.openclaw/openclaw.json.bak-main-primary-2026-04-20T19-41-24-044Z`. Final config keeps `main` primary on `anthropic/claude-opus-4-6` and adds valid fallback `local/qwen3.6-35b-a3b`; no OpenAI API-key fallback and no stale q35cpp fallback. `claude-opus-4-7` is avoided for now because it rejects current OpenClaw thinking params. Internal probe returned `MAIN_REPAIR_OK`; live session is currently on local fallback because Anthropic still appears billing-blocked.

## ACTIVE OPS REPAIR: Codex/Gammamini model fallback
- 2026-04-20 16:06 EDT: Codex verified `@Gammamini3bot`/codex durable config is `codex/gpt-5.4` with `fallbacks=[]`, backed up `/home/pmello/.openclaw/openclaw.json` to `/home/pmello/.openclaw/openclaw.json.bak-codex-gpt54-nofallback-2026-04-20T16-05-12-325-0400`, restarted `openclaw-gateway.service` and `openclaw-node.service`, and verified `session_status` now shows model `codex/gpt-5.4` with no fallback line.

## ACTIVE OPS REPAIR: Comms board + Memory Concierge embeddings
- 2026-04-19 22:00 EDT: Pat asked Codex to investigate and do needed work.
- Repaired Agent Comms board API availability by creating and enabling user service `dgx-comms.service` for `/home/pmello/.openclaw/comms/web/server.py`; verified `:8096`, `/api/health`, `/api/board`, and `board list`.
- Repaired Memory Concierge query/index path by creating and enabling user service `ollama-embeddings.service` on `127.0.0.1:11434` using shared Ollama models with `OLLAMA_NOPRUNE=true`; verified `nomic-embed-text`, `memquery`, and `memory-indexer.service`.
- Nuance: system `ollama.service` is still inactive/disabled; the active compatibility path is the user-level `ollama-embeddings.service`.


## 📦 SHARED TOOLKIT: spark-viewer (All Agents)
- **Repo:** https://github.com/Patvscode/spark-viewer
- **Local:** `~/Desktop/AI-apps-workspace/spark-viewer/`
- **What:** Reusable modular component library for all agents. Currently has a 3D viewer module; will grow to include UI, server, code, inference, and data components.
- **Rule:** Every component MUST have a GUIDE.md (see CONTRIBUTING.md for template). Written for small models.
- **Daily ritual (1 AM EDT):** All agents should document what they built/learned during the day and contribute reusable components or knowledge to this repo. See `DAILY_CONTRIB.md` in the repo for the process.
- **How to use:** Read the component's GUIDE.md first. It has step-by-step setup, examples, and troubleshooting.

## ACTIVE PROJECT: InSpatio-World Interactive App
- 2026-04-21 09:42 EDT: Codex completed the pending stale-crash cleanup fix in `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py` and pushed commit `eef3766` (`Clear stale crash state for scene-less stops`). The clean-stop gate in `read_status_for_viewer()` now compares launch-scene only against `status.get("scene")` instead of falling back to the UI `active_scene`, so scene-less stopped states no longer preserve an old `previous_stream_status=crashed`. Validation after lightweight viewer restart: `:7861` returned `200`, `/health` stayed `level=ok` with `stream_status=stopped`, `launch_reason=operator_shutdown`, `previous_stream_status=null`, and websocket bootstrap remained `active_scene/status/quality_sync/timer_sync` with status payload `stopped` + `previous_status=null`. Restart note: `systemctl --user restart inspatio-stream-viewer.service` hung in `deactivating`, so the lingering old viewer PID had to be killed once before clean service start; follow-up improvement could harden viewer SIGTERM/shutdown handling later.
- **Location:** `~/Desktop/AI-apps-workspace/inspatio-world/`
- **GitHub:** https://github.com/Patvscode/inspatio-dgx-spark
- **Status:** Live and actively improved, but still operationally fragile in a few places
- **Remote viewer URL:** `http://100.109.173.109:7861/`
- **Current runtime truth:**
- **Morning supervisor validation (2026-04-20 09:35 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.010s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service` since 2026-04-19 23:43 EDT with `NRestarts=0`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. `interactive_io/frames` has no files and no recent `interactive_io` writes; service logs have no entries since 09:05. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0935 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 08:35 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.010s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service` since 2026-04-19 23:43 EDT with `NRestarts=0`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. No `interactive_io` files changed in the last 10 minutes. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0835 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 08:06 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.009s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. No `interactive_io` files changed in the last 10 minutes. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0805 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 07:35 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` within the 3s audit window, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. No `interactive_io` files changed in the last 10 minutes. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0735 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 07:07 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` within the 3s audit window, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0708 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 06:36 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.010s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure. Syntax validation passed with `PYTHONPYCACHEPREFIX=/tmp/inspatio_pycache_0635 python3 -m py_compile stream_viewer.py dit_stream.py live_camera.py`.
- **Morning supervisor validation (2026-04-20 06:06 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.009s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure.
- **Morning supervisor validation (2026-04-20 05:36 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.009s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. `previous_status=crashed` remains stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure.
- **Morning supervisor validation (2026-04-20 05:08 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync returned `active_scene/status/quality_sync/timer_sync` in 0.009s, and the stream is idle/stopped rather than actively producing frames. Only lightweight `stream_viewer.py` is running under `inspatio-stream-viewer.service`; no heavy run was started. Small audit confirmed `previous_status=crashed` is stale persisted metadata from scene-mismatched stopped launch state (`IMG_7643.mp4` launch record vs active `ScreenRecording_04-14-2026_01-17-32_1.mp4` viewer scene), not an active failure.
- **Morning supervisor validation (2026-04-20 04:36 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync is responsive, and the stream is idle/stopped rather than actively producing frames. No heavy run was started. Small audit confirmed `/interactive_io/status.json` and `/health.status.previous_status` still expose old `previous_status=crashed` because the stopped launch state scene differs from the active viewer scene; live health remains OK because the crash is stale.
- **Morning supervisor validation (2026-04-20 04:05 EDT):** viewer on `:7861` is reachable, `/health` is `level=ok`, websocket initial sync is responsive, and the stream is idle/stopped rather than actively producing frames. No heavy run was started. Follow-up candidate: clear stale `previous_status=crashed` from viewer-safe stopped websocket/status payloads after the existing 300s monitor window; source edit was not applied from this cron session because the InSpatio repo is outside writable roots.
- **Current wrapper-validation truth (2026-04-16 02:23 EDT):**
  - `scripts/launch_heavy_stream.sh --scene IMG_7643.mp4 --quality draft --steps 25 --dry-run` returned a truthful deny: `llama_main_service_inactive`
  - this means the wrapper is behaving honestly under unmet prerequisites
  - current heavy-path blocker is prerequisite service readiness (`llama-main.service` / `:18080`), not wrapper ambiguity
  - operator notes now live at `interactive_io/heavy_launch_notes.md`
  - viewer serves on `:7861`
  - Docker container `inspatio-world` is running
  - stream backend can reach healthy `streaming` state around `4.4 FPS`
  - live controls now work materially better than the original state
- **Important caveat:** the viewer process is still ad hoc, not a managed service, so remote access can fail if `stream_viewer.py` dies and must be restarted manually.
- **What was actually implemented by codex in this pass:**
  - real live camera steering path
  - removed fake browser viewport movement so controls are visually honest
  - sped startup by skipping expensive Torch compile warmup in the stream path
  - fixed live-camera latent block sizing mismatch that had been crashing joystick steering
  - added hold-to-reset to prevent accidental reset triggers
  - added vertical controls (`moveZ`) and a home/start-position button
  - hardened first-time video scene processing and stale partial cleanup
- **Recent pushed commits:**
  - `1be9b28` Implement live camera steering path
  - `cb48cd6` Make stream controls honest and speed startup
  - `e47aadd` Fix live camera latent block sizing
  - `b9a6f62` Require hold to trigger stream reset
  - `58f81da` Add vertical controls and home button
  - `fbcc952` Harden first-time video scene processing
- **Current architecture truth is no longer planning-only. It is a live hybrid system:**
  - `app.py` = batch mode baseline on `:7860`
  - `stream_viewer.py` = remote full-screen viewer / websocket control app on `:7861`
  - `dit_stream.py` = streaming DiT backend
  - `live_camera.py` = live point-cloud camera renderer used by the stream path
  - `interactive.py` = separate Viser-style refinement path
- **Key remaining risks / next improvements:**
  1. persist viewer cleanly without keeping GPU-heavy stream always hot
  2. build resource-aware enter/exit InSpatio mode instead of ad hoc service pausing
  3. document and restore paused services cleanly, especially Ollama-backed memory embeddings on `127.0.0.1:11434`
  4. continue validating first-time fresh upload → process → stream flow
- **Any agent picking this up:** read `docs/HANDOFF.md`, then inspect `stream_viewer.py`, `dit_stream.py`, and `live_camera.py` before changing behavior.

## PARKED: InSpatio-World Path B (Speed Optimization)
- **File:** `docs/INSPATIO_PATH_B_EXPERIMENTAL.md`
- **What:** Optimized PyTorch wheels, flash-attn build, WorldFM scout renderer for near-real-time
- **Status:** Research done, not started. Return when ready to push beyond ~2 min/gen.
- **Key repos:** GuigsEvt/dgx_spark_config, inspatio/worldfm
- **Key finding:** FlashAttention-4 does NOT work on GB10 (needs SM100 datacenter Blackwell)

## ACTIVE PROJECT: Imagine Studio, workflow-system capability pass

### ERNIE-Image app integration, 2026-04-16 03:28 EDT
- ERNIE-Image is now integrated into Imagine Studio as a real shipped image lane:
  - recipe key: `image.ernie`
  - runtime type: `local-diffusers-image`
- Runtime lives at:
  - `~/.openclaw/hub/45-imagine-studio/runtime/ernie-image/`
- Standalone status:
  - launcher now uses its own dedicated venv at `runtime/ernie-image/venv`
  - runtime is no longer launched through the ComfyUI Python interpreter
  - model and dependency stack were split so ERNIE can run as its own local diffusers lane
- App/backend wiring completed:
  - `~/.openclaw/hub/imagine-studio-api.py` now exposes `image.ernie`
  - `/api/imagine-studio/models` and `/api/imagine-studio/bootstrap` now include ERNIE-Image in the active image set
  - Create routing now accepts `qualityMode: ernie`
- Product UI pass completed:
  - Create now exposes explicit model selection by actual model name instead of only marketing buckets
  - resolution controls now show exact output dimensions instead of only aspect labels
  - cache token bumped so phones should pull the new module bundle after refresh
- Validation completed:
  - app-driven job `35ced771-406e-4021-bc4d-405e18b686c5` completed successfully through the normal Imagine Studio jobs path
  - result asset: `gen-5144a23069`
  - backend recorded as `ERNIE-Image`
- Important nuance:
  - the first standalone-vs-venv decoupling attempts surfaced missing local CUDA/lib metadata issues and an OOM during direct standalone smoke before the GPU-control path was reused
  - final working path uses the standalone ERNIE runtime plus the existing GPU-exclusive service-gating pattern for actual generation jobs

### Model-metadata refresh, 2026-04-16 02:31 EDT
- The app stack is live on `:8090` with the Imagine Studio API on `:8112`.
- `~/.openclaw/hub/imagine-studio-api.py` was refreshed so the metadata endpoints now match the actual product surface instead of older hidden-lane assumptions.
- Verified after `max-web-gallery.service` restart:
  - `/api/imagine-studio/bootstrap` now reports surfaced image lanes as `FLUX Schnell + FLUX.2 Klein + Qwen Image`
  - `/api/imagine-studio/models` now marks `image.fast`, `image.fast.hq`, `image.premium`, `enhance.image`, and staged `edit.image` as product-visible, while `video`, `LTX 2.3`, and `Wan 2.2` remain backend-hidden
- Important nuance preserved:
  - `image.premium` is set up and runnable, but its latest verification still timed out, so it should be treated as provisioned but not freshly re-proven in this pass

### UI refinement follow-up, 2026-04-16 02:15 EDT
- A background UI refinement pass completed and wrote:
  - `reports/imagine-studio-ui-refinement-pass-2026-04-13.md`
  - `reports/imagine-studio-ui-refinement-pass-2026-04-13.html`
  - `reports/imagine-studio-ui-refinement-pass-2026-04-13.pdf`
- Product-facing polish that landed in this pass:
  - shared lane presentation helper in `~/.openclaw/hub/45-imagine-studio/app/labels.js`
  - Jobs cards now use user-facing titles like Quick image / Creative image / Photoreal image / Enhanced image
  - secondary metadata chips now keep truthful mode, exact model, operation, elapsed time, asset type, and `recipeKey`
  - lane labeling is now centralized across Create, Jobs, Library, and Viewer instead of per-surface text drift
- Validation/support asset added:
  - `~/.openclaw/hub/45-imagine-studio/data/people-realism-validation-set.json`
- Recommended next UI move from the pass itself:
  - keep current feed as default, then add an optional compact Library grid with lightweight filters (`All`, `Saved`, `Quick`, `Creative`, `Photoreal`, `Enhance`)
- Important constraint preserved:
  - this was a UI truth/polish pass, not a backend-readiness change, so staged lanes like `edit.image` remain blocked until their backend path is actually fixed

### Workflow foundation update, 2026-04-13 20:39 EDT
- Stable-state product pass landed without changing the render hardening model: no poll expansion, no global surface replacement, no Jobs-driven Library rerender path added.
- Frontend store now carries persistent `selectedAssetId`, so uploaded, generated, or enhanced images can become first-class workflow bases.
- Create, Library, and Viewer are now wired around that shared source-selection model:
  - `Use as base`
  - `Using as source`
  - `Edit (coming soon)` when backend is blocked
  - `Enhance again`
  - `Animate`
- Library polish stayed intentionally light: more consistent card height feel, tighter mobile filter row behavior, and workflow-row/action clarity.
- Agent panel was compacted into grouped product-facing sections instead of repetitive stacked blocks.
- Cache/version token bumped to `20260413n` to keep app modules on one shared state graph.

Edit backend diagnosis after this pass:
- `edit.image` remains **blocked** and still must not be shown as active.
- The staged Qwen edit bundle looks **locally fixable**, not fundamentally unavailable:
  - `model_index.json` declares a root `tokenizer` component
  - tokenizer artifacts currently exist under `source/processor/`, not under the expected `source/tokenizer/`
  - expected missing root tokenizer payload is:
    - `tokenizer/tokenizer.json`
    - `tokenizer/tokenizer_config.json`
    - `tokenizer/merges.txt`
    - `tokenizer/vocab.json`
    - `tokenizer/special_tokens_map.json`
    - `tokenizer/added_tokens.json`
    - `tokenizer/chat_template.jinja`
- Present on disk already:
  - `text_encoder/` weights + index
  - `transformer/` weights + index
  - `vae/` weights
  - `scheduler/scheduler_config.json`
- Recommended direction for the next backend decision:
  - first choice: finish/fix the local Qwen edit bundle layout and re-smoke the existing runner
  - fallback only if that fails: pivot to a Comfy inpaint/edit lane built from proven inpaint primitives

### Product capability update, 2026-04-13 20:18 EDT
- Render-stability hardening remains untouched in principle: no global rerender changes, no polling expansion, no surface-mount rewrite in this pass.
- Upload and workflow-chain product wiring remains in place for:
  - `upload.source`
  - `enhance.image`
  - existing generated-image lanes
- `edit.image` is now treated truthfully as **staged, not active**.

Backend truth verified:
- ComfyUI core does contain image-edit building blocks (`LoadImage`, `VAEEncodeForInpaint`, `SetLatentNoiseMask`, `InpaintModelConditioning`).
- Imagine Studio has a real local edit runner at:
  - `45-imagine-studio/runtime/qwen_image_edit_runner.py`
- That runner uses `diffusers.QwenImageEditPlusPipeline` against the staged Qwen edit bundle.
- A real smoke run failed during model load because the staged bundle is incomplete:
  - missing `tokenizer/`
  - missing `tokenizer_config.json`
- Result: `edit.image` is wired but **blocked**. Do not present it as active.

What changed in this correction pass:
- Backend lane registry now blocks `edit.image` when the staged model bundle is incomplete.
- `lane-verifications.json` now records `edit.image` as failed/blocked with the actual reason.
- Registry/model-catalog lane payload now includes:
  - `requiresSource`
  - `supportsUpload`
  - `supportsGeneratedSource`
  - `operation`
- Frontend now truthfully gates edit actions in Create, Library, and Viewer with:
  - `Edit (coming soon)`
  - `Edit coming soon (backend not active)`
- Upload, Enhance, and Animate remain available.
- Source typing was tightened for lineage:
  - upload → `sourceType: upload`
  - edit → `sourceType: edit`
  - enhance → `sourceType: enhance`

Verification completed so far:
- direct edit smoke test failed truthfully for missing tokenizer artifacts
- backend Python syntax passed
- updated frontend module syntax passed via `node --check`

Still needs manual browser smoke validation before calling fully done:
- upload image appears in Library
- uploaded image opens in Viewer
- edit shows as staged/gated, not fake-active
- derived outputs preserve lineage and original source
- enhance/animate quick actions work from uploaded images

## ACTIVE PROJECT: Imagine Studio, multi-lane backend truth pass for official target models

### Executive summary
This project has now moved from scattered one-off model wiring to a **single multi-lane backend registry**.

### UI activation update, 2026-04-13 17:16 EDT
- The frontend activation pass is now in progress for the three verified image lanes only:
  - `image.premium -> Qwen`
  - `image.fast.hq -> FLUX.2 Klein`
  - `enhance.image -> Real-ESRGAN`
- Create UI now exposes a simple three-way image model selector:
  - Fast = FLUX Schnell
  - Premium = Qwen
  - High Quality = FLUX.2 Klein
- Library and Viewer now expose `Enhance` on image assets only.
- Video creation remains backend-available but is intentionally hidden from the active UI surface.
- FLUX.2 Dev remains unexposed and not wired as a truthful public lane.
- New report artifacts:
  - `reports/imagine-studio-ui-activation-2026-04-13.md`
  - `reports/imagine-studio-ui-activation-2026-04-13.html`
  - `reports/imagine-studio-ui-activation-2026-04-13.pdf`

What changed in this pass:
- Kept shipped baseline untouched:
  - `image.fast -> FLUX.1 Schnell`
- Hardened shared backend plumbing in `~/.openclaw/hub/imagine-studio-api.py`:
  - prompt submission now checks Comfy `node_errors`
  - history polling now checks queue disappearance instead of silently timing out
  - output collection now supports image/video-style outputs through the same path
- Added one central backend lane registry for:
  - `image.fast -> FLUX.1 Schnell`
  - `image.fast.hq -> FLUX.2 Klein`
  - `image.premium.candidate -> Qwen Image`
  - `video.fast.candidate -> LTX 2.3`
  - `video.premium.candidate -> Wan 2.2`
  - `video.alt.candidate -> HunyuanVideo 1.5`
  - `enhance.image -> Real-ESRGAN x4plus`
  - `edit.image.candidate -> Qwen-Image-Edit-2511`
- Added hidden backend registry routes:
  - `GET /internal/lanes`
  - `POST /internal/lanes/{lane_name}/jobs`
- Added persistent lane verification tracking:
  - `~/.openclaw/hub/45-imagine-studio/data/lane-verifications.json`
- Wrote fresh truth-report artifacts:
  - `reports/imagine-studio-multilane-truth-report-2026-04-13.md`
  - `reports/imagine-studio-multilane-truth-report-2026-04-13.html`
  - `reports/imagine-studio-multilane-truth-report-2026-04-13.pdf`

Current truthful lane state:
- **Verified and passing now:** `image.fast`, `image.premium`, `enhance.image`, `video`, `image.fast.hq`
- **Important runtime change:** `/home/pmello/ComfyUI` was upgraded from detached commit `0a674689` (`2025-11-29`) to upstream `master` at `acd71859` / `v0.19.0`
- **New runtime truth:** the upgraded ComfyUI build now contains the Flux2/Klein support that was previously missing:
  - `Flux2.clip_target()` exists in `comfy/supported_models.py`
  - `KleinTokenizer` and `klein_te()` exist in `comfy/text_encoders/flux.py`
  - `comfy/sd.py` now routes `QWEN3_4B` with `CLIPType.FLUX2` through `klein_te(...)`, not `z_image`
- **Main project outcome:** hidden lane `image.fast.hq -> FLUX.2 Klein` now completed successfully under the existing serialized GPU-exclusive execution path:
  - job `4f997b84-7ace-458b-8a15-857f69510c9c`
  - output `/home/pmello/.openclaw/hub/45-imagine-studio/data/generated/imagine-flux2-klein-20260413-164436-3832d0.png`
- **Regression outcome after runtime upgrade:**
  - `image.fast -> FLUX Schnell` passed, job `44c9a66a-aca2-4d16-ab41-c23899646ffa`
  - `image.premium -> Qwen Image` passed, job `41c2c92f-7388-46a6-93f2-8cee248f397c`
  - `enhance.image -> Real-ESRGAN x4plus` passed, job `8487c14f-23eb-41d8-98b6-f91ca70122b6`
- **Serialization truth remains intact:** the API still stops `llama-main.service` and `gemma-e2b.service` before each Comfy job and restores them afterward; post-job recovery returned both services active in this pass.
- **FLUX.2-dev truth after upgrade:** still **staged-only** and **not testable as an Imagine Studio lane**. A fresh registry scan found no hidden FLUX.2 Dev lane at all, so there is still no truthful first-class runtime path to execute.
- **Remaining hidden blocked lanes:** `video.fast.candidate`, `video.premium.candidate`, `edit.image.candidate`
- **New collateral-risk truth:** because the serialization layer intentionally stops local llama helpers during Comfy windows, some local consumers saw brief connection/503 errors while those services were reloading. That is the current tradeoff, but it did not break Imagine Studio job completion or leave jobs stuck.
- **Fresh validation artifacts:**
  - `reports/imagine-studio-comfy-upgrade-validation-2026-04-13.json`
  - `reports/imagine-studio-comfy-upgrade-validation-2026-04-13.md`
  - `reports/imagine-studio-comfy-upgrade-validation-2026-04-13.html`
  - `reports/imagine-studio-comfy-upgrade-validation-2026-04-13.pdf`


### Canonical status
- **Current state:** shipped baseline preserved, real lane registry in place, truth-based lane classification established
- **Default shipped route:** still `image.fast -> FLUX.1 Schnell`
- **Allowed scope for current work:** hidden/runtime verification, exact-model workflow wiring, reversible backend prep, no UI rollout
- **Not allowed in this phase:** UI selector exposure, fake readiness claims, silent model substitution

---

## Why this matters
Pat wants other agents to be able to jump in, audit the current work, and add improvements without losing the current safe baseline.

This file is now the collaboration surface for that.
If you are another agent helping on this project, treat this like a lightweight PR + handoff board.

---

## Project intent and guardrails

### Hard guardrails
- Do **not** break the shipped `image.fast -> FLUX.1 Schnell` mobile baseline.
- Do **not** expose a new lane in the shipped default UI.
- Do **not** mark FLUX.2-dev as shipped or public just because the staged download exists.
- Do **not** pretend Hunyuan or FLUX.2 Klein is verified when it is not.
- Prefer one clean overnight step per wake over noisy retries.

### Current official implementation target
- Hidden backend-only candidate lane:
  - `image.fast.hq`
- Feature flag:
  - `IMAGINE_ENABLE_FLUX2_KLEIN=1`
- Hidden backend route:
  - `POST /internal/recipes/image.fast.hq/jobs`

---

## Current host truth, relevant models installed

### Image
- **Active shipped baseline**
  - `~/ComfyUI/models/checkpoints/flux1-schnell-fp8.safetensors`
- **Installed, hidden-slice target**
  - `~/ComfyUI/models/diffusion_models/flux-2-klein-base-4b.safetensors`
  - `~/ComfyUI/models/diffusion_models/flux-2-klein-4b.safetensors`
  - `~/ComfyUI/models/text_encoders/qwen_3_4b.safetensors`
  - `~/ComfyUI/models/vae/flux2-vae.safetensors`
- **Other relevant installed image-family assets**
  - `~/ComfyUI/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors`
  - `~/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - `~/ComfyUI/models/vae/qwen_image_vae.safetensors`

### Video / adjacent app-relevant families
- `~/ComfyUI/models/checkpoints/ltx-video-2b-v0.9.safetensors`
- `~/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_720p_t2v_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_720p_i2v_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors`
- `~/ComfyUI/models/vae/hunyuanvideo15_vae_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/vae/wan_2.1_vae.safetensors`

Important: those extra families are present, but they are **not** the target of the current slice.

---

## File map, exact paths, and what each file does

### Core backend files
- `~/.openclaw/hub/imagine-studio-api.py`
  - Main Imagine Studio backend API.
  - Owns image/video job creation, job state, library records, model/bootstrap metadata, and hidden route wiring.
  - This is the key file for routing, feature flags, backend model metadata, and hidden recipe behavior.

- `~/.openclaw/hub/serve.py`
  - Hub proxy/server layer.
  - Exposes browser-facing Imagine Studio endpoints and file/upload proxy behavior.
  - Important when checking whether frontend requests are reaching the backend correctly.

### FLUX baseline workflow files
- `~/.openclaw/hub/45-imagine-studio/workflows/api/flux_schnell_api.json`
  - Existing shipped API workflow for the stable FLUX.1 Schnell image baseline.
  - This is the protected default image path and should not be broken.

### FLUX.2 Klein files added for the current slice
- `~/.openclaw/hub/45-imagine-studio/workflows/source/image_flux2_klein.json`
  - Staged source/reference workflow pulled from the official Comfy workflow template family.
  - Serves as the durable upstream-style source artifact for the hidden Klein slice.

- `~/.openclaw/hub/45-imagine-studio/workflows/api/flux2_klein_api.json`
  - Flattened API workflow used by the backend hidden route.
  - This is the workflow actually submitted to ComfyUI for `image.fast.hq`.

### Other currently relevant workflow files already in tree
- `~/.openclaw/hub/45-imagine-studio/workflows/api/qwen_image_api.json`
  - Existing Qwen Image API workflow.
  - Relevant for comparison only, not the current official slice target.

- `~/.openclaw/hub/45-imagine-studio/workflows/api/ltxv_text_to_video_api.json`
  - Existing LTX text-to-video workflow.
  - Relevant to current app state, but out of scope for the FLUX.2 Klein slice.

- `~/.openclaw/hub/45-imagine-studio/workflows/source/image_qwen_image.json`
  - Source/reference Qwen image workflow.
  - Useful when comparing node layout and loader assumptions.

- `~/.openclaw/hub/45-imagine-studio/workflows/source/ltxv_text_to_video.json`
  - Source/reference LTX workflow.
  - Relevant to overall app architecture, not current slice implementation.

### Verification and audit files in workspace
- `/home/pmello/.openclaw/workspace-codex/scripts/test_imagine_studio_flux2_klein.py`
  - Repeatable verification script for this slice.
  - Checks baseline behavior with flag OFF, default-route safety with flag ON, and hidden Klein route behavior.

- `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-flux2-klein-test-results-2026-04-12.json`
  - Structured test evidence from the verification script.
  - Use this first when auditing what actually passed and what failed.

- `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.md`
  - Full written implementation report for the current slice.
  - Best human-readable summary of state, scope, evidence, and blocker.

- `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.pdf`
  - PDF export of the implementation report.
  - Good for sharing, not ideal as the primary editable source.

- `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-official-model-expansion-audit-2026-04-12.md`
  - Source-of-truth audit that selected this slice.
  - Do not redo this; use it as the project decision baseline.

- `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-official-model-expansion-audit-2026-04-12.pdf`
  - PDF export of the official audit.

### Coordination and continuity files
- `/home/pmello/.openclaw/workspace-codex/SHARED_CONTEXT.md`
  - Cross-agent handoff and audit sheet for the project.
  - This is the collaboration surface other agents should update.

- `/home/pmello/.openclaw/workspace-codex/RESUME.md`
  - Compact crash-recovery / return-to-work snapshot.
  - Read this to know the latest practical state fast.

- `/home/pmello/.openclaw/workspace-codex/memory/2026-04-12.md`
  - Durable session memory log for today.
  - Contains the durable record of the audit result and current hidden-slice blocked state.

### Relevant on-host model asset paths
#### Active shipped baseline
- `~/ComfyUI/models/checkpoints/flux1-schnell-fp8.safetensors`
  - Current shipped FLUX.1 Schnell image baseline.

#### FLUX.2 Klein assets for current slice
- `~/ComfyUI/models/diffusion_models/flux-2-klein-base-4b.safetensors`
  - Official Klein base checkpoint, staged for testing.

- `~/ComfyUI/models/diffusion_models/flux-2-klein-4b.safetensors`
  - Official Klein alternate/distilled checkpoint, also staged for testing.

- `~/ComfyUI/models/text_encoders/qwen_3_4b.safetensors`
  - Required Klein text encoder staged for the hidden slice.

- `~/ComfyUI/models/vae/flux2-vae.safetensors`
  - Required Klein VAE staged for the hidden slice.

#### Other app-relevant installed assets
- `~/ComfyUI/models/diffusion_models/qwen_image_fp8_e4m3fn.safetensors`
  - Installed Qwen image model asset.

- `~/ComfyUI/models/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors`
  - Qwen image text encoder.

- `~/ComfyUI/models/vae/qwen_image_vae.safetensors`
  - Qwen image VAE.

- `~/ComfyUI/models/checkpoints/ltx-video-2b-v0.9.safetensors`
  - Installed LTX video checkpoint.

- `~/ComfyUI/models/text_encoders/t5xxl_fp16.safetensors`
  - LTX-related text encoder used by that path.

- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_720p_t2v_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_720p_i2v_fp16.safetensors`
- `~/ComfyUI/models/diffusion_models/hunyuanvideo1.5_1080p_sr_distilled_fp16.safetensors`
- `~/ComfyUI/models/vae/hunyuanvideo15_vae_fp16.safetensors`
  - Installed HunyuanVideo family assets relevant to the app overall.

- `~/ComfyUI/models/diffusion_models/wan2.2_t2v_high_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_t2v_low_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_fun_control_high_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/diffusion_models/wan2.2_fun_control_low_noise_14B_fp8_scaled.safetensors`
- `~/ComfyUI/models/vae/wan_2.1_vae.safetensors`
  - Installed Wan family assets relevant to future work, but not to this current slice.

### Practical reading order for any helping agent
1. `/home/pmello/.openclaw/workspace-codex/SHARED_CONTEXT.md`
2. `/home/pmello/.openclaw/workspace-codex/RESUME.md`
3. `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-official-model-expansion-audit-2026-04-12.md`
4. `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.md`
5. `/home/pmello/.openclaw/workspace-codex/reports/imagine-studio-flux2-klein-test-results-2026-04-12.json`
6. `~/.openclaw/hub/imagine-studio-api.py`
7. `~/.openclaw/hub/45-imagine-studio/workflows/api/flux2_klein_api.json`
8. Only then inspect the wider app/backend files if needed

## What CODEX changed and fixed in this pass

### Backend changes
Changed:
- `~/.openclaw/hub/imagine-studio-api.py`

Implemented:
- FLUX.2 Klein feature flag handling
- hidden recipe key `image.fast.hq`
- hidden route `POST /internal/recipes/image.fast.hq/jobs`
- asset readiness checks for Klein workflow + model files
- explicit routing so default `/jobs` image flow remains FLUX Schnell

### Workflow staging
Added:
- `~/.openclaw/hub/45-imagine-studio/workflows/source/image_flux2_klein.json`
- `~/.openclaw/hub/45-imagine-studio/workflows/api/flux2_klein_api.json`

### Verification tooling
Added:
- `scripts/test_imagine_studio_flux2_klein.py`

Generated artifacts:
- `reports/imagine-studio-flux2-klein-test-results-2026-04-12.json`
- `reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.md`
- `reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.pdf`

### Workspace docs/memory continuity
Updated:
- `RESUME.md`
- `memory/2026-04-12.md`
- this file (`SHARED_CONTEXT.md`)

### Workspace git commit for this pass
- `3669c47` — `Document FLUX.2 Klein hidden slice implementation`

---

## Verification results, current truth

### Passed
#### 1) Baseline guard, flag OFF
- Hidden route returned `404`
- Default image route still rendered:
  - recipe `image.fast`
  - model `FLUX Schnell`

#### 2) Default route regression check, flag ON
- Default image route still rendered:
  - recipe `image.fast`
  - model `FLUX Schnell`

This is the most important proof that the shipped path remained protected.

### Failed / blocked
#### 3) Hidden FLUX.2 Klein integration test, flag ON
- Hidden route used the intended recipe:
  - `image.fast.hq`
- But render failed in ComfyUI `UNETLoader`
- Reproduced with both official checkpoints:
  - `flux-2-klein-base-4b.safetensors`
  - `flux-2-klein-4b.safetensors`
- Observed failure:
  - `Got [32, 32, 32, 32] but expected positional dim 64`

### Practical meaning
The slice is not dead code. It is wired, flag-gated, asset-backed, and testable.
But the current host/runtime does not yet successfully execute Klein.

---

## Current blocker analysis
Likely blocker area:
- ComfyUI / Flux2 model-loader compatibility mismatch versus the current Klein checkpoints on this host

What has already been ruled out:
- missing files on disk
- missing workflow staging
- hidden route not wired
- accidental default-route regression

What is **not** yet ruled out:
- need for newer/different ComfyUI core
- need for a different official Klein-compatible workflow variant
- need for checkpoint-specific loader assumptions not met by current build
- hidden dependency/version mismatch in Flux2 support path

---

## Best ways another agent can help right now

### Highest-value audit/help lanes
#### Lane A, runtime compatibility audit
Goal:
- make `image.fast.hq` actually render once, without touching shipped `image.fast`

Good tasks:
- inspect current ComfyUI Flux2 support versus Klein checkpoint expectations
- compare host ComfyUI revision against known working Klein examples
- check whether the official source workflow assumes a newer loader path than this host provides
- identify the smallest runtime upgrade or workflow adjustment needed

#### Lane B, backend/code audit
Goal:
- verify CODEX’s hidden route implementation is clean, minimal, reversible, and correctly isolated

Good tasks:
- review `~/.openclaw/hub/imagine-studio-api.py`
- confirm no accidental default-route behavior drift
- confirm error handling and flag gating are solid
- suggest small cleanup patches only, not broad rewrites

#### Lane C, verification/test audit
Goal:
- improve proof quality without widening scope

Good tasks:
- review `scripts/test_imagine_studio_flux2_klein.py`
- improve reproducibility/logging if needed
- add a tiny additional assertion if it increases confidence without broadening the test suite

#### Lane D, docs/handoff polish
Goal:
- make the current state easier for any future agent to continue from

Good tasks:
- tighten reports
- sharpen blocker summary
- improve next-step recommendations
- keep claims honest and conservative

---

## What helpers should NOT do
- Do not expose FLUX.2 Klein in the Create UI yet.
- Do not repoint `image.fast` away from FLUX Schnell.
- Do not widen into FLUX.2 Dev, LTX 2.3, Wan 2.2 product integration, editing, enhancement, or broad selectors.
- Do not do a broad architecture rewrite.
- Do not mark Klein as working unless a real hidden flagged render succeeds.

---

## Suggested quick-audit assignments
If `main`, `q35`, or another agent joins, these are good short assignments:

- **Agent 1: backend isolation audit**
  - inspect routing + flag logic only
  - report any regressions or cleanup suggestions
- **Agent 2: ComfyUI/Klein runtime audit**
  - inspect the positional-dim mismatch and identify the likely compatibility fix
- **Agent 3: verification/report audit**
  - review test artifacts and suggest any small proof improvements

---

## PR-style collaboration instructions for any helping agent
If you touch this project, append your update under the section below using this format:

```markdown
### Agent update — <agent> — <timestamp>
- Focus:
- Files inspected:
- Files changed:
- What I verified:
- What I fixed or improved:
- Blockers found:
- Recommendation / next step:
```

If you make code changes, also include:
- commit hash if committed
- exact path(s) changed outside workspace if any
- whether the shipped FLUX Schnell route was re-verified after your change

---

## Agent update log

### Agent update — codex — 2026-04-12 15:50 EDT
- Focus:
  - first official target-model expansion slice, hidden FLUX.2 Klein only
- Files inspected:
  - `~/.openclaw/hub/imagine-studio-api.py`
  - `~/.openclaw/hub/45-imagine-studio/workflows/source/image_qwen_image.json`
  - host ComfyUI model directories
  - ComfyUI object info for Flux2-related nodes
- Files changed:
  - `~/.openclaw/hub/imagine-studio-api.py`
  - `~/.openclaw/hub/45-imagine-studio/workflows/source/image_flux2_klein.json`
  - `~/.openclaw/hub/45-imagine-studio/workflows/api/flux2_klein_api.json`
  - `scripts/test_imagine_studio_flux2_klein.py`
  - report artifacts under `reports/`
- What I verified:
  - flag OFF baseline still renders FLUX Schnell
  - flag ON default route still renders FLUX Schnell
  - hidden route is wired and reaches ComfyUI
- What I fixed or improved:
  - created the hidden backend-only path
  - staged Klein assets and workflows
  - built a repeatable verification script and report
- Blockers found:
  - Klein still fails at runtime in current ComfyUI Flux2 path with positional-dimension mismatch
- Recommendation / next step:
  - focus next agent effort on Klein runtime compatibility only, not on broader product changes

### Agent update — codex — 2026-04-13 04:58 EDT
- Focus:
  - overnight supervisor wake, FLUX.2-dev staging progress refresh, and Comfy health diagnosis
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - `~/.openclaw/hub/tmp/imagine-studio-comfy.log`
  - `~/.openclaw/hub/45-imagine-studio/data/lane-verifications.json`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging remains incomplete at `27.0488%` with `22 / 34` expected files complete and `12` missing
  - `image.fast` remains the last verified shipped lane, with Qwen and Real-ESRGAN still the last successful hidden or adjacent proofs from this pass
  - ComfyUI is currently not healthy on `127.0.0.1:8188`
- What I fixed or improved:
  - narrowed the overnight blocker from generic downtime to a specific startup-time CUDA OOM condition under heavy GPU contention
  - posted a concise status and next-step update to `#ops`
- Blockers found:
  - ComfyUI startup attempts at `03:56` and `04:03` failed with CUDA OOM during initialization
  - current GPU occupancy is dominated by two active `llama-server` processes, so recovery is not low-risk without interrupting other local inference work
- Recommendation / next step:
  - keep re-checking download progress each wake, and only attempt Comfy recovery if GPU pressure clearly drops or there is explicit approval to interrupt the model servers

### Agent update — codex — 2026-04-13 05:05 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev staging truth, and verified whether the live `:8000` listener was actually Imagine Studio
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live GPU state via `nvidia-smi`
  - live listener/process state for `:8000`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging advanced to `63.7137%` with `33 / 34` expected files complete; only `flux2-dev.safetensors` is still missing
  - ComfyUI is still inactive and GPU pressure is still too high for a clearly low-risk recovery attempt
  - the current `:8000` listener is a separate Gemma Interaction Hub uvicorn process, not the Imagine Studio API, and `/internal/lanes` currently returns `404`
- What I fixed or improved:
  - removed ambiguity around API health by proving the active `:8000` listener belongs to another app
  - refreshed the shared handoff to reflect the much newer FLUX.2-dev download state
- Blockers found:
  - the final FLUX.2-dev top-level checkpoint is still not on disk
  - Imagine Studio backend verification remains blocked until ComfyUI is healthy and the real API is intentionally restored
- Recommendation / next step:
  - keep the overnight pass conservative, wait for the final FLUX.2-dev checkpoint and/or GPU pressure drop, and avoid mistaking the Gemma listener for Imagine Studio readiness

### Agent update — codex — 2026-04-13 07:00 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev completion truth, and re-checked whether runtime health had improved enough for one safe activation action
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live socket/API checks for `:8188` and `:8000`
  - live GPU state via `nvidia-smi`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes matched
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - ComfyUI is still down on `127.0.0.1:8188`, and `:8000` still returns `404` for both `/internal/lanes` and `/health`
  - GPU pressure is still dominated by the same two `llama-server` processes at about `31.99 GiB` and `7.84 GiB`
- What I fixed or improved:
  - kept the overnight handoff truthful and current after the 07:00 wake without making risky runtime changes
- Blockers found:
  - no safe hidden-lane verification can proceed until ComfyUI health changes and the real Imagine Studio API is intentionally live again
- Recommendation / next step:
  - keep future wakes on the same conservative pattern: refresh truth, watch for actual runtime recovery, and only resume Qwen/Hunyuan/Real-ESRGAN verification after the stack is genuinely healthy

### Agent update — codex — 2026-04-13 07:20 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev staged-completion truth, and checked whether there was finally one low-risk runtime move
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live socket/API checks for `:8188` and `:8000`
  - live GPU state via `nvidia-smi`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - ComfyUI still refuses connections on `127.0.0.1:8188`
  - `:8000` still serves a different uvicorn app and returns `404` for both `/health` and `/internal/lanes`
  - GPU pressure is still dominated by the same two `llama-server` processes at about `31.99 GiB` and `7.84 GiB`
- What I fixed or improved:
  - kept this wake non-destructive and refreshed the handoff with one more exact checkpoint rather than forcing a risky recovery attempt
- Blockers found:
  - there is still no clear low-risk path to restart ComfyUI or resume hidden-lane verification while GPU contention and API mismatch remain unchanged
- Recommendation / next step:
  - if a future wake sees real runtime recovery, resume with one hidden verification pass for Qwen or Hunyuan; otherwise keep the overnight loop in truth-maintenance mode only

### Agent update — codex — 2026-04-13 08:20 EDT
- Focus:
  - overnight supervisor wake, re-validated FLUX.2-dev staged completeness, and checked whether the blocked runtime state had actually changed
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live socket/API checks for `:8188` and `:8000`
  - live GPU state via `nvidia-smi`
  - user service visibility via `systemctl --user status imagine-studio-api.service comfyui.service`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - ComfyUI still refuses connections on `127.0.0.1:8188`
  - `:8000` still serves a different uvicorn app and still returns `404` for both `/health` and `/internal/lanes`
  - GPU pressure is still dominated by the same two `llama-server` processes at about `31.99 GiB` and `7.84 GiB`
  - the obvious user unit names `imagine-studio-api.service` and `comfyui.service` do not exist in the current user systemd scope
- What I fixed or improved:
  - added one more exact checkpoint and removed another false recovery assumption, namely that those two user service names are available to restart cleanly
- Blockers found:
  - runtime remains unhealthy
  - the visible `:8000` service is still not the Imagine Studio hidden API
  - there is still no clear low-risk service-level recovery path from this wake
- Recommendation / next step:
  - keep future wakes conservative, and if recovery ever becomes justified, identify the real launch path first instead of assuming those missing user units exist

### Agent update — codex — 2026-04-13 09:00 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev staged-completion truth again, and spent the turn on one safe launch-path discovery pass
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live socket/API checks for `:8188` and `:8000`
  - live GPU state via `nvidia-smi`
  - low-risk file scan hits under `~/.openclaw/hub`, `~/.openclaw`, and workspace files
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - ComfyUI still refuses connections on `127.0.0.1:8188`, and there is still no listener on `:8188`
  - `:8000` still serves a different uvicorn app and still returns `404` for both `/health` and `/internal/lanes`
  - GPU pressure is still dominated by two `llama-server` processes at about `31.26 GiB` and `7.66 GiB`
  - the broader file scan still did not surface a concrete Imagine Studio launcher or service definition, only docs, reports, and persisted job artifacts
- What I fixed or improved:
  - kept the wake non-destructive and replaced another guess with a sharper negative finding about launch-path discovery
- Blockers found:
  - runtime remains unhealthy
  - the visible `:8000` service is still not the Imagine Studio hidden API
  - the real Imagine Studio launch path is still unresolved
- Recommendation / next step:
  - keep future wakes conservative, and if runtime is still blocked next time, continue low-risk launch-path discovery rather than forcing restarts under current GPU pressure

### Agent update — codex — 2026-04-13 09:22 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev completion truth, corrected the real backend launch path, and checked whether the hidden API could still come up safely without touching Comfy
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - `~/.openclaw/hub/serve.py`
  - live socket/API checks for `:8090`, `:8112`, `:8188`, and `:8000`
  - live GPU state via `nvidia-smi`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - the hub server on `127.0.0.1:8090` is live
  - `GET /api/imagine-studio/bootstrap` on `:8090` successfully auto-started the real Imagine Studio API on `127.0.0.1:8112`
  - `http://127.0.0.1:8112/health` and `/internal/lanes` both return `200`
  - lane registry truth still shows `image.fast`, `image.premium`, and `enhance.image` as runnable or verified, while `image.fast.hq` remains blocked by `mat1 and mat2 shapes cannot be multiplied (512x2560 and 7680x3072)`
  - ComfyUI still refuses connections on `127.0.0.1:8188`
  - GPU pressure is still dominated by two `llama-server` processes at about `32.01 GiB` and `7.84 GiB`
- What I fixed or improved:
  - removed the overnight confusion around `:8000` by proving the real launch path is `serve.py` on `:8090` plus `imagine-studio-api.py` on `:8112`
  - gave future wakes a real health-check target that does not depend on guessing systemd unit names
- Blockers found:
  - Comfy itself is still down on `:8188`, so hidden verification jobs are still not a low-risk next move
- Recommendation / next step:
  - use `:8090` and `:8112` as the canonical health path on future wakes, and only resume Qwen or Hunyuan hidden verification after Comfy genuinely recovers

### Agent update — codex — 2026-04-13 09:28 EDT
- Focus:
  - safe follow-up truth refresh after the async wake completed, using the corrected `:8090` to `:8112` Imagine Studio health path
- Files inspected:
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - live API checks for `:8090`, `:8112`, and `:8188`
  - live GPU state via `nvidia-smi`
  - `RESUME.md`
- Files changed:
  - `RESUME.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `GET /api/imagine-studio/bootstrap` on `:8090` still returns `200`
  - `http://127.0.0.1:8112/health` still returns `200` with `imageStatus: ready`
  - `http://127.0.0.1:8112/internal/lanes` still returns `200`, with `image.fast` and `image.premium` verified and `image.fast.hq` still blocked by the same FLUX.2 Klein shape mismatch
  - ComfyUI still refuses connections on `127.0.0.1:8188`
  - GPU pressure is still dominated by two `llama-server` processes at about `32013 MiB` and `7843 MiB`
- What I fixed or improved:
  - kept the overnight state truthful and current without forcing any runtime mutation
- Blockers found:
  - backend health is up, but the actual Comfy executor remains down, so hidden render verification is still not a low-risk next step
- Recommendation / next step:
  - keep using the `:8090` and `:8112` path for lightweight health truth, and wait for real Comfy recovery or explicit approval before any action that could disturb the loaded llama runtimes

### Agent update — codex — 2026-04-13 10:00 EDT
- Focus:
  - overnight supervisor wake, refreshed staged-download truth, and spent one safe pass clarifying the exact Comfy launcher and failure point
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - `~/.openclaw/hub/imagine-studio-api.py`
  - `~/.openclaw/hub/tmp/imagine-studio-comfy.log`
  - live process/socket checks for `:8112` and `:8188`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - the live Imagine Studio API process is `~/.openclaw/hub/imagine-studio-api.py`
  - that API directly launches Comfy via `/home/pmello/ComfyUI/venv/bin/python /home/pmello/ComfyUI/main.py --listen 127.0.0.1 --port 8188`
  - Comfy still never binds `:8188`, and the last logged startup attempts still die immediately in `torch.cuda.mem_get_info()` with `torch.AcceleratorError: CUDA error: out of memory`
  - `image.premium` and `enhance.image` remain verified, while Hunyuan still remains hidden/runnable but unverified
- What I fixed or improved:
  - removed the remaining ambiguity around how Comfy is supposed to come up, so future wakes can stop spending time on launch-path guessing
- Blockers found:
  - the blocker is still startup-time CUDA OOM on the known direct Comfy launcher path, so recovery is not yet a low-risk move
- Recommendation / next step:
  - keep future wakes conservative, re-check `:8188`, and only consider touching the direct Comfy launcher if GPU pressure has clearly changed enough to make that safe

### Agent update — codex — 2026-04-13 10:22 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev staged truth again, and spent one safe pass checking the hidden Hunyuan lane for a concrete next blocker signal
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - `~/.openclaw/hub/tmp/imagine-studio-api.log`
  - `~/.openclaw/hub/tmp/imagine-studio-comfy.log`
  - live API truth via `:8090/api/imagine-studio/bootstrap`, `:8112/health`, and `:8112/internal/lanes`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - direct Comfy on `:8188` is still unavailable, and the Comfy startup log still ends at the same `torch.cuda.mem_get_info()` CUDA OOM before bind
  - the hidden Hunyuan lane still resolves as recipe key `video`, remains wired/runnable/hidden, and is still not verified
  - the live bootstrap payload now shows active hidden job `333a2611-82b5-4ed3-9846-94fdec406c52` for that Hunyuan lane still marked `running` since `03:59 EDT`
- What I fixed or improved:
  - turned the vague Hunyuan "not yet verified" state into a more actionable next-check target, namely a long-running hidden video job that may be stalled or waiting on backend recovery
- Blockers found:
  - direct Comfy is still unhealthy, and the hidden video path has an unresolved long-running job, so launching fresh verification work on that lane would be noisy
- Recommendation / next step:
  - on the next wake, re-check `:8188` first, then re-check whether the hidden Hunyuan job is still stuck before attempting any new video-lane verification

### Agent update — codex — 2026-04-13 10:40 EDT
- Focus:
  - overnight supervisor wake, refreshed FLUX.2-dev staged truth, and used this wake for safe documentation-only staging alignment because runtime health is still split
- Files inspected:
  - `RESUME.md`
  - `reports/imagine_studio_flux2_dev_download_status.json`
  - `~/.openclaw/hub/tmp/imagine-studio-comfy.log`
  - live API truth via `:8090/api/imagine-studio/bootstrap`, `:8112/health`, and `:8112/internal/lanes`
- Files changed:
  - `RESUME.md`
  - `memory/2026-04-13.md`
  - this file (`SHARED_CONTEXT.md`)
- What I verified:
  - FLUX.2-dev staging is still fully complete at `100.0%` with `34 / 34` expected files present and exact manifest bytes still matched at `177,605,823,056`
  - `flux2-dev.safetensors` remains present at the expected `64,446,596,128` bytes
  - direct Comfy on `:8188` still refuses connections while `:8112` and `:8090` remain healthy enough for status inspection
  - the hidden Hunyuan lane still resolves as recipe key `video`, remains wired/runnable/hidden, and still has active job `333a2611-82b5-4ed3-9846-94fdec406c52` marked `running`
- What I fixed or improved:
  - documented FLUX.2-dev more explicitly as a complete staged artifact set that must remain staged-only until runtime alignment can be validated safely
- Blockers found:
  - direct Comfy is still unhealthy from the same startup-time CUDA OOM, so this stack is not stable enough for non-destructive FLUX.2-dev runtime alignment yet
- Recommendation / next step:
  - keep the next wake focused on truthful health checks first, then only attempt hidden Hunyuan or FLUX.2-dev alignment work if `:8188` genuinely recovers

### Agent update — codex — 2026-04-14 04:35 EDT
- Focus:
  - InSpatio morning supervisor wake, quick live-state check, and one small viewer-honesty fix
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
- What I verified:
  - `http://127.0.0.1:7861/` is live
  - websocket accepts connections
  - `interactive_io/status.json` currently reports `stopped`
  - last stream run produced frames cleanly, then stopped normally after block 43
  - after restart, a fresh websocket connection now receives initial `{"type":"status","status":"stopped"}` truthfully
- What I fixed or improved:
  - removed the optimistic fake `streaming` UI state on websocket open
  - added initial server-side status sync on connect so reconnects reflect real stream state immediately
  - set client stopped-state from server `stopped` and `ended` status messages
- Blockers found:
  - current live stream is not actively producing frames; latest known state is cleanly stopped, not crashed
- Recommendation / next step:
  - next wake should prefer a small restart/reload action or scene-start validation to confirm first-frame recovery from a stopped state
  - commit pushed: `ec07c2b` (`Keep stream viewer status honest on reconnect`)

### Agent update — codex — 2026-04-14 05:05 EDT
- Focus:
  - InSpatio morning supervisor wake, live-state refresh, and one small restart-correctness fix in the stream runner
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/dit_stream.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/dit_stream.py`
- What I verified:
  - `http://127.0.0.1:7861/` still returns `200`
  - websocket still responds and reports the active scene plus `{"type":"status","status":"stopped"}`
  - current status file still reports `stopped`
  - last stream exit still shows the NCCL warning about `destroy_process_group()` not being called
  - updated Python sources compile cleanly via `py_compile`
- What I fixed or improved:
  - wrapped `dit_stream.py` entrypoint with a `finally` cleanup path
  - added explicit `torch.distributed.destroy_process_group()` on normal process exit to reduce leaked distributed state and make restart/stop behavior cleaner
- Blockers found:
  - I did not force a fresh heavy render just to validate the shutdown path live, because the system is currently idle and the prompt prefers small safe changes
- Recommendation / next step:
  - next wake can do one light scene-start/stop validation to confirm the shutdown warning disappears in a real stream cycle
  - commit pushed: `1e48a61` (`Clean up distributed state on stream exit`)

### Agent update — codex — 2026-04-14 07:35 EDT
- Focus:
  - InSpatio morning supervisor wake, live-state refresh, and one small shutdown-path hardening change in the viewer
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
- What I verified:
  - `http://127.0.0.1:7861/` returned `200` before and after the viewer restart
  - websocket still responds and immediately reports the active scene plus `{"type":"status","status":"stopped"}`
  - current status file still reports `stopped`
  - last logged stream stop still showed the NCCL cleanup warning, which pointed back to the viewer forcing shutdown too quickly
- What I fixed or improved:
  - increased the graceful wait in `stop_dit_stream()` from about 8 seconds to about 20 seconds before escalating to `SIGKILL`
  - raised the outer stop command timeout to match that longer grace period
  - added explicit stderr logging when the viewer does have to force-kill the stream, so future wakes can distinguish clean exits from forced ones
- Blockers found:
  - I did not run a fresh heavy stream cycle just to trigger a real stop, so the warning-removal effect is not yet re-proven live
- Recommendation / next step:
  - next wake should do one light start/stop validation and check whether the NCCL warning is gone or reduced on a real shutdown
  - commit pushed: `0a98961` (`Let stream shutdown wait longer before force-kill`)

### Agent update — codex — 2026-04-14 09:39 EDT
- Focus:
  - InSpatio morning supervisor wake, live-state refresh, and one small crash-honesty fix in the viewer status path
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
- What I verified:
  - `http://127.0.0.1:7861/` returned `200`
  - websocket responds and now reports `{"type":"status","status":"crashed"}` for the current failed stream
  - current status file now records `crashed` with previous status `streaming`
  - the current DiT PID was still `kill -0`-visible but already a zombie, which explained the false stale/alive impression
- What I fixed or improved:
  - tightened `dit_process_alive()` so zombie or pid-reused processes no longer count as healthy stream workers
  - upgraded previously written `stale` statuses back to `crashed` when the prior state was active and the worker is actually dead
  - restarted the lightweight viewer so the live websocket reflects the corrected truth immediately
- Blockers found:
  - the underlying stream is still genuinely failed on the current scene, with the last logged crash still showing a latent/render tensor height mismatch (`Expected size 45 but got size 30`)
- Recommendation / next step:
  - next wake should target that active stream crash itself, likely in the render-latent sizing path for the current `IMG_7643.mp4` scene, now that the UI no longer hides the failure behind `stale`
  - commit pushed: `2a31341` (`Report crashed streams instead of stale zombies`)

### Agent update — codex — 2026-04-14 09:59 EDT
- Focus:
  - final morning InSpatio pass, fix the active draft-quality crash on `IMG_7643.mp4`
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/dit_stream.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/dit_stream.py`
- What I verified:
  - viewer still serves on `http://127.0.0.1:7861/`
  - the failing scene still had mixed tensor sizes at startup: source `360x624`, but precomputed render/mask `240x416`
  - after the patch, a fresh `dit_stream.py` run now logs explicit resize normalization for those stale precomputed tensors and no longer hits the old immediate `Expected size 45 but got size 30` denoise crash
  - the restarted DiT worker stayed alive in `encoding` instead of dying at first block submission
- What I fixed or improved:
  - normalized precomputed render, mask, and source videos to the selected stream quality before latent encoding
  - made mixed-quality scene artifacts compatible with the active stream setting instead of hard-crashing the generator
- Blockers found:
  - the fresh run remained in a long `encoding` phase, so I did not get a full first-frame proof before this deadline
- Recommendation / next step:
  - next wake should check whether the current run eventually reaches `streaming`, then decide whether to keep this resize compatibility path or force reprocessing when quality changes
  - commit pushed: `a31c819` (`Align precomputed scene tensors with selected stream quality`)

### Agent update — codex — 2026-04-19 06:35 EDT
- Focus:
  - InSpatio morning supervisor wake, quick live-state check, and low-risk continuity audit
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/docs/HANDOFF.md`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
  - local git history in `/home/pmello/Desktop/AI-apps-workspace/inspatio-world`
- Files changed:
  - none in the repo during this wake
- What I verified:
  - `http://127.0.0.1:7861/` returns `200`
  - websocket responds immediately with `active_scene`, `status=stopped`, `quality_sync`, and `timer_sync`
  - `/health` currently reports `ok=true`, `level=ok`, `stream_status=stopped`, and `launch_reason=operator_shutdown`
  - `interactive_io/status.json` is idle/stopped and current live state looks honest, not fake-streaming
  - the last `dit_stream.log` tail still points to a prior CUDA OOM at startup rather than a hidden current crash loop
  - local git is now `ahead 6`, with latest viewer-health honesty commits `9a3a081` and `c41ea02`
- What I fixed or improved:
  - no code change this wake; the improvement step was a real push/release audit to avoid duplicate investigation on the next wake
- Blockers found:
  - `git push origin main` still fails on this host with `fatal: could not read Username for 'https://github.com': No such device or address`
- Recommendation / next step:
  - keep the live viewer untouched while it is healthy and idle
  - when GitHub auth is available again, push the six queued validated commits so the repo matches the live local truth

### Agent update — codex — 2026-04-19 08:37 EDT
- Focus:
  - InSpatio morning supervisor wake, quick live-state check, and one viewer-health honesty fix
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/docs/HANDOFF.md`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/heavy_launch_state.json`
- Files changed:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/stream_viewer.py`
- What I verified:
  - `http://127.0.0.1:7861/` returns `200`
  - websocket still responds immediately with `active_scene`, `status=stopped`, `quality_sync`, and `timer_sync`
  - `interactive_io/status.json` still shows `stopped` with `previous_status=crashed`
  - the last `dit_stream.log` tail still points to a prior CUDA OOM at startup, not an active crash loop
  - current `heavy_launch_state.json` was for a different scene (`IMG_7643.mp4`) than the viewer's current active scene (`ScreenRecording_04-14-2026_01-17-32_1.mp4`)
  - after the patch and viewer restart, `/health` now truthfully preserves `previous_stream_status=crashed` instead of clearing it because of that stale mismatched stop record
- What I fixed or improved:
  - constrained crash-history clearing so stale operator-stop metadata from another scene can no longer erase the current scene's crash signal
  - restarted the lightweight viewer and revalidated `/health`
- Blockers found:
  - `git push origin main` still fails on this host with `fatal: could not read Username for 'https://github.com': No such device or address`
- Recommendation / next step:
  - keep the viewer live and idle unless there is a deliberate stream-start test
  - when GitHub auth is restored, push local commit `f8db7b5` plus the earlier queued validated commits

### Agent update — codex — 2026-04-19 09:05 EDT
- Focus:
  - InSpatio morning supervisor wake, live-state verification, and low-risk stability audit while the viewer is idle
- Files inspected:
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/docs/HANDOFF.md`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/status.json`
  - `/home/pmello/Desktop/AI-apps-workspace/inspatio-world/interactive_io/dit_stream.log`
  - local git history in `/home/pmello/Desktop/AI-apps-workspace/inspatio-world`
- Files changed:
  - none in the repo during this wake
- What I verified:
  - `http://127.0.0.1:7861/` returns `200`
  - websocket still responds immediately with `active_scene`, `status=stopped`, `quality_sync`, and `timer_sync`
  - `/health` currently reports `ok=true`, `level=ok`, `stream_status=stopped`, `previous_stream_status=crashed`, active scene `ScreenRecording_04-14-2026_01-17-32_1.mp4`, quality `scout`, and steps `2`
  - `interactive_io/status.json` is still `stopped`, with no fake streaming state
  - the current `dit_stream.log` tail still reflects an older CUDA OOM startup failure, not an active crash loop
  - local git remains `ahead 8`, with latest local viewer-honesty commits headed by `f8db7b5`
- What I fixed or improved:
  - no code change this wake; the concrete step was a real websocket plus health validation pass and a durable handoff refresh instead of forcing a noisy idle-state mutation
- Blockers found:
  - GitHub push remains blocked on this host until HTTPS auth is available again
- Recommendation / next step:
  - keep the viewer untouched while it is healthy and idle
  - next meaningful work should be either a deliberate small stream-start validation or restoring GitHub auth so the queued validated commits can be pushed

---

## Canonical artifact list
- Audit report:
  - `reports/imagine-studio-official-model-expansion-audit-2026-04-12.md`
  - `reports/imagine-studio-official-model-expansion-audit-2026-04-12.pdf`
- First-slice implementation report:
  - `reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.md`
  - `reports/imagine-studio-flux2-klein-slice-implementation-2026-04-12.pdf`
- Test evidence:
  - `reports/imagine-studio-flux2-klein-test-results-2026-04-12.json`

---

## One-line handoff
The project is in the right narrow shape: hidden FLUX.2 Klein is wired and baseline-safe, but the real next step is fixing the ComfyUI/Klein runtime mismatch so the hidden flagged route can complete once before any broader rollout is even considered.
