"use client";

import { useTranslation } from "react-i18next";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function JudgeHome() {
  const { t } = useTranslation();
  const [offers, setOffers] = useState<any[]>([]);

  useEffect(() => {
    api("/judge/offers").then((r: any) => setOffers(r.offers || [])).catch(() => null);
  }, []);

  const accept = async (id: number) => {
    await api(`/judge/offers/${id}/accept`, { method: "POST" });
    setOffers((prev) => prev.filter((o) => o.id !== id));
  };

  const decline = async (id: number) => {
    await api(`/judge/offers/${id}/decline`, { method: "POST" });
    setOffers((prev) => prev.filter((o) => o.id !== id));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("judge_offers_title")}</h1>
      <p className="text-sm text-slate-600">{t("judge_accept_note")}</p>
      <p className="text-xs text-slate-600">{t("judge_deadline_note")}</p>
      <div className="mt-4 grid gap-3">
        {offers.length === 0 && (
          <div className="text-sm text-slate-500">{t("feed_empty")}</div>
        )}
        {offers.map((o) => (
          <div key={o.id} className="border rounded p-3">
            <div className="text-sm text-slate-500">Dispute #{o.dispute_id}</div>
            <div className="mt-2 flex gap-2">
              <button className="button" onClick={() => accept(o.id)}>{t("accept")}</button>
              <button className="border rounded px-3 py-2" onClick={() => decline(o.id)}>{t("decline")}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
