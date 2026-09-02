"use client";

import { Menu, Moon, Sun } from "lucide-react";

interface ChatHeaderProps {
  title: string;
  onMenuClick: () => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
}

export function ChatHeader({
  title,
  onMenuClick,
  theme,
  onToggleTheme,
}: ChatHeaderProps) {
  return (
    <header className="flex items-center gap-3 px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 z-10">
      {/* Mobile menu button */}
      <button
        onClick={onMenuClick}
        className="lg:hidden p-1.5 rounded-lg text-gray-500 hover:text-gray-800 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 transition-colors"
        aria-label="Open sidebar"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Title */}
      <div className="flex-1 min-w-0">
        <h1 className="text-sm font-semibold text-gray-900 dark:text-white truncate">
          {title}
        </h1>
        <p className="text-[11px] text-gray-400 dark:text-gray-500">
          Powered by NanoGPT · 5.24M params
        </p>
      </div>

      {/* Theme toggle (desktop, mirrored in sidebar on mobile) */}
      <button
        onClick={onToggleTheme}
        className="hidden lg:flex p-2 rounded-lg text-gray-500 hover:text-gray-800 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-white dark:hover:bg-gray-800 transition-colors"
        aria-label="Toggle theme"
      >
        {theme === "dark" ? (
          <Sun className="w-4 h-4" />
        ) : (
          <Moon className="w-4 h-4" />
        )}
      </button>
    </header>
  );
}
