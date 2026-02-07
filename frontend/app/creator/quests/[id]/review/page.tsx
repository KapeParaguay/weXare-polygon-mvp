"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { api } from "../../../../../lib/api";
import { useTranslation } from "react-i18next";

export default function CreatorMilestoneReview() {
  const params = useParams<{ id: string }>();
  const [payout, setPayout] = useState("");
  const { t } = useTranslation();

  const approve = async () => {
    await api(`/quests/${params.id}/approve`, {
      method: "POST",
      body: JSON.stringify({ quest_id: Number(params.id), evidence_url: "https://example.com/evidence", payout_amount: payout ? Number(payout) : undefined })
    });
    alert(t("quest_approve"));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("quest_review_title")}</h1>
      <p className="text-sm text-slate-600">{t("quest_review_sub")}</p>
      <div className="mt-4 grid gap-2">
        <label className="text-sm">{t("quest_payout_label")}</label>
        <input className="border rounded px-3 py-2" value={payout} onChange={(e) => setPayout(e.target.value)} placeholder="Ej: 800" />
      </div>
      <div className="mt-4 flex gap-2">
        <button className="button" onClick={approve}>{t("quest_approve")}</button>
        <a className="underline" href="../dispute">{t("quest_dispute")}</a>
      </div>
    </div>
  );
}
