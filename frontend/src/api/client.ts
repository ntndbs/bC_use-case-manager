const BASE_URL = "/api";
const TOKEN_KEY = "ucm_token";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...authHeaders() },
    ...options,
  });

  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail = body.detail || "";
    } catch (parseErr) {
      console.warn(`Failed to parse error response for ${path}:`, parseErr);
    }
    throw new Error(detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),

  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),

  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),

  del: <T>(path: string) =>
    request<T>(path, { method: "DELETE" }),

  upload: <T>(path: string, formData: FormData) =>
    request<T>(path, {
      method: "POST",
      headers: { ...authHeaders() },  // No Content-Type — browser sets boundary
      body: formData,
    }),
};
