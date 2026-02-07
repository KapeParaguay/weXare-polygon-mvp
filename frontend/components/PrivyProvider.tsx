"use client";

import { ReactNode } from "react";
import { PrivyProvider } from "@privy-io/react-auth";

export default function PrivyProviderWrapper({ children }: { children: ReactNode }) {
  const appId = process.env.NEXT_PUBLIC_PRIVY_APP_ID || "";
  if (!appId) {
    return <>{children}</>;
  }
  return (
    <PrivyProvider
      appId={appId}
      config={{
        loginMethods: ["email"],
        appearance: { theme: "light" },
      }}
    >
      {children}
    </PrivyProvider>
  );
}
