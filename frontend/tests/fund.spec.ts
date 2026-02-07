import { test, expect } from "@playwright/test";

test("fund page renders moonpay warning and status", async ({ page }) => {
  await page.goto("/creator/fund");
  await expect(page.getByRole("heading", { name: /Fund|Fondear/ })).toBeVisible();
  await expect(page.getByText(/MoonPay may charge higher fees|MoonPay puede cobrar comisiones altas/)).toBeVisible();
  await expect(page.getByText(/Funding status|Estado del fondeo/)).toBeVisible();
});
