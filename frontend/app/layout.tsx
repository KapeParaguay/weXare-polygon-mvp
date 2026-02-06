import "./globals.css";
import type { ReactNode } from "react";
import QueryProvider from "../components/QueryProvider";

export const metadata = {
  title: "WEXARE MVP",
  description: "Agentes, hitos y disputas con UX Web2"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body>
        <div className="max-w-5xl mx-auto p-6">
          <header className="flex items-center justify-between mb-8">
            <div className="text-2xl font-bold">WEXARE</div>
            <nav className="flex gap-4 text-sm">
              <a href="/creator">Creator</a>
              <a href="/worker">Worker</a>
              <a href="/judge">Judge</a>
              <a href="/creator/fund">Fondear</a>
              <a href="/wallet/withdraw">Retirar</a>
            </nav>
          </header>
          <QueryProvider>{children}</QueryProvider>
        </div>
      </body>
    </html>
  );
}
