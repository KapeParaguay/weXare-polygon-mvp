import { test, expect } from "@playwright/test";

test("deposit page renders", async ({ page }) => {
  await page.goto("/wallet/deposit");
  await expect(page.getByText("Add funds")).toBeVisible();
  await expect(page.getByText("Start MoonPay")).toBeVisible();
});
