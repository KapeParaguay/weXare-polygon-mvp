import { test, expect } from "@playwright/test";

test("judge page shows deadline", async ({ page }) => {
  await page.goto("/judge");
  await expect(page.getByText("Deadline para votar")).toBeVisible();
});
