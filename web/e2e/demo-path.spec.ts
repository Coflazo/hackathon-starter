import { expect, test } from "@playwright/test";

// The one test that must never be cut: it walks the demo path end to end.
test("demo path answers from the fixture in DEMO_MODE", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Demo path" })).toBeVisible();
  await page.getByLabel("Input").fill("What does this app do?");
  await page.getByRole("button", { name: "Run" }).click();
  await expect(page.getByTestId("output")).toContainText("Sample answer");
  await expect(page.getByText("Sample data")).toBeVisible();
});

test("empty input is rejected with a clear error", async ({ request }) => {
  const res = await request.post("/api/demo", { data: { input: "" } });
  expect(res.status()).toBe(400);
});
