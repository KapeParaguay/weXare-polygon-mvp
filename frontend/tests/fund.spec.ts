import { test, expect } from "@playwright/test";

test("fund page renders moonpay warning and status", async ({ page }) => {
  await page.goto("/creator/fund");
  await expect(page.getByText("Fund (MoonPay)")).toBeVisible();
  await expect(page.getByText("MoonPay may charge higher fees")).toBeVisible();
  await expect(page.getByText("Funding status")).toBeVisible();
});
