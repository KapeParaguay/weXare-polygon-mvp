"use client";

import { useTranslation } from "react-i18next";

export default function WorkerHistory() {
  const { t } = useTranslation();
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("history_title")}</h1>
      <p className="text-sm text-slate-600">{t("history_completed")}</p>
    </div>
  );
}
