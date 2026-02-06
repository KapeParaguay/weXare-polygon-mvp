"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { api } from "../../../../../lib/api";

export default function CreatorMilestoneReview() {
  const params = useParams<{ id: string }>();
  const [payout, setPayout] = useState("");

  const approve = async () => {
    await api(`/quests/${params.id}/approve`, {
      method: "POST",
      body: JSON.stringify({ quest_id: Number(params.id), evidence_url: "https://example.com/evidence", payout_amount: payout ? Number(payout) : undefined })
    });
    alert("Quest aprobado");
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Revisión de quest</h1>
      <p className="text-sm text-slate-600">Evidencia requerida para aprobar.</p>
      <div className="mt-4 grid gap-2">
        <label className="text-sm">Payout al worker (opcional, sobrante se reembolsa automáticamente)</label>
        <input className="border rounded px-3 py-2" value={payout} onChange={(e) => setPayout(e.target.value)} placeholder="Ej: 800" />
      </div>
      <div className="mt-4 flex gap-2">
        <button className="button" onClick={approve}>Aprobar quest</button>
        <a className="underline" href="../dispute">Disputar</a>
      </div>
    </div>
  );
}
