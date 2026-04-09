import { readFileSync, appendFileSync, mkdirSync } from "node:fs";
import { exec } from "node:child_process";

const GEMMA_WORKSPACE = "/home/pmello/.openclaw/workspace-gemma";
const SCRATCHPAD = `${GEMMA_WORKSPACE}/SCRATCHPAD.md`;
const RESUME = `${GEMMA_WORKSPACE}/RESUME.md`;
const LOG_PATH = "/home/pmello/.openclaw/logs/gemma-auto-continue.log";
const MAX_CONTINUATIONS = 10;
const CONTINUE_DELAY_MS = 5000;

function log(msg: string) {
  try {
    mkdirSync("/home/pmello/.openclaw/logs", { recursive: true });
    appendFileSync(LOG_PATH, `${new Date().toISOString()} ${msg}\n`);
  } catch {}
}

function readFile(path: string): string {
  try { return readFileSync(path, "utf-8"); } catch { return ""; }
}

function parseDecision(scratchpad: string): { shouldContinue: boolean; nextStep: string } {
  const result = { shouldContinue: false, nextStep: "" };
  const decisionMatch = scratchpad.match(/## Decision[\s\S]*?(?=## |$)/i);
  if (!decisionMatch) return result;
  const decision = decisionMatch[0];
  
  if (/do i need to continue\??\s*:?\s*no/i.test(decision) || /\bn\/a\b/i.test(decision)) return result;
  if (/do i need to continue\??\s*:?\s*yes/i.test(decision)) {
    result.shouldContinue = true;
    const m = decision.match(/(?:next step|what's the next step)[?:\s]*(.+?)(?:\n|$)/i);
    if (m) result.nextStep = m[1].trim().replace(/^[- ]+/, "");
  }
  return result;
}

function getCurrentStep(resume: string): number {
  const m = resume.match(/(?:step|continuations?)[:\s]*(\d+)\s*\/\s*\d+/i);
  return m ? parseInt(m[1], 10) : 0;
}

// Log EVERYTHING to debug
const handler = async (event: any) => {
  // Log every call regardless
  log(`EVENT: type=${event?.type} action=${event?.action} sessionKey=${event?.sessionKey} keys=${Object.keys(event || {}).join(",")}`);
  
  if (event?.context) {
    log(`CONTEXT: keys=${Object.keys(event.context).join(",")} to=${event.context?.to} content_len=${(event.context?.content || "").length}`);
  }

  // Extract agent from sessionKey
  const sk = event?.sessionKey || "";
  const parts = sk.split(":");
  const agent = parts.length >= 2 && parts[0] === "agent" ? parts[1] : null;
  
  log(`AGENT: ${agent}`);
  
  if (agent !== "gemma") {
    log("SKIP: not gemma");
    return;
  }

  const content = event?.context?.content || "";
  if (content === "HEARTBEAT_OK" || content === "NO_REPLY") {
    log("SKIP: heartbeat/noreply");
    return;
  }

  // Check scratchpad
  const scratchpad = readFile(SCRATCHPAD);
  if (!scratchpad) { log("SKIP: no scratchpad"); return; }

  const decision = parseDecision(scratchpad);
  log(`DECISION: continue=${decision.shouldContinue} next="${decision.nextStep}"`);

  if (!decision.shouldContinue) { log("SKIP: scratchpad says done"); return; }

  const resume = readFile(RESUME);
  const step = getCurrentStep(resume);
  if (step >= MAX_CONTINUATIONS) { log(`BLOCKED: max steps ${step}/${MAX_CONTINUATIONS}`); return; }

  const nextStep = decision.nextStep || "Continue from SCRATCHPAD.md and RESUME.md context.";
  const message = `Auto-continue (step ${step + 1}/${MAX_CONTINUATIONS}): ${nextStep}`;
  
  log(`WILL CONTINUE in ${CONTINUE_DELAY_MS}ms: "${message}"`);

  await new Promise(r => setTimeout(r, CONTINUE_DELAY_MS));

  exec(
    `openclaw agent --agent gemma --message ${JSON.stringify(message)} --timeout 300`,
    { timeout: 310000 },
    (err) => { if (err) log(`TRIGGER_ERR: ${err.message}`); else log("TRIGGER_OK"); }
  );
  log("DISPATCHED");
};

export default handler;
