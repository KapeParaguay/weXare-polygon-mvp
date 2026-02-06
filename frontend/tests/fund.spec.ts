import { test, expect } from "@playwright/test";

test("fund page renders moonpay warning and status", async ({ page }) => {
  await page.goto("/creator/fund");
  await expect(page.getByText("Fondear (MoonPay)")).toBeVisible();
  await expect(page.getByText("MoonPay puede cobrar comisiones altas")).toBeVisible();
  await expect(page.getByText("Estado del fondeo")).toBeVisible();
});
