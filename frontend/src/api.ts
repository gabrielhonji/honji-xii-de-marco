let csrfToken = "";

export type Session = { user: { id: string; name: string }; capabilities: string[]; csrfToken: string };

export async function loadSession(): Promise<Session | null> {
  const response = await fetch("/api/session", { credentials: "same-origin" });
  if (response.status === 401) return null;
  if (!response.ok) {
    let detail = "Não foi possível verificar sua sessão.";
    try {
      const failure = (await response.json()) as { error?: unknown; code?: unknown };
      if (typeof failure.error === "string" && failure.error.trim()) detail = failure.error;
      if (typeof failure.code === "string" && /^[a-z0-9_]{1,64}$/.test(failure.code)) {
        detail += ` (${failure.code})`;
      }
    } catch {
      /* Preserve the generic message for non-JSON proxy failures. */
    }
    throw new Error(detail);
  }
  const session = (await response.json()) as Session;
  csrfToken = session.csrfToken;
  return session;
}

export async function logout(): Promise<Response> {
  return fetch("/auth/logout", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
    body: "{}",
  });
}

export async function api(path: string, payload: unknown): Promise<Response> {
  const response = await fetch(path, {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken },
    body: JSON.stringify(payload),
  });
  if (response.status === 401) {
    window.location.assign("/auth/login");
    throw new Error("Sua sessão expirou. Redirecionando para o login…");
  }
  if (!response.ok) {
    let message = "Não foi possível processar os dados.";
    try {
      message = (await response.json()).error || message;
    } catch {
      /* Preserve a useful error for non-JSON responses. */
    }
    throw new Error(message);
  }
  return response;
}
export const message = (error: unknown) =>
  error instanceof Error
    ? error.message
    : "Não foi possível concluir a operação.";
