import { test, expect } from "@playwright/test";

test("deposit page renders", async ({ page }) => {
  await page.goto("/wallet/deposit");
  await expect(page.getByRole("heading", { name: "Add funds" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Start MoonPay" })).toBeVisible();
});
