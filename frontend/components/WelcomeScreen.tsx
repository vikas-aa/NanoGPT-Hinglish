"use client";

import { MessageSquare, Sparkles } from "lucide-react";

interface WelcomeScreenProps {
  onSend: (message: string) => void;
}

const EXAMPLE_PROMPTS = [
  { label: "Python kya hai?", emoji: "🐍" },
  { label: "Mujhe ek joke sunao", emoji: "😄" },
  { label: "Machine learning simple language mein samjhao", emoji: "🤖" },
  { label: "Aaj kya kar rahe ho?", emoji: "💬" },
  { label: "JavaScript vs Python — kya better hai?", emoji: "⚡" },
  { label: "Ek short story sunao Hindi mein", emoji: "📖" },
];

export function WelcomeScreen({ onSend }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-full py-16 px-6 text-center animate-fade-in">
      {/* Logo */}
      <div className="w-16 h-16 rounded-2xl bg-brand-600 flex items-center justify-center mb-5 shadow-lg shadow-brand-200 dark:shadow-brand-900/40">
        <MessageSquare className="w-8 h-8 text-white" />
      </div>

      {/* Heading */}
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 tracking-tight">
        NanoGPT
      </h2>
      <p className="text-gray-500 dark:text-gray-400 text-sm mb-1">
        Your personal Hinglish AI assistant.
      </p>
      <p className="text-gray-400 dark:text-gray-600 text-xs mb-8 flex items-center gap-1.5">
        <Sparkles className="w-3 h-3" />
        5.24M params · Trained on Roman Hinglish
      </p>

      {/* Example prompts */}
      <div className="w-full max-w-xl">
        <p className="text-xs text-gray-400 dark:text-gray-600 mb-3 uppercase tracking-wide font-medium">
          Try asking
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {EXAMPLE_PROMPTS.map((p) => (
            <button
              key={p.label}
              onClick={() => onSend(p.label)}
              className="
                flex items-center gap-2.5 px-4 py-3 rounded-xl text-left
                bg-gray-50 dark:bg-gray-900
                border border-gray-200 dark:border-gray-800
                hover:border-brand-300 dark:hover:border-brand-700
                hover:bg-brand-50 dark:hover:bg-brand-900/20
                transition-colors group
              "
            >
              <span className="text-lg flex-shrink-0">{p.emoji}</span>
              <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-brand-700 dark:group-hover:text-brand-400 transition-colors">
                {p.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
