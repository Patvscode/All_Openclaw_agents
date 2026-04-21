# Model Routing Incident — Post-Mortem

**Date:** 2026-04-20
**Impact:** `main` silently running on Gemma 4 E2B fallback instead of Opus, codex silently running on Gemma 26B labeled as Qwen, q35/Jess similarly mislabeled. Many turns over ~36h produced outputs that looked like they came from Opus but didn't.
**Resolved:** 2026-04-20 ~14:20 EDT

## Timeline

- **Sat Apr 18, 16:33 EDT** — Pat asks: "how do we properly add opus 4.7 to our model list"
- **Sat Apr 18, 16:41 EDT** — I told Pat that `/model anthropic/claude-opus-4-7` on a chat would "just work" with the existing Anthropic provider. I was wrong — the provider catalog had no entry for 4-7, only a bare allowlist stub. Session state pinned the model ID anyway.
- **Sun Apr 19 afternoon** — noticed the stale override. I called it "cosmetic" because the old fallback (opus-4-6) was still working. This was the wrong call; it masked a live config gap.
- **Sun Apr 19 ~19:00 EDT** — Anthropic brief outage. Fallback chain added to `main`: `[gpt-4.1-mini, gpt-4.1-nano, qwen3.5-35b]`. Reasonable at the time.
- **Sun Apr 19 ~20:40 EDT → Mon Apr 20 ~00:40 EDT** — between `openclaw.json.bak.4` and `bak.3`, `main`'s primary got flipped from `opus-4-6` → `opus-4-7`, and the fallbacks got rewritten to `[local/gemma-4-26b-a4b-it, local/qwen3.6-35b-a3b, local/gemma-4-e2b-it]`. Source of the edit not pinpointed (likely codex-driven cleanup or a cron-triggered agent edit).
- **Mon Apr 20, 00:40 EDT** — `openclaw.json.bak-main-fallback-20260420-0040` taken. State now looks broken at steady state but failures are hidden by silent fallback.
- **Mon Apr 20 ~12:35 EDT** — codex `gpt-5.4` quota exceeded; codex got an identical misleading `local/*` fallback chain.
- **Mon Apr 20 13:16 EDT** — Pat + another agent produce `OPENCLAW_AGENT_MODEL_REPORT.md`. Opus 4.7 provider catalog entry added at 13:48 EDT.
- **Mon Apr 20 14:20 EDT** — cleanup committed. Codex fallback set to `anthropic/claude-opus-4-6`. `~/.openclaw` initialized as a git repo for audit trail.

## Root Cause (single sentence)

I told Pat that pinning a session to `anthropic/claude-opus-4-7` would work without adding a real provider-catalog entry for the model. The fallback-on-unknown-model path then silently routed every affected turn to whatever "local" mapped to — which kept changing as we renamed providers — making wrong answers look correct.

## Why it looked "out of nowhere"

- Fallback was silent. `main` kept replying; nothing logged to Telegram.
- The "local" provider catalog advertises 8 model IDs as a menu, but only 1 is physically loaded on :18080 at any time (this is how `swap-model` works). So `local/gemma-4-e2b-it` as a label is *valid* but routes to whatever's loaded — in this case Gemma 26B.
- Two different quota/auth problems (Anthropic outage, then codex 5.4 quota) caused us to add fallback chains as a defensive move, but they were built on the already-broken "local/*" label soup.
- No git history on `~/.openclaw`, so nobody could see what changed between working and broken states.

## Fixes Applied

1. Added full Anthropic provider catalog entry for `claude-opus-4-7` (contextWindow, reasoning flag, costs, input types). Verified `models.list` returns full metadata now.
2. `main`: primary=`anthropic/claude-opus-4-7`, fallbacks=`[]`. Fail loud, not silent.
3. `codex`: primary=`codex/gpt-5.4`, fallbacks=`[anthropic/claude-opus-4-6]`. Removed misleading `local/*` chain.
4. `~/.openclaw` is now a git repo. `openclaw.json` and `agents/*/agent/models.json` are tracked.
5. This file + the lesson entry in `LESSONS.md`.

## What's Still Open

- **Codex quota** on `gpt-5.4` still exceeded; codex will trip over to Opus 4.6 until that's restored.
- **q35/Jess naming mismatch:** config says `local/qwen3.6-35b-a3b`, :18080 is physically Gemma 26B. Waiting on Pat to decide: either run `swap-model qwen36` (takes 18080 down ~3 min, affects other agents) or rename Jess to match reality.
- **Provider catalog cleanup for `local`:** the 8-model menu is intentional (swap-model), but the agent-facing UX is deceiving. Consider either: (a) add a runtime check that compares configured model ID vs what :18080 actually serves, or (b) only advertise the *currently loaded* model in the local provider catalog and update it when swap-model runs.

## Lesson

**Never pin a session to a model ID before its provider has a full catalog entry.** OpenClaw's "Unknown model" fallback path is silent by default — it will mask the problem forever. When adding a new model, always: (1) full provider catalog entry, (2) verify via `clawdbot gateway call models.list`, (3) THEN allow any session to use it.

## Lesson 2

**Never use `local/*` model IDs as fallbacks unless the catalog matches what's physically loaded.** The `local` provider at :18080 is a menu for `swap-model`, not a reflection of what's running. Either keep its catalog dynamically synced to the loaded model, or don't use it in fallback chains.
