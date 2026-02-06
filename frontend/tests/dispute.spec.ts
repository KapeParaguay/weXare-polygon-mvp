import { test, expect } from "@playwright/test";

test("dispute page renders vote form", async ({ page }) => {
  await page.goto("/judge/disputes/1");
  await expect(page.getByText("Disputa")).toBeVisible();
  await expect(page.getByText("Votar")).toBeVisible();
});
