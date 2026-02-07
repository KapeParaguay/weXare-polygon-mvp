"use client";

import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./LanguageSwitcher";

export default function NavBar() {
  const { t } = useTranslation();
  return (
    <nav className="flex gap-4 text-sm items-center">
      <a href="/feed">{t("nav_feed")}</a>
      <a href="/creator">{t("nav_creator")}</a>
      <a href="/worker">{t("nav_worker")}</a>
      <a href="/judge">{t("nav_judge")}</a>
      <a href="/wallet/deposit">{t("nav_add_funds")}</a>
      <a href="/wallet/withdraw">{t("nav_withdraw")}</a>
      <LanguageSwitcher />
    </nav>
  );
}
