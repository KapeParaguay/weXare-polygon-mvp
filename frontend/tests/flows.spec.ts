import { test, expect } from "@playwright/test";

test("creator flow pages", async ({ page }) => {
  await page.goto("/creator");
  await expect(page.getByText("Proyectos")).toBeVisible();
  await page.goto("/creator/new");
  await expect(page.getByText("Crear proyecto")).toBeVisible();
  await page.goto("/creator/quests/1/review");
  await expect(page.getByText("Revisión de quest")).toBeVisible();
});

test("worker flow pages", async ({ page }) => {
  await page.goto("/worker/profile");
  await expect(page.getByText("Perfil de worker")).toBeVisible();
  await page.goto("/worker/feed");
  await expect(page.getByText("Feed de tareas")).toBeVisible();
  await page.goto("/worker/tasks/active");
  await expect(page.getByText("Tarea activa")).toBeVisible();
});

test("judge flow pages", async ({ page }) => {
  await page.goto("/judge");
  await expect(page.getByText("Ofertas de juez")).toBeVisible();
  await page.goto("/judge/disputes/1");
  await expect(page.getByText("Disputa")).toBeVisible();
});
