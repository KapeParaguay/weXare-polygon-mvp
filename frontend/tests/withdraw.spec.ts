import { test, expect } from "@playwright/test";

test("withdraw page renders methods", async ({ page }) => {
  await page.goto("/wallet/withdraw");
  await expect(page.getByText("Withdraw funds")).toBeVisible();
  await expect(page.getByText("USDC (external wallet)")).toBeVisible();
  await expect(page.getByText("MoonPay (recommended)")).toBeVisible();
});
