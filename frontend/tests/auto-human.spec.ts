import { test, expect } from "@playwright/test";

test("creator project shows auto/human fallback", async ({ page }) => {
  await page.goto("/creator/projects/1");
  await expect(page.getByText("Ejecución: AUTO → fallback HUMAN si falla")).toBeVisible();
});
