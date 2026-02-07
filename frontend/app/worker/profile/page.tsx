"use client";

import { useTranslation } from "react-i18next";

export default function WorkerProfile() {
  const { t } = useTranslation();
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("worker_profile_title")}</h1>
      <div className="grid gap-2 text-sm">
        <label><input type="radio" name="status" /> {t("status_active")}</label>
        <label><input type="radio" name="status" /> {t("status_paused")}</label>
        <label><input type="radio" name="status" /> {t("status_vacation")}</label>
      </div>
      <div className="mt-4">
        <button className="button">{t("save")}</button>
      </div>
    </div>
  );
}
