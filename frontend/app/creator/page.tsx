"use client";

import { useTranslation } from "react-i18next";

export default function CreatorHome() {
  const { t } = useTranslation();
  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">{t("creator_projects")}</h1>
        <p className="text-sm text-slate-600">{t("creator_projects_sub")}</p>
        <div className="mt-3 text-sm">
          <span className="font-semibold">{t("available_funds")}</span> $0.00
        </div>
        <a className="button inline-block mt-4" href="/creator/new">{t("creator_new_project")}</a>
      </div>
    </div>
  );
}
