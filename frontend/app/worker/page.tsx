export default function WorkerHome() {
  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">Resumen</h1>
        <p className="text-sm text-slate-600">Tu tarea activa y estado global.</p>
        <div className="mt-3 text-sm">
          <span className="font-semibold">Fondos disponibles:</span> $0.00
        </div>
        <div className="mt-4 flex gap-2">
          <a className="button" href="/worker/feed">Ir al feed</a>
          <a className="underline" href="/worker/profile">Editar perfil</a>
        </div>
        <div className="mt-4 text-sm text-slate-600">
          Retiros: solo a la wallet verificada de la cooperativa.
        </div>
        <div className="mt-4 text-sm">
          <div className="font-semibold">Tu Quest</div>
          <div>Verás solo tu quest asignado y su pago.</div>
        </div>
        <div className="mt-4 text-sm">
          <div className="font-semibold">Reputación</div>
          <div>Rep worker: 1000 (ELO v1)</div>
        </div>
      </div>
    </div>
  );
}
