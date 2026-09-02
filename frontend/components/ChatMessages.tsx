"use client";

import { useEffect, useRef } from "react";
import type { Message } from "@/types/chat";
import { MessageBubble } from "./MessageBubble";
import { LoadingMessage } from "./LoadingMessage";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onRegenerate: () => void;
  onFeedback: (messageId: string, liked: boolean) => void;
  onRetry: () => void;
}

export function ChatMessages({
  messages,
  isLoading,
  error,
  onRegenerate,
  onFeedback,
  onRetry,
}: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, error]);

  const lastAssistantIdx = messages
    .map((m, i) => (m.role === "assistant" ? i : -1))
    .filter((i) => i >= 0)
    .pop();

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
      {messages.map((msg, idx) => (
        <MessageBubble
          key={msg.id}
          message={msg}
          isLastAssistant={idx === lastAssistantIdx}
          onRegenerate={onRegenerate}
          onFeedback={onFeedback}
        />
      ))}

      {isLoading && <LoadingMessage />}

      {error && !isLoading && (
        <div className="flex items-start gap-3 animate-fade-in">
          <div className="w-8 h-8 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center flex-shrink-0 mt-0.5">
            <AlertCircle className="w-4 h-4 text-red-500" />
          </div>
          <div className="flex-1">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-4 py-3">
              <p className="text-sm text-red-700 dark:text-red-400 font-medium mb-1">
                NanoGPT is currently unavailable
              </p>
              <p className="text-xs text-red-600 dark:text-red-500">
                {error.includes("fetch") || error.includes("network") || error.includes("Failed")
                  ? "Please make sure the backend server is running on port 8000."
                  : error}
              </p>
            </div>
            <button
              onClick={onRetry}
              className="mt-2 flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
