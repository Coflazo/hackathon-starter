// Walks the demo path in a headless browser, records a video, and saves one screenshot per step.
// Writes proof/timeline.json with each step's start time, narration line and caption.
//   cd web && PROOF_DIR=../proof node ../tools/proof/record.mjs ../tools/proof/demo-path.json   (app running)
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";

// Resolve Playwright from the app folder this runs in (web/), not from tools/proof/.
const { chromium } = createRequire(`${process.cwd()}/package.json`)("@playwright/test");

const spec = JSON.parse(readFileSync(process.argv[2] || "tools/proof/demo-path.json", "utf8"));
const out = process.env.PROOF_DIR || "proof";
const [width, height] = spec.viewport || [1280, 720];
mkdirSync(`${out}/shots`, { recursive: true });
// narrate.py prepare writes the length of each spoken line, so each step is held until its line ends
const durations = existsSync(`${out}/durations.json`) ? JSON.parse(readFileSync(`${out}/durations.json`, "utf8")) : [];

const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || undefined });
const context = await browser.newContext({ viewport: { width, height } });
const page = await context.newPage();

// Chrome DevTools screencast instead of Playwright's recordVideo: its ffmpeg does not run on macOS 13.
// Frames arrive only when the page changes; mux.sh turns them into a video with the system ffmpeg.
mkdirSync(`${out}/frames`, { recursive: true });
const frames = [];
const cdp = await context.newCDPSession(page);
cdp.on("Page.screencastFrame", async ({ data, metadata, sessionId }) => {
  const file = `${out}/frames/${String(frames.length + 1).padStart(6, "0")}.jpg`;
  writeFileSync(file, Buffer.from(data, "base64"));
  frames.push({ file, at: Date.now() });
  await cdp.send("Page.screencastFrameAck", { sessionId }).catch(() => {});
});
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 85, maxWidth: width, maxHeight: height });
const t0 = Date.now();
const timeline = [];

for (const [i, s] of spec.steps.entries()) {
  const start = (Date.now() - t0) / 1000;
  if (s.action === "goto") await page.goto(new URL(s.url, spec.base_url).toString());
  if (s.action === "fill") await page.getByLabel(s.label).fill(s.value);
  if (s.action === "click") await page.getByRole(s.role, { name: s.name }).click();
  if (s.wait_for_testid) await page.getByTestId(s.wait_for_testid).waitFor({ timeout: 30_000 });
  if (s.action === "pause") await page.waitForTimeout(s.ms);
  const said = durations[i] ? durations[i] * 1000 + 400 : 0;
  const spent = Date.now() - t0 - start * 1000;
  await page.waitForTimeout(Math.max((s.hold_ms ?? 1200) - spent, said - spent, 300));
  await page.screenshot({ path: `${out}/shots/${String(i + 1).padStart(2, "0")}.png` });
  timeline.push({ step: i + 1, start, end: (Date.now() - t0) / 1000, say: s.say, caption: s.caption, wow: !!s.wow });
}

await cdp.send("Page.stopScreencast");
const tEnd = Date.now();
await context.close();
await browser.close();
// ffmpeg concat list: each frame lasts until the next one (page changes are when frames arrive)
const list = frames.map((f, i) => {
  const until = i + 1 < frames.length ? frames[i + 1].at : tEnd;
  const startAt = i === 0 ? t0 : f.at;
  return `file '${f.file.split("/").pop()}'\nduration ${Math.max((until - startAt) / 1000, 0.04).toFixed(3)}`;
});
writeFileSync(`${out}/frames/frames.txt`, `${list.join("\n")}\nfile '${frames.at(-1).file.split("/").pop()}'\n`);
writeFileSync(`${out}/timeline.json`, JSON.stringify({ sponsors: spec.sponsors || [], steps: timeline }, null, 2));
console.log(`recorded ${timeline.length} steps, ${frames.length} frames -> ${out}/frames/, ${out}/shots/, ${out}/timeline.json`);
