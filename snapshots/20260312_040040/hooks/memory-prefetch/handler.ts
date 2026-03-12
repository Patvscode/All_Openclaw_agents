/**
 * Memory Pre-Fetch — searches RAG for relevant context before every prompt.
 * Gives every agent an effectively infinite memory window.
 */

const MEMQUERY_URL = "http://localhost:8102/query";
const SCORE_THRESHOLD = 0.68;
const MAX_SNIPPETS = 4;
const MAX_SNIPPET_CHARS = 600;
const QUERY_TIMEOUT_MS = 2000;
const MIN_PROMPT_LENGTH = 12;

const SKIP_PATTERNS = [
  /^(HEARTBEAT|heartbeat)/,
  /^(NO_REPLY|HEARTBEAT_OK)/,
  /^\/(new|reset|status|help|model)/,
  /^(hi|hey|hello|thanks|ok|yes|no|sure|yep|nah|bye)\s*[.!]?$/i,
];

const handler = async (
  event: { prompt: string; messages?: unknown[] },
  ctx: { agentId?: string; trigger?: string }
) => {
  try {
    const prompt = event?.prompt?.trim();
    if (!prompt || prompt.length < MIN_PROMPT_LENGTH) return;
    if (ctx?.trigger === "heartbeat" || ctx?.trigger === "cron") return;
    if (SKIP_PATTERNS.some((p) => p.test(prompt))) return;
    if (prompt.startsWith("[media attached") || prompt.startsWith("<<SYSTEM")) return;

    // Clean prompt for search
    let searchText = prompt;
    const convInfoIdx = searchText.indexOf("Conversation info (untrusted");
    if (convInfoIdx > 0) searchText = searchText.substring(0, convInfoIdx).trim();
    const mediaIdx = searchText.indexOf("[media attached");
    if (mediaIdx >= 0) searchText = searchText.substring(0, mediaIdx).trim();
    if (searchText.length < MIN_PROMPT_LENGTH) return;
    if (searchText.length > 500) searchText = searchText.substring(0, 500);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), QUERY_TIMEOUT_MS);

    const resp = await fetch(MEMQUERY_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: searchText, top_k: MAX_SNIPPETS + 2 }),
      signal: controller.signal,
    });
    clearTimeout(timeout);
    if (!resp.ok) return;

    const data = (await resp.json()) as { results?: { text: string; source: string; score: number }[] };
    const results = data?.results;
    if (!results?.length) return;

    // Filter, score, dedupe
    const seen = new Set<string>();
    const relevant: typeof results = [];
    for (const r of results) {
      if (r.score < SCORE_THRESHOLD) continue;
      const key = r.text?.substring(0, 80);
      if (seen.has(key)) continue;
      seen.add(key);
      relevant.push(r);
      if (relevant.length >= MAX_SNIPPETS) break;
    }
    if (!relevant.length) return;

    const snippets = relevant.map((r) => {
      const text = r.text.length > MAX_SNIPPET_CHARS
        ? r.text.substring(0, MAX_SNIPPET_CHARS) + "…"
        : r.text;
      const src = r.source ? ` [${r.source.split("/").pop()}]` : "";
      return `• ${text}${src}`;
    });

    return {
      prependContext: [
        "## 🧠 Auto-Retrieved Context (Memory Sidecar)",
        "This was automatically retrieved from the ARC memory system — not typed by the user.",
        "Sourced from past conversations, research papers, and agent memory. Use if relevant, ignore if not.",
        "",
        ...snippets,
      ].join("\n"),
    };
  } catch {
    return;
  }
};

export default handler;
