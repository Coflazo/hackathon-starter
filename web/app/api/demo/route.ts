import { chat } from "@/lib/llm";

// ponytail: in-memory per-IP limit, per server instance; use a shared store (Upstash, Vercel KV)
// if the demo is public for long. It stops a stray visitor from draining the LLM quota before judging.
const WINDOW_MS = 60_000;
const MAX_PER_WINDOW = Number(process.env.DEMO_RATE_LIMIT ?? 20);
const hits = new Map<string, number[]>();

function limited(ip: string): boolean {
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > MAX_PER_WINDOW;
}

export async function POST(request: Request) {
  const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
  if (limited(ip)) return Response.json({ error: "Too many requests. Try again in a minute." }, { status: 429 });
  const { input } = (await request.json().catch(() => ({}))) as { input?: string };
  if (!input || input.length > 2000) {
    return Response.json({ error: "Send an input of 1 to 2000 characters." }, { status: 400 });
  }
  try {
    const { data, source } = await chat("demo", `Answer in two sentences: ${input}`);
    return Response.json({ output: data, source });
  } catch (err) {
    console.error("demo route:", err); // details stay in the server log
    return Response.json({ error: "The demo service is unavailable right now." }, { status: 502 });
  }
}
