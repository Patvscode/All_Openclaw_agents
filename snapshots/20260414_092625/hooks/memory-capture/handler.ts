/**
 * Memory Capture — extracts key facts from every exchange and writes to RAG.
 *
 * Runs AFTER the assistant response is sent (llm_output event).
 * Uses qwen3.5:0.8b for extraction (~200-500ms, async, non-blocking).
 * Writes extracted facts to Memory Concierge with timestamps.
 */

const OLLAMA_URL = "http://127.0.0.1:11434/api/generate";
const MEMINGEST_URL = "http://localhost:8102/ingest";
const EXTRACT_MODEL = "qwen3.5:0.8b";
const EXTRACT_TIMEOUT_MS = 8000;

import { appendFileSync, mkdirSync } from "node:fs";

const LOG_PATH = "/home/pmello/.openclaw/logs/memory-capture.log";

function log(msg: string) {
  try {
    mkdirSync("/home/pmello/.openclaw/logs", { recursive: true });
    appendFileSync(LOG_PATH, `${new Date().toISOString()} ${msg}\n`);
  } catch {}
}

const handler = async (
  event: {
    prompt: string;
    assistantTexts: string[];
    model?: string;
    sessionId?: string;
    runId?: string;
  },
  ctx: { agentId?: string; trigger?: string; sessionKey?: string }
) => {
  log(`FIRED: agent=${ctx?.agentId} trigger=${ctx?.trigger} prompt_len=${event?.prompt?.length} assist_len=${event?.assistantTexts?.join("")?.length}`);
  // Fire-and-forget — never block the agent
  captureMemory(event, ctx).catch((e) => log(`ERROR: ${e}`));
};

async function captureMemory(
  event: {
    prompt: string;
    assistantTexts: string[];
    model?: string;
    sessionId?: string;
  },
  ctx: { agentId?: string; trigger?: string; sessionKey?: string }
) {
  try {
    // Skip heartbeats, cron, system triggers
    if (ctx?.trigger === "heartbeat" || ctx?.trigger === "cron") return;

    const userMsg = event.prompt?.trim() || "";
    const assistantMsg = (event.assistantTexts || []).join("\n").trim();

    // Skip trivial exchanges
    if (userMsg.length < 20 && assistantMsg.length < 50) return;
    if (assistantMsg === "NO_REPLY" || assistantMsg === "HEARTBEAT_OK") return;

    // Clean user message — strip Telegram/Discord metadata
    let cleanUser = userMsg;
    const convIdx = cleanUser.indexOf("Conversation info (untrusted");
    if (convIdx > 0) cleanUser = cleanUser.substring(0, convIdx).trim();
    // If it starts with media tags and has text after, keep the text
    const senderIdx = cleanUser.indexOf("Sender (untrusted");
    if (senderIdx > 0) cleanUser = cleanUser.substring(0, senderIdx).trim();

    // Skip if mostly metadata/system
    if (cleanUser.length < 15) return;

    // Truncate for extraction prompt
    const userSnippet = cleanUser.length > 600 ? cleanUser.substring(0, 600) + "…" : cleanUser;
    const assistSnippet = assistantMsg.length > 600 ? assistantMsg.substring(0, 600) + "…" : assistantMsg;

    // Ask 0.8b to extract key facts
    const extractPrompt = `<|im_start|>system
You extract key facts from conversations. Return ONLY a short bullet list of facts, decisions, preferences, or important info worth remembering. If nothing important, return exactly "NONE".<|im_end|>
<|im_start|>user
Human said: ${userSnippet}

Agent responded: ${assistSnippet}

Extract key facts worth remembering:<|im_end|>
<|im_start|>assistant
`;

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), EXTRACT_TIMEOUT_MS);

    const resp = await fetch(OLLAMA_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: EXTRACT_MODEL,
        prompt: extractPrompt,
        raw: true,
        stream: false,
        options: { num_predict: 200, temperature: 0.1, stop: ["<|im_end|>"] },
      }),
      signal: controller.signal,
    });
    clearTimeout(timeout);

    if (!resp.ok) return;
    const data = (await resp.json()) as { response?: string };
    const extracted = data?.response?.trim() || "";

    log(`EXTRACTED (${ctx?.agentId}): ${extracted.substring(0, 100)}`);

    // Skip if nothing worth remembering
    if (!extracted || extracted === "NONE" || extracted.length < 10) {
      log(`SKIPPED: trivial extraction`);
      return;
    }

    // Build memory chunk with rich metadata
    const now = new Date();
    const agent = ctx?.agentId || "unknown";
    const model = event.model || "unknown";
    const dateStr = now.toISOString().split("T")[0];
    const timeStr = now.toISOString().split("T")[1]?.split(".")[0] || "";

    const memoryChunk = [
      `[${dateStr} ${timeStr}] [agent:${agent}] [model:${model}]`,
      extracted,
    ].join("\n");

    log(`INGESTING: ${memoryChunk.substring(0, 100)}`);

    // Ingest into RAG store
    await fetch(MEMINGEST_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: memoryChunk,
        source: `conversation/${agent}/${dateStr}`,
        source_type: "conversation-extract",
      }),
      signal: AbortSignal.timeout(3000),
    }).catch(() => {});

  } catch {
    // Silent fail — never block the agent
  }
}

export default handler;
