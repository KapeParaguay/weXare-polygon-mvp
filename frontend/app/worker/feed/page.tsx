"use client";

import { useTranslation } from "react-i18next";

export default function WorkerFeed() {
  const { t } = useTranslation();
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("worker_feed_title")}</h1>
      <p className="text-sm text-slate-600">{t("worker_feed_note")}</p>
      <div className="mt-4 flex gap-2">
        <button className="button">{t("feed_accept")}</button>
        <button className="border rounded px-3 py-2">{t("feed_reject")}</button>
      </div>
    </div>
  );
}
