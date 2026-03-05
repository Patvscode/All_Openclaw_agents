# LEVERAGE_BACKLOG.md

Prioritized initiatives to increase capability while reducing Codex spend.

Scoring
- Impact (1-5): expected quality/capability gain
- Savings (1-5): expected Codex usage reduction
- Effort (1-5): implementation difficulty (lower is better)
- Reliability (1-5): expected stability/ops gain
- Revenue Option (1-5): potential to create external/internal monetary value
- Priority Score = (Impact + Savings + Reliability + Revenue Option) - Effort

## Top Priorities (Now)

| Rank | Initiative | Impact | Savings | Effort | Reliability | Revenue Option | Priority Score | Why now |
|---:|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Budget-aware model router (auto conserve/normal/sprint + hard 70% cap policy) | 5 | 5 | 2 | 5 | 3 | 16 | Immediate control of burn-rate and sustainable runway |
| 2 | Local-first task classifier + escalation gates | 5 | 5 | 3 | 4 | 3 | 14 | Stops unnecessary Codex calls and enforces ROI usage |
| 3 | Context bloat prevention layer (summary-only outputs, artifact links, preflight required) | 4 | 5 | 2 | 4 | 2 | 13 | Biggest direct token savings by default behavior |
| 4 | Automated eval harness for local models by task family | 5 | 4 | 3 | 5 | 4 | 15 | Data-backed routing + continuous quality improvement |
| 5 | Failure-point sentinel + anomaly alerts | 4 | 3 | 2 | 5 | 2 | 12 | Faster recovery and less expensive firefighting |

## Next Wave (2-6 weeks)

| Initiative | Goal | KPI |
|---|---|---|
| Local coding pipeline hardening (qwen3-coder + lint/test wrappers) | Increase local completion rate for coding tasks | % tasks completed locally without Codex |
| Prompt/policy library for recurring workflows | Reuse proven prompts and avoid rework | Mean iterations per task |
| Retrieval memory quality upgrade (chunking + tags + freshness) | Better recall, less duplicate reasoning | Repeat-task token reduction |
| Parallel local workers with queue limits | Throughput without runaway context | Tasks/day with stable error rate |
| Cost-aware triage dashboards | Faster spend decisions | Daily burn variance reduction |

## Revenue/Value Track (optional but strategic)

1. Package agent-ops toolkit as reusable internal automation bundle.
2. Offer setup/optimization service for local model routing + telemetry.
3. Build repeatable “ops intelligence reports” from logs/usage data.
4. Productize reliability guardrails (preflight + failure sentinel + routing).

## Decision Method (when to spend Codex)

Use Codex only if one of these is true:
- High risk/correctness critical
- High complexity not solved by local path after 1-2 attempts
- High leverage (build once, save repeatedly)
- Urgent unblock with meaningful downstream value

Otherwise default to local-first and keep Codex in reserve.

## KPIs to Track Weekly

- Codex share of total task volume (%)
- Codex share of high-value tasks (%)
- Local completion rate (%)
- Escalation rate local -> Codex (%)
- Mean tokens per completed task
- Context overflow / compaction incidents
- Reliability incidents and MTTR

## Milestone Plan

### Milestone A (this week)
- Implement budget-aware router with 70% policy target
- Enforce summary-only by default for heavy tool outputs
- Add KPI extraction to nightly usage summary

### Milestone B (next week)
- Add local eval harness for coding/reasoning/vision tasks
- Add automatic route recommendation with confidence scores

### Milestone C (month)
- Demonstrate sustained lower burn-rate with equal or better task quality
- Publish monthly efficiency report and reinvestment options

## Future Project Note — Real-Time Jess Voice Loop (Deferred)

Status: **Deferred / planned** (not implementing now)

Goal:
- Add near real-time, interruption-capable voice conversation with Jess (full-duplex feel).

Target capabilities:
- Streaming STT (partial transcripts while user speaks)
- Streaming LLM response generation
- Streaming TTS playback
- Barge-in/interrupt handling (user speech immediately stops TTS)
- Low-latency turn-taking (~sub-second perceived response start)

Suggested architecture:
1. Local voice gateway service (always-on process, later)
2. VAD + mic capture + partial transcript pipeline
3. Jess inference stream endpoint integration
4. TTS stream + playback controller
5. Interrupt controller and conversation state manager

Milestones (future):
- M1: Prototype local loop with fake/CLI input + streamed output
- M2: Add barge-in and cancellation semantics
- M3: Optimize latency budget and buffering
- M4: Reliability hardening + watchdog + restart policy
- M5: Optional Telegram voice bridge fallback

Constraints/notes:
- Keep this out of current stabilization scope for now.
- Revisit after Jess stability gate is met.

### Linked Plan
- Detailed implementation plan: `FUTURE_VOICE_DASHBOARD_PLAN.md`

## Future Project Note — Jess Fast Chat Mode

Problem observed:
- Real Telegram latency can reach 30s to minutes due to very large carried prompt context.

Planned fix:
- Add a "Fast Chat Mode" profile for Jess with earlier compaction/summarization, tighter context hygiene, and periodic rollover guidance.
- Keep large context capability available, but default interactive chat path optimized for responsiveness.
