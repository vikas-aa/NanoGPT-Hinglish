import { v4 as uuidv4 } from "uuid";
import type { Conversation, Message } from "@/types/chat";

// ============================================================
// localStorage keys
// ============================================================
const CONVERSATIONS_KEY = "nanogpt_conversations";
const ACTIVE_KEY = "nanogpt_active_conversation";

// ============================================================
// Helpers
// ============================================================
function load(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(CONVERSATIONS_KEY);
    return raw ? (JSON.parse(raw) as Conversation[]) : [];
  } catch {
    return [];
  }
}

function save(convs: Conversation[]): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(CONVERSATIONS_KEY, JSON.stringify(convs));
}

// ============================================================
// Public API
// ============================================================

export function getAllConversations(): Conversation[] {
  return load().sort((a, b) => b.updatedAt - a.updatedAt);
}

export function getConversation(id: string): Conversation | undefined {
  return load().find((c) => c.id === id);
}

export function createConversation(): Conversation {
  const conv: Conversation = {
    id: uuidv4(),
    title: "New Chat",
    messages: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  const convs = load();
  convs.unshift(conv);
  save(convs);
  return conv;
}

export function saveConversation(conv: Conversation): void {
  const convs = load();
  const idx = convs.findIndex((c) => c.id === conv.id);
  if (idx >= 0) {
    convs[idx] = { ...conv, updatedAt: Date.now() };
  } else {
    convs.unshift({ ...conv, updatedAt: Date.now() });
  }
  save(convs);
}

export function deleteConversation(id: string): void {
  const convs = load().filter((c) => c.id !== id);
  save(convs);
}

export function renameConversation(id: string, title: string): void {
  const convs = load();
  const conv = convs.find((c) => c.id === id);
  if (conv) {
    conv.title = title.trim() || "New Chat";
    conv.updatedAt = Date.now();
    save(convs);
  }
}

export function addMessage(convId: string, message: Message): Conversation | null {
  const convs = load();
  const conv = convs.find((c) => c.id === convId);
  if (!conv) return null;
  conv.messages.push(message);
  conv.updatedAt = Date.now();
  // Auto-generate title from first user message
  if (conv.title === "New Chat" && message.role === "user") {
    conv.title =
      message.content.length > 40
        ? message.content.slice(0, 40) + "…"
        : message.content;
  }
  save(convs);
  return conv;
}

export function updateMessage(
  convId: string,
  messageId: string,
  updates: Partial<Message>
): void {
  const convs = load();
  const conv = convs.find((c) => c.id === convId);
  if (!conv) return;
  const msg = conv.messages.find((m) => m.id === messageId);
  if (!msg) return;
  Object.assign(msg, updates);
  conv.updatedAt = Date.now();
  save(convs);
}

// Active conversation persistence
export function getActiveConversationId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACTIVE_KEY);
}

export function setActiveConversationId(id: string | null): void {
  if (typeof window === "undefined") return;
  if (id) {
    localStorage.setItem(ACTIVE_KEY, id);
  } else {
    localStorage.removeItem(ACTIVE_KEY);
  }
}
