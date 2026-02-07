"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../../lib/api";

export default function WithdrawPage() {
  const { t } = useTranslation();
  const [options, setOptions] = useState<any[]>([]);
  const [method, setMethod] = useState("moonpay");
  const [amount, setAmount] = useState("");
  const [destination, setDestination] = useState("");
  const [confirm, setConfirm] = useState(false);
  const [balance, setBalance] = useState<any>(null);
  const [estimate, setEstimate] = useState<any>(null);

  useEffect(() => {
    api(`/withdrawal/options`).then((r: any) => setOptions(r.options || [])).catch(() => null);
    api(`/wallet/balance`).then((r: any) => setBalance(r)).catch(() => null);
  }, []);

  const submit = async () => {
    if (method === "external" && !confirm) {
      alert("Debes confirmar que la dirección es correcta.");
      return;
    }
    if (method === "moonpay") {
      const res = await api(`/wallet/withdraw/moonpay`, {
        method: "POST",
        body: JSON.stringify({ amount_usdc: Number(amount) })
      });
      setEstimate(res);
      alert(t("request_sent_moonpay"));
      return;
    }
    if (method === "external") {
      await api(`/wallet/withdraw/external`, {
        method: "POST",
        body: JSON.stringify({ amount_usdc: Number(amount), destination })
      });
      alert("Retiro enviado on-chain");
      return;
    }
    alert(t("request_sent"));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("withdraw_title")}</h1>
      <p className="text-sm text-slate-600">{t("withdraw_subtitle")}</p>
      {balance && (
        <div className="mt-2 text-sm">
          Disponible: <strong>{balance.available_usdc}</strong> USDC
        </div>
      )}

      <div className="mt-4 grid gap-3">
        <label className="text-sm">{t("withdraw_amount")}</label>
        <input className="border rounded px-3 py-2" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="100" />

        <label className="text-sm">{t("withdraw_method")}</label>
        <select className="border rounded px-3 py-2" value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="moonpay">{t("withdraw_moonpay")}</option>
          <option value="external">{t("withdraw_external")}</option>
        </select>

        {method === "external" && (
          <div className="grid gap-2">
            <label className="text-sm">{t("withdraw_external_addr")}</label>
            <input className="border rounded px-3 py-2" value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="0x..." />
            <p className="text-xs text-red-600">{t("withdraw_external_warning")}</p>
            <label className="text-xs">
              <input type="checkbox" checked={confirm} onChange={(e) => setConfirm(e.target.checked)} /> {t("withdraw_external_confirm")}
            </label>
          </div>
        )}

        {method === "moonpay" && (
          <div className="grid gap-1">
            <p className="text-xs text-amber-700">{t("withdraw_moonpay_warning")}</p>
            {estimate?.estimated_fee_usd && (
              <p className="text-xs text-slate-600">
                {t("withdraw_fee_estimate", { fee: estimate.estimated_fee_usd, net: estimate.estimated_net_usd })}
              </p>
            )}
          </div>
        )}

        <button className="button" onClick={submit}>{t("withdraw_submit")}</button>
      </div>

      <div className="mt-4 text-xs text-slate-600">
        {t("withdraw_disclaimer")}
      </div>

      <div className="mt-6 text-sm">
        <div className="font-semibold">{t("withdraw_options")}</div>
        {options.map((o) => (
          <div key={o.method} className="mt-1">{o.method} — {o.eta} — fee {o.fee_pct}%</div>
        ))}
      </div>
    </div>
  );
}
