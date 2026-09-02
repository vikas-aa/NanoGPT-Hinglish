import type {
  ChatApiRequest,
  ChatApiResponse,
  HealthApiResponse,
  Message,
} from "@/types/chat";

// ============================================================
// Base URL — comes from environment variable only
// ============================================================
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ============================================================
// Health check
// ============================================================
export async function checkHealth(): Promise<HealthApiResponse> {
  const res = await fetch(`${API_URL}/api/health`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }

  return res.json() as Promise<HealthApiResponse>;
}

// ============================================================
// Send chat message
// ============================================================
export async function sendMessage(
  messages: Message[],
  options?: {
    maxNewTokens?: number;
    temperature?: number;
    topK?: number;
  }
): Promise<string> {
  const body: ChatApiRequest = {
    messages: messages.map((m) => ({ role: m.role, content: m.content })),
    ...(options?.maxNewTokens !== undefined && {
      max_new_tokens: options.maxNewTokens,
    }),
    ...(options?.temperature !== undefined && {
      temperature: options.temperature,
    }),
    ...(options?.topK !== undefined && { top_k: options.topK }),
  };

  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let detail = `Server error ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail ?? detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(detail);
  }

  const data = (await res.json()) as ChatApiResponse;
  return data.response;
}
