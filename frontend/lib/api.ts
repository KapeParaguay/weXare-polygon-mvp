export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("privy_access_token");
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token || "mock"}`,
      ...(options.headers || {})
    }
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }
  return res.json() as Promise<T>;
}
