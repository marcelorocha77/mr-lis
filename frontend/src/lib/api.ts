// Vazio => usa mesma origem + proxy do Next.js (/api/* -> backend). Isso funciona
// tanto em localhost quanto atrás de um tunel público sem CORS.
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
const TOKEN_KEY = "mr_access_token";
const REFRESH_KEY = "mr_refresh_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveTokens(access: string, refresh: string) {
  window.localStorage.setItem(TOKEN_KEY, access);
  window.localStorage.setItem(REFRESH_KEY, refresh);
}

export function clearTokens() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

export async function api<T = unknown>(
  path: string,
  init: RequestInit & { json?: unknown } = {}
): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    init.body = JSON.stringify(init.json);
  }

  const url = API_URL ? `${API_URL}${path}` : `/api${path}`;
  const res = await fetch(url, { ...init, headers });

  if (res.status === 401 && typeof window !== "undefined" && !path.startsWith("/auth/")) {
    clearTokens();
    window.location.href = "/login";
    throw new Error("unauthorized");
  }

  if (!res.ok) {
    let msg = res.statusText;
    try {
      const j = await res.json();
      msg = (j as { detail?: string }).detail || msg;
    } catch {}
    throw new Error(msg);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export type Page<T> = { items: T[]; total: number; page: number; page_size: number };
