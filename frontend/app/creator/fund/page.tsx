"use client";

import { useState } from "react";
import { api } from "../../../lib/api";

const STATUS_COPY: Record<string, string> = {
  INITIATED: "Pago iniciado. Esperando confirmación.",
  PAID_PENDING_USDC: "Pago confirmado. Esperando USDC.",
  USDC_CONFIRMED: "USDC confirmado. Listo para financiar quest.",
  FAILED: "Pago falló. Reintenta."
};

export default function CreatorFund() {
  const [questId, setQuestId] = useState("");
  const [amount, setAmount] = useState("");
  const [paymentId, setPaymentId] = useState<number | null>(null);
  const [status, setStatus] = useState<string | null>(null);

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
      <h1 className="text-xl font-semibold mb-2">Fondear (MoonPay)</h1>
      <p className="text-sm text-slate-600">Compra USDC para financiar quests.</p>

      <div className="mt-4 grid gap-3">
        <input className="border rounded px-3 py-2" placeholder="Quest ID" value={questId} onChange={(e) => setQuestId(e.target.value)} />
        <input className="border rounded px-3 py-2" placeholder="Monto" value={amount} onChange={(e) => setAmount(e.target.value)} />
        <p className="text-xs text-amber-700">MoonPay puede cobrar comisiones altas en montos pequeños.</p>
        <button className="button" onClick={submit}>Iniciar fondeo</button>
      </div>

      <div className="mt-6 text-sm">
        <div className="font-semibold">Estado del fondeo</div>
        <div>{status ? STATUS_COPY[status] : "Sin pagos activos"}</div>
        <div className="mt-2 text-xs text-slate-600">Delays típicos: confirmación 1–5 min, USDC 5–15 min.</div>
        <div className="mt-3 flex gap-2">
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("PAID_PENDING_USDC")}>Simular pago</button>
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("USDC_CONFIRMED")}>Simular USDC</button>
          <button className="border rounded px-3 py-1" onClick={() => setMockStatus("FAILED")}>Simular fallo</button>
        </div>
      </div>
    </div>
  );
}
