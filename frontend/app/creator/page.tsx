export default function CreatorHome() {
  return (
    <div className="grid gap-4">
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">Proyectos</h1>
        <p className="text-sm text-slate-600">Lista de proyectos del creador.</p>
        <div className="mt-3 text-sm">
          <span className="font-semibold">Fondos disponibles:</span> $0.00
        </div>
        <a className="button inline-block mt-4" href="/creator/new">Nuevo proyecto</a>
      </div>
    </div>
  );
}
