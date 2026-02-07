"use client";

import { I18nextProvider } from "react-i18next";
import i18n from "../lib/i18n";
import { useEffect } from "react";

export default function I18nProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const stored = typeof window !== "undefined" ? window.localStorage.getItem("lang") : null;
    const lang = stored || (navigator.language?.startsWith("es") ? "es" : "en");
    i18n.changeLanguage(lang);
  }, []);

  return <I18nextProvider i18n={i18n}>{children}</I18nextProvider>;
}
