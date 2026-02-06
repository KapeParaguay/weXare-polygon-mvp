export default function JudgeHome() {
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Ofertas de juez</h1>
      <p className="text-sm text-slate-600">Acepta o declina en 30 minutos.</p>
      <p className="text-xs text-slate-600">Deadline para votar: 24 horas desde aceptación.</p>
      <div className="mt-4 flex gap-2">
        <button className="button">Aceptar</button>
        <button className="border rounded px-3 py-2">Declinar</button>
      </div>
    </div>
  );
}
