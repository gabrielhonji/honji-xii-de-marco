export async function api(path: string, payload: unknown): Promise<Response> {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
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
