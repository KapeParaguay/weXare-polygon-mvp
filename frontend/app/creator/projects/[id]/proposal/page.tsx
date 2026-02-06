"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../../../../lib/api";

export default function CreatorProposal() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api(`/projects/${params.id}`).then(setData).catch(() => null);
  }, [params.id]);

  const proposal = data?.proposals?.[0];

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Propuesta</h1>
      <p className="text-sm text-slate-600">Versión actual, hitos y presupuesto con buffer.</p>
      {proposal && (
        <div className="mt-4 text-sm">
          <div>Versión: {proposal.version}</div>
          <div>Buffer: {proposal.data?.buffer_pct || 20}%</div>
          <div>MoonPay fee: {proposal.data?.moonpay_fee_pct || 6}%</div>
          <div className="mt-2 font-semibold">Precio total (creator): ${proposal.data?.price_to_creator}</div>
          {proposal.data?.quests && (
            <div className="mt-2">
              {proposal.data.quests.map((q: any) => (
                <div key={q.index} className="mt-1">
                  Quest #{q.index} — ${q.price_to_creator} (worker ${q.budget})
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      <div className="mt-4 flex gap-2">
        <button className="button">Aprobar propuesta</button>
        <button className="border rounded px-3 py-2">Solicitar cambios</button>
      </div>
    </div>
  );
}
