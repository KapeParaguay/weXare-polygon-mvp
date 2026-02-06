"use client";

import { useEffect, useState } from "react";
import { api } from "../../../lib/api";

export default function WithdrawPage() {
  const [options, setOptions] = useState<any[]>([]);
  const [method, setMethod] = useState("bank");
  const [amount, setAmount] = useState("");
  const [destination, setDestination] = useState("");
  const [country, setCountry] = useState("PY");
  const [confirm, setConfirm] = useState(false);

  useEffect(() => {
    api(`/withdrawal/options?country=${country}`).then((r: any) => setOptions(r.options || [])).catch(() => null);
  }, [country]);

  const submit = async () => {
    if (method === "crypto" && !confirm) {
      alert("Debes confirmar que la dirección es correcta.");
      return;
    }
    await api(`/wallet/withdraw`, {
      method: "POST",
      body: JSON.stringify({ amount: Number(amount), method, destination: destination || null, country })
    });
    alert("Solicitud enviada");
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Retirar fondos</h1>
      <p className="text-sm text-slate-600">Saldo en USD, sin términos cripto.</p>

      <div className="mt-4 grid gap-3">
        <label className="text-sm">Monto</label>
        <input className="border rounded px-3 py-2" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="100" />

        <label className="text-sm">Método</label>
        <select className="border rounded px-3 py-2" value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="bank">Transferencia bancaria</option>
          <option value="crypto">USDC (wallet externa)</option>
          <option value="moonpay">MoonPay</option>
        </select>

        {method === "crypto" && (
          <div className="grid gap-2">
            <label className="text-sm">Dirección externa</label>
            <input className="border rounded px-3 py-2" value={destination} onChange={(e) => setDestination(e.target.value)} placeholder="0x..." />
            <p className="text-xs text-red-600">Irreversible. Verifica la dirección.</p>
            <label className="text-xs">
              <input type="checkbox" checked={confirm} onChange={(e) => setConfirm(e.target.checked)} /> Confirmo que la dirección es correcta
            </label>
          </div>
        )}

        {method === "bank" && (
          <div className="grid gap-2">
            <label className="text-sm">País</label>
            <input className="border rounded px-3 py-2" value={country} onChange={(e) => setCountry(e.target.value)} />
            <p className="text-xs text-slate-600">ETA Paraguay 1–2 días hábiles, internacional 2–5 días.</p>
          </div>
        )}

        {method === "moonpay" && (
          <p className="text-xs text-amber-700">MoonPay puede cobrar comisiones altas en montos pequeños.</p>
        )}

        <button className="button" onClick={submit}>Solicitar retiro</button>
      </div>

      <div className="mt-6 text-sm">
        <div className="font-semibold">Opciones disponibles</div>
        {options.map((o) => (
          <div key={o.method} className="mt-1">{o.method} — {o.eta} — fee {o.fee_pct}%</div>
        ))}
      </div>
    </div>
  );
}
