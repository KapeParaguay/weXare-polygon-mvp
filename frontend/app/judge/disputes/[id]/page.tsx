"use client";

import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { api } from "../../../../lib/api";

export default function JudgeDispute() {
  const params = useParams<{ id: string }>();
  const { register, handleSubmit } = useForm();
  const { t } = useTranslation();

  const onSubmit = async (values: any) => {
    await api(`/disputes/${params.id}/vote`, {
      method: "POST",
      body: JSON.stringify({
        dispute_id: Number(params.id),
        vote: values.vote,
        split: Number(values.split || 0),
        comment: values.comment,
        evidence_ref: values.evidence_ref
      })
    });
    alert(t("vote_sent"));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("dispute_title")}</h1>
      <p className="text-sm text-slate-600">{t("dispute_subtitle")}</p>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <select className="border rounded px-3 py-2" {...register("vote")}>
          <option value="CREATOR">{t("favor_creator")}</option>
          <option value="WORKER">{t("favor_worker")}</option>
          <option value="SPLIT">{t("split")}</option>
        </select>
        <input className="border rounded px-3 py-2" placeholder={t("split_pct")} {...register("split")} />
        <textarea className="border rounded px-3 py-2" placeholder={t("comment_required")} rows={4} {...register("comment")} />
        <input className="border rounded px-3 py-2" placeholder={t("evidence_ref")} {...register("evidence_ref")} />
        <button className="button" type="submit">{t("vote_submit")}</button>
      </form>
    </div>
  );
}
