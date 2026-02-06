export default function LoginPage() {
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">Iniciar sesión</h1>
      <p className="text-sm text-slate-600 mb-4">Accede con magic link por email.</p>
      <form className="flex gap-2">
        <input className="border rounded px-3 py-2 flex-1" placeholder="tu@email.com" />
        <button className="button">Enviar link</button>
      </form>
    </div>
  );
}
