"use client";

import { useTranslation } from "react-i18next";

export default function OfferLanding() {
  const { t } = useTranslation();
  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("offer_external_title")}</h1>
      <p className="text-sm text-slate-600">{t("offer_external_sub")}</p>
      <button className="button mt-4">{t("offer_accept")}</button>
    </div>
  );
}
