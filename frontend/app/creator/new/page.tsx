"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { projectSchema } from "../../../lib/validators";
import { api } from "../../../lib/api";

export default function CreatorNew() {
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
      <h1 className="text-xl font-semibold mb-2">Crear proyecto</h1>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input className="border rounded px-3 py-2" placeholder="Título" {...register("title")} />
        <textarea className="border rounded px-3 py-2" placeholder="Descripción" rows={5} {...register("description")} />
        {formState.errors.title && <p className="text-sm text-red-600">Título requerido</p>}
        {formState.errors.description && <p className="text-sm text-red-600">Descripción requerida</p>}
        <div>
          <button className="button" type="submit">Generar propuesta</button>
        </div>
      </form>
    </div>
  );
}
