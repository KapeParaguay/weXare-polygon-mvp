"use client";

import { useTranslation } from "react-i18next";

export default function JudgeHome() {
  const { t } = useTranslation();
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("judge_offers_title")}</h1>
      <p className="text-sm text-slate-600">{t("judge_accept_note")}</p>
      <p className="text-xs text-slate-600">{t("judge_deadline_note")}</p>
      <div className="mt-4 flex gap-2">
        <button className="button">{t("accept")}</button>
        <button className="border rounded px-3 py-2">{t("decline")}</button>
      </div>
    </div>
  );
}
