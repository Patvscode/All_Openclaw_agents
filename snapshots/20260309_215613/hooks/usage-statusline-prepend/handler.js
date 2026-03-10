import fs from "node:fs/promises";

const LOG_PATH = process.env.STATUSLINE_OPENCLAW_JSONL || "/home/pmello/.openclaw/workspace-codex/logs/usage/openclaw_status.jsonl";
const ROUTER_PATH = process.env.STATUSLINE_ROUTER_JSON || "/home/pmello/.openclaw/workspace-codex/logs/usage/budget_router_latest.json";
const DEBUG_LOG = process.env.STATUSLINE_DEBUG_LOG || "/home/pmello/.openclaw/logs/usage-statusline-hook.log";

async function readLastJsonLine(path) {
  try {
    const raw = await fs.readFile(path, "utf8");
    const lines = raw.trim().split(/\r?\n/).filter(Boolean);
    if (!lines.length) return null;
    return JSON.parse(lines[lines.length - 1]);
  } catch {
    return null;
  }
}

function parseDuration(ms) {
  if (!Number.isFinite(ms) || ms <= 0) return "?";
  const totalMin = Math.floor(ms / 60000);
  const d = Math.floor(totalMin / (60 * 24));
  const h = Math.floor((totalMin % (60 * 24)) / 60);
  const m = totalMin % 60;
  if (d > 0) return `${d}d${h}h`;
  return `${h}h${m}m`;
}

function normalizeMode(mode) {
  if (!mode || typeof mode !== "string") return "?";
  return mode;
}

function alreadyPrefixed(content) {
  return /^\[U\s+W:[^\]]+\]\s*/.test(content || "");
}

const handler = async (event, ctx) => {
  try {
    await fs.mkdir("/home/pmello/.openclaw/logs", { recursive: true });
    await fs.appendFile(DEBUG_LOG, JSON.stringify({ at: new Date().toISOString(), seen: true, keys: Object.keys(event || {}), channel: ctx?.channelId || null }) + "\n", "utf8");

    if (!event?.content || typeof event.content !== "string") return;
    if (alreadyPrefixed(event.content)) return;

    const oc = await readLastJsonLine(LOG_PATH);
    if (!oc) {
      return { content: `[U W:? D:? C:? M:conserve] ${event.content}` };
    }

    const metrics = oc.metrics || {};
    const sessions = (oc.sessions && oc.sessions.recent) || [];
    const primary = sessions.find((s) => s?.agentId === "codex") || sessions[0] || null;

    const remaining = Number(primary?.remainingTokens);
    const context = Number(primary?.contextTokens);
    const pct = Number.isFinite(remaining) && Number.isFinite(context) && context > 0
      ? Math.max(0, Math.min(100, Math.round(((context - remaining) / context) * 100)))
      : null;

    let mode = "conserve";
    try {
      const routerRaw = await fs.readFile(ROUTER_PATH, "utf8");
      const router = JSON.parse(routerRaw);
      mode = normalizeMode(router?.recommended_mode || mode);
    } catch {
      mode = pct !== null && pct > 70 ? "hard-conserve" : (pct !== null && pct >= 55 ? "conserve" : "normal");
    }

    const windowLeft = parseDuration(primary?.windowRemainingMs ?? null);
    const dayLeft = parseDuration(primary?.dayRemainingMs ?? null);
    const cTxt = pct === null ? "?" : `${pct}%`;

    const tag = `[U W:${windowLeft} D:${dayLeft} C:${cTxt} M:${mode}]`;
    return { content: `${tag} ${event.content}` };
  } catch {
    return;
  }
};

export default handler;
