"use client";

import { MessageSquare } from "lucide-react";

export function LoadingMessage() {
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0 mt-0.5">
        <MessageSquare className="w-4 h-4 text-white" />
      </div>

      {/* Typing indicator */}
      <div className="flex items-center gap-1.5 bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3 mt-0.5">
        <span className="text-xs text-gray-500 dark:text-gray-400 mr-1">
          NanoGPT
        </span>
        <span className="dot-1 w-2 h-2 rounded-full bg-brand-500 inline-block" />
        <span className="dot-2 w-2 h-2 rounded-full bg-brand-500 inline-block" />
        <span className="dot-3 w-2 h-2 rounded-full bg-brand-500 inline-block" />
      </div>
    </div>
  );
}
