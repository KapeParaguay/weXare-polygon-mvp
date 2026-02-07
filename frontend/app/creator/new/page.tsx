"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { projectSchema } from "../../../lib/validators";
import { api } from "../../../lib/api";
import { useTranslation } from "react-i18next";

export default function CreatorNew() {
  const { t } = useTranslation();
  const { register, handleSubmit, formState } = useForm({
    resolver: zodResolver(projectSchema)
  });

  const onSubmit = async (values: any) => {
    const project = await api<{ id: number }>("/projects", {
      method: "POST",
      body: JSON.stringify(values)
    });
    await api(`/projects/${project.id}/proposals/generate`, { method: "POST" });
    window.location.href = `/creator/projects/${project.id}`;
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("creator_create_project")}</h1>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input className="border rounded px-3 py-2" placeholder={t("creator_title")} {...register("title")} />
        <textarea className="border rounded px-3 py-2" placeholder={t("creator_description")} rows={5} {...register("description")} />
        {formState.errors.title && <p className="text-sm text-red-600">{t("creator_title_required")}</p>}
        {formState.errors.description && <p className="text-sm text-red-600">{t("creator_description_required")}</p>}
        <div>
          <button className="button" type="submit">{t("creator_generate_proposal")}</button>
        </div>
      </form>
    </div>
  );
}
