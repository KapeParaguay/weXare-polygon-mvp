export default function WorkerFeed() {
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Feed de tareas</h1>
      <p className="text-sm text-slate-600">Acepta o pasa tareas. Si pasas, se oculta por 7 días.</p>
      <div className="mt-4 flex gap-2">
        <button className="button">Aceptar</button>
        <button className="border rounded px-3 py-2">Pasar</button>
      </div>
    </div>
  );
}
