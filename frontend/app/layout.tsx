import "./globals.css";
import type { ReactNode } from "react";
import QueryProvider from "../components/QueryProvider";
import I18nProvider from "../components/I18nProvider";
import NavBar from "../components/NavBar";
import PrivyProviderWrapper from "../components/PrivyProvider";

export const metadata = {
  title: "WEXARE MVP",
  description: "Agentes, hitos y disputas con UX Web2"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <PrivyProviderWrapper>
          <I18nProvider>
            <div className="max-w-5xl mx-auto p-6">
              <header className="flex items-center justify-between mb-8">
                <div className="text-2xl font-bold">WEXARE</div>
                <NavBar />
              </header>
              <QueryProvider>{children}</QueryProvider>
            </div>
          </I18nProvider>
        </PrivyProviderWrapper>
      </body>
    </html>
  );
}
