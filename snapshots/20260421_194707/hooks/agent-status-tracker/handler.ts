import { writeFileSync, mkdirSync } from "fs";
import { join } from "path";

const STATUS_DIR = "/tmp/agent-status";

function writeStatus(agent: string, status: string, task: string, detail: string = "") {
  try {
    mkdirSync(STATUS_DIR, { recursive: true });
    const data = {
      agent,
      status,
      task,
      detail,
      timestamp: new Date().toISOString(),
      epoch: Math.floor(Date.now() / 1000),
    };
    writeFileSync(join(STATUS_DIR, `${agent}.json`), JSON.stringify(data, null, 2));
  } catch {
    // Silent fail — status is non-critical
  }
}

function extractAgent(sessionKey: string | undefined): string | null {
  // Session keys look like "agent:main:main" or "agent:q35:telegram:123"
  if (!sessionKey) return null;
  const parts = sessionKey.split(":");
  if (parts.length >= 2 && parts[0] === "agent") {
    return parts[1]; // The agent name
  }
  return null;
}

function truncate(s: string, max: number): string {
  if (!s) return "";
  return s.length > max ? s.slice(0, max) + "…" : s;
}

const handler = async (event: any) => {
  const agent = extractAgent(event.sessionKey);
  if (!agent) return;

  if (event.type === "message" && event.action === "received") {
    const from = event.context?.from || event.context?.metadata?.senderName || "unknown";
    const channel = event.context?.channelId || "unknown";
    const snippet = truncate(event.context?.content || "", 80);
    writeStatus(
      agent,
      "active",
      `Processing message from ${from}`,
      `[${channel}] ${snippet}`
    );
  }

  if (event.type === "message" && event.action === "sent") {
    const snippet = truncate(event.context?.content || "", 100);
    const to = event.context?.to || "";
    writeStatus(
      agent,
      "idle",
      snippet ? `Responded: ${truncate(snippet, 60)}` : "Response sent",
      to ? `to ${to}` : ""
    );
  }
};

export default handler;
