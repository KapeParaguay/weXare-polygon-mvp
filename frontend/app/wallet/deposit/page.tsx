"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../../lib/api";

export default function DepositPage() {
  const { t } = useTranslation();
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [session, setSession] = useState<string | null>(null);

  const initiate = async () => {
    const res = await api(`/wallet/deposit/initiate`, {
      method: "POST",
      body: JSON.stringify({ amount_usd: Number(amount) })
    });
    setStatus("PENDING");
    setSession(res.provider_session_id || null);
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("deposit_title")}</h1>
      <p className="text-sm text-slate-600">{t("deposit_subtitle")}</p>

      <div className="mt-4 grid gap-3">
        <label className="text-sm">{t("deposit_amount")}</label>
        <input className="border rounded px-3 py-2" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="100" />
        <button className="button" onClick={initiate}>{t("deposit_start")}</button>
        {status && <div className="text-sm">{t("status_label")} {status}</div>}
        {session && <div className="text-xs text-slate-600">{t("session_label")} {session}</div>}
      </div>
    </div>
  );
}
