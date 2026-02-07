"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { usePrivy } from "@privy-io/react-auth";

function PrivyLogin() {
  const { t } = useTranslation();
  const { login, authenticated, ready, getAccessToken, user, logout } = usePrivy();
  const [status, setStatus] = useState<"idle" | "saving" | "done">("idle");

  useEffect(() => {
    const persist = async () => {
      if (!authenticated) return;
      setStatus("saving");
      const token = await getAccessToken();
      if (token && typeof window !== "undefined") {
        window.localStorage.setItem("privy_access_token", token);
      }
      setStatus("done");
    };
    persist();
  }, [authenticated, getAccessToken]);

  return (
    <div className="card">
      <h1 className="text-xl font-semibold mb-2">{t("login_title")}</h1>
      <p className="text-sm text-slate-600 mb-4">{t("login_subtitle")}</p>
      {!ready && <div className="text-sm text-slate-500">{t("login_loading")}</div>}
      {ready && !authenticated && (
        <button className="button" onClick={() => login()}>
          {t("login_send")}
        </button>
      )}
      {authenticated && (
        <div className="text-sm text-slate-700">
          <div>{t("login_signed_in")}: {user?.email || user?.id}</div>
          {status === "saving" && <div>{t("login_session_saving")}</div>}
          {status === "done" && <div>{t("login_session_ready")}</div>}
          <button className="button mt-3" onClick={() => logout()}>
            {t("login_signout")}
          </button>
        </div>
      )}
    </div>
  );
}

export default function LoginPage() {
  const appId = process.env.NEXT_PUBLIC_PRIVY_APP_ID || "";
  if (!appId) {
    return (
      <div className="card">
        <h1 className="text-xl font-semibold mb-2">Privy not configured</h1>
        <p className="text-sm text-slate-600">Set NEXT_PUBLIC_PRIVY_APP_ID to enable login.</p>
      </div>
    );
  }
  return <PrivyLogin />;
}
