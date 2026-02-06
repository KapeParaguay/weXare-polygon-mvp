import { test, expect } from "@playwright/test";

test("withdraw page renders methods", async ({ page }) => {
  await page.goto("/wallet/withdraw");
  await expect(page.getByText("Retirar fondos")).toBeVisible();
  await expect(page.getByText("Transferencia bancaria")).toBeVisible();
  await expect(page.getByText("USDC (wallet externa)")).toBeVisible();
  await expect(page.getByText("MoonPay")).toBeVisible();
});
