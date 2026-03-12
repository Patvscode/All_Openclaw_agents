/**
 * Knowledge RAG Inject — auto-injects relevant internal knowledge into agent context.
 * 
 * Hook: before_prompt_build
 * Source: Memory Concierge (port 8102)
 */

const MEMQUERY_URL = "http://localhost:8102/query";
const SCORE_THRESHOLD = 0.72;
const MAX_SNIPPETS = 3;
const MAX_SNIPPET_CHARS = 800;
const QUERY_TIMEOUT_MS = 1500; // Hard timeout — don't delay the agent
const MIN_PROMPT_LENGTH = 12; // Skip very short messages

// Skip patterns — don't waste RAG queries on these
const SKIP_PATTERNS = [
  /^(HEARTBEAT|heartbeat)/,
  /^(NO_REPLY|HEARTBEAT_OK)/,
  /^\/(new|reset|status|help|model)/,
  /^(hi|hey|hello|thanks|ok|yes|no|sure|yep|nah|bye)\s*[.!]?$/i,
];

interface QueryResult {
  text: string;
  source: string;
  score: number;
}

const handler = async (
  event: { prompt: string; messages?: unknown[] },
  ctx: { agentId?: string; trigger?: string }
) => {
  try {
    const prompt = event?.prompt?.trim();
    if (!prompt || prompt.length < MIN_PROMPT_LENGTH) return;

    // Skip heartbeats and system triggers
    if (ctx?.trigger === "heartbeat" || ctx?.trigger === "cron") return;

    // Skip trivial messages
    if (SKIP_PATTERNS.some((p) => p.test(prompt))) return;

    // Skip if prompt is mostly media/file references (not searchable)
    if (prompt.startsWith("[media attached") || prompt.startsWith("<<SYSTEM")) return;

    // Extract the actual question/topic from the prompt
    // Strip metadata blocks that Telegram/Discord might inject
    let searchText = prompt;
    const convInfoIdx = searchText.indexOf("Conversation info (untrusted");
    if (convInfoIdx > 0) searchText = searchText.substring(0, convInfoIdx).trim();
    const mediaIdx = searchText.indexOf("[media attached");
    if (mediaIdx >= 0) searchText = searchText.substring(0, mediaIdx).trim();
    
    if (searchText.length < MIN_PROMPT_LENGTH) return;

    // Truncate long prompts for search efficiency
    if (searchText.length > 500) searchText = searchText.substring(0, 500);

    // Query Memory Concierge
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), QUERY_TIMEOUT_MS);

    const resp = await fetch(MEMQUERY_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        q: searchText,
        top_k: MAX_SNIPPETS + 2, // Fetch a couple extra to filter
      }),
      signal: controller.signal,
    });

    clearTimeout(timeout);

    if (!resp.ok) return;

    const data = (await resp.json()) as {
      results?: QueryResult[];
      answer?: string;
    };

    const results = data?.results;
    if (!results || !Array.isArray(results) || results.length === 0) return;

    // Filter by score and deduplicate
    const seen = new Set<string>();
    const relevant: QueryResult[] = [];
    for (const r of results) {
      if (r.score < SCORE_THRESHOLD) continue;
      // Dedupe by first 100 chars
      const key = r.text?.substring(0, 100);
      if (seen.has(key)) continue;
      seen.add(key);
      relevant.push(r);
      if (relevant.length >= MAX_SNIPPETS) break;
    }

    if (relevant.length === 0) return;

    // Build context block
    const snippets = relevant.map((r) => {
      const text =
        r.text.length > MAX_SNIPPET_CHARS
          ? r.text.substring(0, MAX_SNIPPET_CHARS) + "…"
          : r.text;
      const src = r.source
        ? ` [${r.source.split("/").pop()}]`
        : "";
      return `• ${text}${src}`;
    });

    const context = [
      "## Internal Knowledge (auto-retrieved from RAG store)",
      "The following may be relevant to the user's message. Use if helpful, ignore if not.",
      "",
      ...snippets,
    ].join("\n");

    return { prependContext: context };
  } catch {
    // Silent fail — don't block the agent if RAG is down
    return;
  }
};

export default handler;
