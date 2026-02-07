"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../lib/api";

export default function UnifiedFeed() {
  const { t } = useTranslation();
  const [cards, setCards] = useState<any[]>([]);

  useEffect(() => {
    api("/feed").then((r: any) => setCards(r.cards || [])).catch(() => null);
  }, []);

  const accept = async (card: any) => {
    if (card.type === "work") {
      await api(`/tasks/${card.id}/accept`, { method: "POST" });
    } else {
      await api(`/judge/offers/${card.id}/accept`, { method: "POST" });
    }
    setCards((prev) => prev.filter((c) => c.id !== card.id));
  };

  const reject = async (card: any) => {
    if (card.type === "work") {
      await api(`/tasks/${card.id}/decline`, { method: "POST" });
    } else {
      await api(`/judge/offers/${card.id}/decline`, { method: "POST" });
    }
    setCards((prev) => prev.filter((c) => c.id !== card.id));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("feed_title")}</h1>
      <p className="text-sm text-slate-600">{t("feed_subtitle")}</p>

      <div className="mt-6 grid gap-4">
        {cards.length === 0 && (
          <div className="text-sm text-slate-500">{t("feed_empty")}</div>
        )}
        {cards.map((card) => (
          <div key={`${card.type}-${card.id}`} className="border rounded p-4">
            <div className="text-sm text-slate-500">
              {card.type === "work" ? t("work_card_title") : t("judge_card_title")}
            </div>
            <div className="text-lg font-semibold">{card.title}</div>
            <div className="mt-3 flex gap-2">
              <button className="button" onClick={() => accept(card)}>{t("feed_accept")}</button>
              <button className="button" onClick={() => reject(card)}>{t("feed_reject")}</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
