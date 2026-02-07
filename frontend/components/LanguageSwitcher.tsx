"use client";

import { useState } from "react";
import i18n from "../lib/i18n";

export default function LanguageSwitcher() {
  const [lang, setLang] = useState(i18n.language || "en");

  const change = (next: string) => {
    setLang(next);
    i18n.changeLanguage(next);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("lang", next);
    }
  };

  return (
    <select className="border rounded px-2 py-1 text-xs" value={lang} onChange={(e) => change(e.target.value)}>
      <option value="en">EN</option>
      <option value="es">ES</option>
    </select>
  );
}
