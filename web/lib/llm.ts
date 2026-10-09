// One OpenAI-compatible chat call with a fallback provider, wrapped in record-and-replay.
// Set LLM_BASE_URL / LLM_API_KEY / LLM_MODEL for the sponsor's or main model, and optionally
// FALLBACK_BASE_URL / FALLBACK_API_KEY / FALLBACK_MODEL (for example a local free-tier router).
import { withReplay, type Replayed } from "./replay";

type Provider = { base: string; key: string; model: string };

function providers(): Provider[] {
  const list: Provider[] = [];
  const { LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, FALLBACK_BASE_URL, FALLBACK_API_KEY, FALLBACK_MODEL } = process.env;
  if (LLM_BASE_URL && LLM_MODEL) list.push({ base: LLM_BASE_URL, key: LLM_API_KEY ?? "", model: LLM_MODEL });
  if (FALLBACK_BASE_URL && FALLBACK_MODEL)
    list.push({ base: FALLBACK_BASE_URL, key: FALLBACK_API_KEY ?? "", model: FALLBACK_MODEL });
  return list;
}

async function chatOnce(p: Provider, prompt: string, signal: AbortSignal): Promise<string> {
  const res = await fetch(`${p.base.replace(/\/$/, "")}/chat/completions`, {
    method: "POST",
    signal,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${p.key}` },
    body: JSON.stringify({ model: p.model, messages: [{ role: "user", content: prompt }] }),
  });
  if (!res.ok) throw new Error(`${p.model}: HTTP ${res.status}`);
  const json = await res.json();
  return json.choices?.[0]?.message?.content ?? "";
}

export async function chat(key: string, prompt: string): Promise<Replayed<string>> {
  return withReplay(key, async (signal) => {
    let lastError: unknown = new Error("no LLM provider configured");
    for (const p of providers()) {
      try {
        return await chatOnce(p, prompt, signal);
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError;
  });
}
