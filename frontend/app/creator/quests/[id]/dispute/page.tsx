"use client";

import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { disputeSchema } from "../../../../../lib/validators";
import { api } from "../../../../../lib/api";
import { useTranslation } from "react-i18next";

export default function CreatorMilestoneDispute() {
  const params = useParams<{ id: string }>();
  const { register, handleSubmit, formState } = useForm({
    resolver: zodResolver(disputeSchema)
  });
  const { t } = useTranslation();

  const onSubmit = async (values: any) => {
    await api(`/quests/${params.id}/dispute`, {
      method: "POST",
      body: JSON.stringify({ reason: values.reason, evidence_url: values.evidence })
    });
    window.location.href = `/creator/projects/${params.id}`;
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("dispute_open_title")}</h1>
      <p className="text-sm text-slate-600">{t("dispute_evidence_required")}</p>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <textarea className="border rounded px-3 py-2" placeholder={t("dispute_reason")} rows={4} {...register("reason")} />
        <input className="border rounded px-3 py-2" placeholder={t("dispute_evidence_link")} {...register("evidence")} />
        {formState.errors.reason && <p className="text-sm text-red-600">{t("dispute_reason_required")}</p>}
        {formState.errors.evidence && <p className="text-sm text-red-600">{t("evidence_required")}</p>}
        <button className="button" type="submit">{t("dispute_submit")}</button>
      </form>
    </div>
  );
}
