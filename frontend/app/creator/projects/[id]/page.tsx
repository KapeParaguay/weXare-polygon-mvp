"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../../../lib/api";
import { useTranslation } from "react-i18next";

export default function CreatorProject() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const { t } = useTranslation();

  useEffect(() => {
    api(`/projects/${params.id}`).then(setData).catch(() => null);
  }, [params.id]);

  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">{t("project_title")}</h1>
        <p className="text-sm text-slate-600">{t("project_timeline")}</p>
        <div className="mt-4 flex gap-2">
          <a className="button inline-block" href={`/creator/fund?quest_id=${data?.quests?.[0]?.id || ""}`}>{t("project_fund")}</a>
          <a className="underline" href="./proposal">{t("project_view_proposal")}</a>
        </div>
        <div className="mt-4 p-3 border rounded bg-amber-50 text-sm">
          <strong>{t("scope_freeze")}</strong>
        </div>
        {data?.quests && (
          <div className="mt-4 text-sm">
            <div className="font-semibold">{t("quests_label")}</div>
            {data.quests.map((q: any) => (
              <div key={q.id} className="mt-2">
                #{q.index} — {q.status} — ${q.budget}
                <div className="text-xs text-slate-600">{t("execution_note")}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
