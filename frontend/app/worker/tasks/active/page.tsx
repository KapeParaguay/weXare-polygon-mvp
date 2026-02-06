"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { submitSchema } from "../../../../lib/validators";
import { api } from "../../../../lib/api";

export default function WorkerActiveTask() {
  const { register, handleSubmit, formState } = useForm({
    resolver: zodResolver(submitSchema)
  });

  const onSubmit = async (values: any) => {
    // MVP: using task_id=1 placeholder
    await api(`/tasks/1/submit`, {
      method: "POST",
      body: JSON.stringify({ evidence_url: values.evidence })
    });
    alert("Entrega enviada");
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Tarea activa</h1>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <input className="border rounded px-3 py-2" placeholder="Link de evidencia" {...register("evidence")} />
        {formState.errors.evidence && <p className="text-sm text-red-600">Evidencia válida requerida</p>}
        <button className="button" type="submit">Enviar entrega</button>
      </form>
    </div>
  );
}
