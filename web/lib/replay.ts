// Record-and-replay for every external call, so a demo survives bad venue Wi-Fi and dead APIs.
//
//   DEMO_MODE=1  -> always answer from fixtures/<key>.json (identical demo every run)
//   RECORD=1     -> call live, save the answer to fixtures/<key>.json
//   otherwise    -> call live with a timeout; on failure fall back to the fixture if one exists
import { promises as fs } from "node:fs";
import path from "node:path";

const FIXTURES = path.join(process.cwd(), "fixtures");

export class ReplayError extends Error {}

export type Replayed<T> = { data: T; source: "live" | "fixture" };

function checkKey(key: string): void {
  // Keys are code constants; refuse anything that could walk out of fixtures/.
  if (!/^[A-Za-z0-9_-]{1,64}$/.test(key)) throw new ReplayError(`invalid fixture key: ${key}`);
}

async function readFixture<T>(key: string): Promise<T | null> {
  try {
    return JSON.parse(await fs.readFile(path.join(FIXTURES, `${key}.json`), "utf8")) as T;
  } catch {
    return null;
  }
}

export async function withReplay<T>(
  key: string,
  live: (signal: AbortSignal) => Promise<T>,
  timeoutMs = 8000,
): Promise<Replayed<T>> {
  checkKey(key);
  if (process.env.DEMO_MODE === "1") {
    const data = await readFixture<T>(key);
    if (data === null) throw new ReplayError(`DEMO_MODE is on but fixtures/${key}.json is missing`);
    return { data, source: "fixture" };
  }
  try {
    const data = await live(AbortSignal.timeout(timeoutMs));
    // Never record in production: a visitor's input would overwrite the judges' demo fixture.
    if (process.env.RECORD === "1" && process.env.NODE_ENV !== "production") {
      await fs.mkdir(FIXTURES, { recursive: true });
      await fs.writeFile(path.join(FIXTURES, `${key}.json`), JSON.stringify(data, null, 2));
    }
    return { data, source: "live" };
  } catch (err) {
    const data = await readFixture<T>(key);
    if (data !== null) return { data, source: "fixture" };
    throw new ReplayError(`live call failed and no fixture for ${key}: ${String(err)}`);
  }
}
