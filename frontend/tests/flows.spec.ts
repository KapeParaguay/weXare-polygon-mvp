import { test, expect } from "@playwright/test";

test("creator flow pages", async ({ page }) => {
  await page.goto("/creator");
  await expect(page.getByRole("heading", { name: /Projects|Proyectos/ })).toBeVisible();
  await page.goto("/creator/new");
  await expect(page.getByRole("heading", { name: /Create project|Crear proyecto/ })).toBeVisible();
  await page.goto("/creator/quests/1/review");
  await expect(page.getByRole("heading", { name: /Quest review|Revisión de quest/ })).toBeVisible();
});

test("worker flow pages", async ({ page }) => {
  await page.goto("/feed");
  await expect(page.getByText("Unified feed")).toBeVisible();
  await page.goto("/worker/profile");
  await expect(page.getByText("Worker profile")).toBeVisible();
  await page.goto("/worker/feed");
  await expect(page.getByText("Task feed")).toBeVisible();
  await page.goto("/worker/tasks/active");
  await expect(page.getByText("Active task")).toBeVisible();
});

test("judge flow pages", async ({ page }) => {
  await page.goto("/judge");
  await expect(page.getByText("Judge offers")).toBeVisible();
  await page.goto("/judge/disputes/1");
  await expect(page.getByText("Dispute")).toBeVisible();
});
