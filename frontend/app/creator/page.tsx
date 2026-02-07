"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../lib/api";

export default function CreatorHome() {
  const { t } = useTranslation();
  const [balance, setBalance] = useState<number | null>(null);

  useEffect(() => {
    api(`/wallet/balance`)
      .then((r: any) => setBalance(r.available_usdc ?? 0))
      .catch(() => setBalance(0));
  }, []);

  const canCreate = (balance ?? 0) > 0;
  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">{t("creator_projects")}</h1>
        <p className="text-sm text-slate-600">{t("creator_projects_sub")}</p>
        <div className="mt-3 text-sm">
          <span className="font-semibold">{t("available_funds")}</span>{" "}
          {balance === null ? t("balance_loading") : `$${balance.toFixed(2)}`}
        </div>
        <div className="mt-4 flex gap-2 items-center">
          <button
            className="button"
            disabled={!canCreate}
            title={!canCreate ? t("fund_required_note") : ""}
            onClick={() => {
              if (canCreate) window.location.href = "/creator/new";
            }}
          >
            {t("creator_new_project")}
          </button>
          <a className="underline" href="/wallet/deposit">{t("fund_account_cta")}</a>
        </div>
        {!canCreate && (
          <div className="mt-2 text-xs text-amber-700">{t("fund_required_note")}</div>
        )}
      </div>
    </div>
  );
}
