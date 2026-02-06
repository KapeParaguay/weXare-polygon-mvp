import { test, expect } from "@playwright/test";

test("worker page shows reputation", async ({ page }) => {
  await page.goto("/worker");
  await expect(page.getByText("Reputación")).toBeVisible();
});
