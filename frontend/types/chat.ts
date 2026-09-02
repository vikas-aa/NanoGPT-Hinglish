// ============================================================
// Core chat types
// ============================================================

export type Role = "user" | "assistant";

export interface Message {
  id: string;
  role: Role;
  content: string;
  createdAt: number;
  /** undefined = delivered, true = liked, false = disliked */
  feedback?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

// ============================================================
// API types
// ============================================================

export interface ApiMessage {
  role: Role;
  content: string;
}

export interface ChatApiRequest {
  messages: ApiMessage[];
  max_new_tokens?: number;
  temperature?: number;
  top_k?: number;
}

export interface ChatApiResponse {
  response: string;
}

export interface HealthApiResponse {
  status: string;
  model: string;
  device: string;
}

// ============================================================
// UI state
// ============================================================

export type LoadingState = "idle" | "loading" | "error";

export interface GenerationSettings {
  maxNewTokens: number;
  temperature: number;
  topK: number;
}

export const DEFAULT_SETTINGS: GenerationSettings = {
  maxNewTokens: 100,
  temperature: 0.8,
  topK: 50,
};
