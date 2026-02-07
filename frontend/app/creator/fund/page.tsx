"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useTranslation } from "react-i18next";
import { api } from "../../../lib/api";

export default function CreatorFund() {
  const { t } = useTranslation();
  const searchParams = useSearchParams();
  const [questId, setQuestId] = useState("");
  const [amount, setAmount] = useState("");
  const [paymentId, setPaymentId] = useState<number | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [fee, setFee] = useState<number | null>(null);

  useEffect(() => {
    const qid = searchParams.get("quest_id");
    if (qid) setQuestId(qid);
  }, [searchParams]);

  useEffect(() => {
    api("/config")
      .then((res: any) => {
        if (typeof res?.onchain_node_fee_usd === "number") {
          setFee(res.onchain_node_fee_usd);
        }
      })
      .catch(() => null);
  }, []);

  const submit = async () => {
    const res: any = await api(`/payments/initiate`, {
      method: "POST",
      body: JSON.stringify({ quest_id: Number(questId), amount: Number(amount) })
    });
    setPaymentId(res.payment_id);
    setStatus("INITIATED");
    alert(`Pago iniciado. Fee estimada: ${res.fee}`);
  };

  const setMockStatus = async (next: string) => {
    if (!paymentId) return;
    await api(`/payments/${paymentId}/confirm`, {
      method: "POST",
      body: JSON.stringify({ status: next })
    });
    setStatus(next);
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("creator_fund_title")}</h1>
      <p className="text-sm text-slate-600">{t("creator_fund_subtitle")}</p>
      <p className="text-xs text-slate-500 mt-1">
        {t("creator_fund_fee_note", { fee: (fee ?? 0.25).toFixed(2) })}
      </p>

      <div className="mt-4 grid gap-3">
        <input className="border rounded px-3 py-2" placeholder={t("creator_fund_quest_id")} value={questId} onChange={(e) => setQuestId(e.target.value)} />
        <input className="border rounded px-3 py-2" placeholder={t("creator_fund_amount")} value={amount} onChange={(e) => setAmount(e.target.value)} />
        <p className="text-xs text-amber-700">{t("withdraw_moonpay_warning")}</p>
        <button className="button" onClick={submit}>{t("creator_fund_start")}</button>
      </div>

      <div className="mt-6 text-sm">
        <div className="font-semibold">{t("creator_fund_status")}</div>
        <div>{status ? t(`fund_status_${status}`) : t("fund_status_none")}</div>
        <div className="mt-2 text-xs text-slate-600">{t("fund_status_delays")}</div>
        <div className="mt-3 flex gap-2">
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("PAID_PENDING_USDC")}>{t("fund_mock_paid")}</button>
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("USDC_CONFIRMED")}>{t("fund_mock_usdc")}</button>
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("FAILED")}>{t("fund_mock_failed")}</button>
        </div>
      </div>
    </div>
  );
}
