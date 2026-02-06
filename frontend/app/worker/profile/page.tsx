export default function WorkerProfile() {
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Perfil de worker</h1>
      <div className="grid gap-2 text-sm">
        <label><input type="radio" name="status" /> ACTIVE — receive work and occasional judge requests</label>
        <label><input type="radio" name="status" /> PAUSED — receive nothing; no penalties</label>
        <label><input type="radio" name="status" /> VACATION — receive nothing; no penalties</label>
      </div>
      <div className="mt-4">
        <button className="button">Guardar</button>
      </div>
    </div>
  );
}
