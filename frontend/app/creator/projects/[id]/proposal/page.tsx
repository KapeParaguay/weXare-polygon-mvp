"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "../../../../../lib/api";
import { useTranslation } from "react-i18next";

export default function CreatorProposal() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const { t } = useTranslation();

  useEffect(() => {
    api(`/projects/${params.id}`).then(setData).catch(() => null);
  }, [params.id]);

  const proposal = data?.proposals?.[0];

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("proposal_title")}</h1>
      <p className="text-sm text-slate-600">{t("proposal_subtitle")}</p>
      {proposal && (
        <div className="mt-4 text-sm">
          <div>{t("proposal_version")}: {proposal.version}</div>
          <div>{t("proposal_buffer")}: {proposal.data?.buffer_pct || 20}%</div>
          <div>{t("proposal_fee")}: {proposal.data?.moonpay_fee_pct || 6}%</div>
          <div className="mt-2 font-semibold">{t("proposal_total")}: ${proposal.data?.price_to_creator}</div>
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
        <button className="button">{t("proposal_approve")}</button>
        <button className="border rounded px-3 py-2">{t("proposal_changes")}</button>
      </div>
    </div>
  );
}
