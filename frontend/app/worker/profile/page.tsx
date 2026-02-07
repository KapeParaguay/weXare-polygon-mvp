"use client";

import { useState } from "react";
import { useTranslation } from "react-i18next";
import { api } from "../../../lib/api";

export default function WorkerProfile() {
  const { t } = useTranslation();
  const [status, setStatus] = useState("ACTIVE");

  const save = async () => {
    await api(`/me/status`, {
      method: "PATCH",
      body: JSON.stringify({ status })
    });
  };

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("worker_profile_title")}</h1>
      <div className="grid gap-2 text-sm">
        <label><input type="radio" name="status" checked={status === "ACTIVE"} onChange={() => setStatus("ACTIVE")} /> {t("status_active")}</label>
        <label><input type="radio" name="status" checked={status === "PAUSED"} onChange={() => setStatus("PAUSED")} /> {t("status_paused")}</label>
        <label><input type="radio" name="status" checked={status === "VACATION"} onChange={() => setStatus("VACATION")} /> {t("status_vacation")}</label>
      </div>
      <div className="mt-4">
        <button className="button" onClick={save}>{t("save")}</button>
      </div>
    </div>
  );
}
