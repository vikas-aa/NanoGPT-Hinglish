"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function MessageInput({ onSend, isLoading }: MessageInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
  }, [value]);

  // Focus on mount
  useEffect(() => {
    if (!isLoading) textareaRef.current?.focus();
  }, [isLoading]);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || isLoading) return;
    onSend(trimmed);
    setValue("");
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, isLoading, onSend]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const canSend = value.trim().length > 0 && !isLoading;

  return (
    <div className="max-w-3xl mx-auto w-full">
      <div
        className={`
          flex items-end gap-2 rounded-2xl border px-4 py-3
          bg-white dark:bg-gray-900
          transition-colors
          ${
            canSend
              ? "border-brand-400 dark:border-brand-600 shadow-sm shadow-brand-100 dark:shadow-brand-900/20"
              : "border-gray-200 dark:border-gray-700"
          }
        `}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message NanoGPT..."
          rows={1}
          disabled={isLoading}
          className="
            flex-1 resize-none bg-transparent outline-none
            text-sm text-gray-900 dark:text-gray-100
            placeholder:text-gray-400 dark:placeholder:text-gray-600
            disabled:opacity-50
            max-h-[180px] overflow-y-auto
            leading-relaxed
          "
        />

        <button
          onClick={handleSend}
          disabled={!canSend}
          aria-label="Send message"
          className={`
            w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0
            transition-all
            ${
              canSend
                ? "bg-brand-600 hover:bg-brand-700 active:bg-brand-800 text-white shadow-sm"
                : "bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-600 cursor-not-allowed"
            }
          `}
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

      <p className="text-center text-[11px] text-gray-400 dark:text-gray-600 mt-2">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
