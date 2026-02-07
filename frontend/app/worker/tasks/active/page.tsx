"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { submitSchema } from "../../../../lib/validators";
import { api } from "../../../../lib/api";
import { useTranslation } from "react-i18next";

export default function WorkerActiveTask() {
  const { t } = useTranslation();
  const { register, handleSubmit, formState } = useForm({
    resolver: zodResolver(submitSchema)
  });

  const onSubmit = async (values: any) => {
    // MVP: using task_id=1 placeholder
    await api(`/tasks/1/submit`, {
      method: "POST",
      body: JSON.stringify({ evidence_url: values.evidence })
    });
    alert(t("delivery_sent"));
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("worker_active_title")}</h1>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input className="border rounded px-3 py-2" placeholder={t("evidence_link")} {...register("evidence")} />
        {formState.errors.evidence && <p className="text-sm text-red-600">{t("evidence_required")}</p>}
        <button className="button" type="submit">{t("submit_delivery")}</button>
      </form>
    </div>
  );
}
