import { test, expect } from "@playwright/test";

test("withdraw page renders methods", async ({ page }) => {
  await page.goto("/wallet/withdraw");
  await expect(page.getByRole("heading", { name: /Withdraw funds|Retirar fondos/ })).toBeVisible();
  const optionTexts = await page.locator("#withdraw_method option").allTextContents();
  expect(optionTexts.join(" ")).toMatch(/USD \(external wallet\)|USD \(wallet externa\)/);
  expect(optionTexts.join(" ")).toMatch(/MoonPay \(recommended\)|MoonPay \(recomendado\)/);
});
