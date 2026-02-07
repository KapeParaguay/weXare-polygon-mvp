"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../../../lib/api";

export default function CreatorProject() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    api(`/projects/${params.id}`).then(setData).catch(() => null);
  }, [params.id]);

  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">Proyecto</h1>
        <p className="text-sm text-slate-600">Timeline de quests.</p>
        <div className="mt-4 flex gap-2">
          <button className="button">Financiar quest</button>
          <a className="underline" href={`/creator/projects/${params.id}/proposal`}>Ver propuesta</a>
        </div>
        <div className="mt-4 p-3 border rounded bg-amber-50 text-sm">
          <strong>Scope Freeze:</strong> el alcance del quest es inmutable luego de financiar.
        </div>
        {data?.quests && (
          <div className="mt-4 text-sm">
            <div className="font-semibold">Quests</div>
            {data.quests.map((q: any) => (
              <div key={q.id} className="mt-2">
                #{q.index} — {q.status} — ${q.budget}
                <div className="text-xs text-slate-600">Ejecución: AUTO → fallback HUMAN si falla</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
