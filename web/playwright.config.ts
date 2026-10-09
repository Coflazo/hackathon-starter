import { defineConfig } from "@playwright/test";

// The smoke test always runs the demo path in DEMO_MODE, so it passes offline and in CI.
// Locally, PLAYWRIGHT_CHANNEL=chrome reuses the installed Google Chrome instead of downloading one.
export default defineConfig({
  testDir: "e2e",
  timeout: 60_000,
  use: { baseURL: "http://127.0.0.1:3100", channel: process.env.PLAYWRIGHT_CHANNEL || undefined },
  webServer: {
    command: "npm run build && npx next start -p 3100",
    url: "http://127.0.0.1:3100",
    env: { DEMO_MODE: "1" },
    timeout: 240_000,
    reuseExistingServer: false,
  },
});
