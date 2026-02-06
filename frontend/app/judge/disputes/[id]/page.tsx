"use client";

import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { api } from "../../../../lib/api";

export default function JudgeDispute() {
  const params = useParams<{ id: string }>();
  const { register, handleSubmit } = useForm();

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
    alert("Voto enviado");
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Disputa</h1>
      <p className="text-sm text-slate-600">Compara evidencia y vota.</p>
      <form className="grid gap-3" onSubmit={handleSubmit(onSubmit)}>
        <select className="border rounded px-3 py-2" {...register("vote")}>
          <option value="CREATOR">Favor creator</option>
          <option value="WORKER">Favor worker</option>
          <option value="SPLIT">Split</option>
        </select>
        <input className="border rounded px-3 py-2" placeholder="Split %" {...register("split")} />
        <textarea className="border rounded px-3 py-2" placeholder="Comentario (requerido)" rows={4} {...register("comment")} />
        <input className="border rounded px-3 py-2" placeholder="Referencia a evidencia" {...register("evidence_ref")} />
        <button className="button" type="submit">Votar</button>
      </form>
    </div>
  );
}
