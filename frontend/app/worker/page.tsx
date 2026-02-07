"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../lib/api";

type Reputation = {
  score: number;
  formula_version?: string;
};

export default function WorkerHome() {
  const { t } = useTranslation();
  const [rep, setRep] = useState<Reputation | null>(null);
  const [repError, setRepError] = useState(false);
  const [balance, setBalance] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const me = await api<any>("/me");
        if (!me?.id) return;
        const data = await api<any>(`/reputation/${me.id}?role=worker`);
        if (!cancelled) setRep({ score: data.score, formula_version: data.formula_version });
      } catch {
        if (!cancelled) setRepError(true);
      }
    };
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    api(`/wallet/balance`)
      .then((r: any) => setBalance(r.available_usdc ?? 0))
      .catch(() => setBalance(0));
  }, []);

  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">{t("worker_summary")}</h1>
        <p className="text-sm text-slate-600">{t("worker_active_task")}</p>
        <div className="mt-3 text-sm">
          <span className="font-semibold">{t("available_funds")}</span>{" "}
          {balance === null ? t("balance_loading") : `$${balance.toFixed(2)}`}
        </div>
        <div className="mt-4 flex gap-2">
          <a className="button" href="/worker/feed">Ir al feed</a>
          <a className="underline" href="/worker/profile">Editar perfil</a>
        </div>
        <div className="mt-4 text-sm text-slate-600">
          {t("worker_withdraw_note")}
        </div>
        <div className="mt-4 text-sm">
          <div className="font-semibold">{t("worker_your_quest")}</div>
          <div>{t("worker_quest_note")}</div>
        </div>
        <div className="mt-4 text-sm">
          <div className="font-semibold">{t("worker_reputation")}</div>
          <div>
            {rep
              ? `Rep worker: ${rep.score} (${rep.formula_version || "ELO v1"})`
              : repError
                ? t("worker_rep_value")
                : t("worker_rep_loading")}
          </div>
        </div>
      </div>
    </div>
  );
}
