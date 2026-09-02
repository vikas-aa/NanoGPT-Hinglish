"use client";

import { useEffect, useRef, useState } from "react";
import {
  MessageSquare,
  Plus,
  Pencil,
  Trash2,
  X,
  Sun,
  Moon,
  SlidersHorizontal,
  Check,
} from "lucide-react";
import type { Conversation, GenerationSettings } from "@/types/chat";

interface SidebarProps {
  conversations: Conversation[];
  activeConvId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onNewChat: () => void;
  onSelectConv: (id: string) => void;
  onDeleteConv: (id: string) => void;
  onRenameConv: (id: string, title: string) => void;
  theme: "light" | "dark";
  onToggleTheme: () => void;
  settings: GenerationSettings;
  onSettingsChange: (s: GenerationSettings) => void;
}

export function Sidebar({
  conversations,
  activeConvId,
  isOpen,
  onClose,
  onNewChat,
  onSelectConv,
  onDeleteConv,
  onRenameConv,
  theme,
  onToggleTheme,
  settings,
  onSettingsChange,
}: SidebarProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [menuOpenId, setMenuOpenId] = useState<string | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const editRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingId && editRef.current) editRef.current.focus();
  }, [editingId]);

  function startEdit(conv: Conversation) {
    setEditingId(conv.id);
    setEditTitle(conv.title);
    setMenuOpenId(null);
  }

  function commitEdit(id: string) {
    if (editTitle.trim()) onRenameConv(id, editTitle);
    setEditingId(null);
  }

  function formatDate(ts: number): string {
    const d = new Date(ts);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const days = Math.floor(diff / 86400000);
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    return d.toLocaleDateString();
  }

  return (
    <aside
      className={`
        fixed top-0 left-0 z-30 h-screen flex flex-col
        w-[260px] bg-gray-50 dark:bg-gray-900
        border-r border-gray-200 dark:border-gray-800
        transition-transform duration-250 ease-out
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
        lg:relative lg:translate-x-0 lg:flex
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-brand-600 flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-gray-900 dark:text-white tracking-tight">
            NanoGPT
          </span>
        </div>
        <button
          onClick={onClose}
          className="lg:hidden text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors p-1 rounded"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* New chat button */}
      <div className="px-3 py-3">
        <button
          onClick={onNewChat}
          className="
            w-full flex items-center gap-2 px-3 py-2.5 rounded-lg
            bg-brand-600 hover:bg-brand-700 active:bg-brand-800
            text-white text-sm font-medium transition-colors
          "
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-0.5">
        {conversations.length === 0 ? (
          <p className="text-xs text-gray-400 dark:text-gray-600 text-center mt-6">
            No conversations yet
          </p>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conv={conv}
              isActive={conv.id === activeConvId}
              isEditing={editingId === conv.id}
              editTitle={editTitle}
              isMenuOpen={menuOpenId === conv.id}
              editRef={editRef}
              onSelect={() => onSelectConv(conv.id)}
              onStartEdit={() => startEdit(conv)}
              onEditChange={(v) => setEditTitle(v)}
              onCommitEdit={() => commitEdit(conv.id)}
              onDelete={() => { onDeleteConv(conv.id); setMenuOpenId(null); }}
              onToggleMenu={() =>
                setMenuOpenId(menuOpenId === conv.id ? null : conv.id)
              }
              formatDate={formatDate}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 dark:border-gray-800 px-3 py-3 space-y-1">
        {/* Settings toggle */}
        <button
          onClick={() => setShowSettings((p) => !p)}
          className="
            w-full flex items-center gap-2 px-3 py-2 rounded-lg
            text-sm text-gray-600 dark:text-gray-400
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
          "
        >
          <SlidersHorizontal className="w-4 h-4" />
          Generation Settings
        </button>

        {showSettings && (
          <SettingsPanel settings={settings} onChange={onSettingsChange} />
        )}

        {/* Theme toggle */}
        <button
          onClick={onToggleTheme}
          className="
            w-full flex items-center gap-2 px-3 py-2 rounded-lg
            text-sm text-gray-600 dark:text-gray-400
            hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
          "
        >
          {theme === "dark" ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </button>
      </div>
    </aside>
  );
}

// ============================================================
// Conversation item
// ============================================================
interface ConvItemProps {
  conv: Conversation;
  isActive: boolean;
  isEditing: boolean;
  editTitle: string;
  isMenuOpen: boolean;
  editRef: React.RefObject<HTMLInputElement>;
  onSelect: () => void;
  onStartEdit: () => void;
  onEditChange: (v: string) => void;
  onCommitEdit: () => void;
  onDelete: () => void;
  onToggleMenu: () => void;
  formatDate: (ts: number) => string;
}

function ConversationItem({
  conv,
  isActive,
  isEditing,
  editTitle,
  isMenuOpen,
  editRef,
  onSelect,
  onStartEdit,
  onEditChange,
  onCommitEdit,
  onDelete,
  onToggleMenu,
  formatDate,
}: ConvItemProps) {
  return (
    <div className="relative group">
      <div
        className={`
          flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer
          transition-colors select-none
          ${
            isActive
              ? "bg-brand-50 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300"
              : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
          }
        `}
        onClick={onSelect}
      >
        <MessageSquare className="w-3.5 h-3.5 flex-shrink-0 opacity-60" />

        {isEditing ? (
          <input
            ref={editRef}
            value={editTitle}
            onChange={(e) => onEditChange(e.target.value)}
            onBlur={onCommitEdit}
            onKeyDown={(e) => {
              if (e.key === "Enter") onCommitEdit();
              if (e.key === "Escape") onCommitEdit();
            }}
            onClick={(e) => e.stopPropagation()}
            className="
              flex-1 min-w-0 bg-white dark:bg-gray-700 text-gray-900 dark:text-white
              text-sm px-1 py-0.5 rounded border border-brand-400 outline-none
            "
          />
        ) : (
          <div className="flex-1 min-w-0">
            <p className="text-sm truncate">{conv.title}</p>
            <p className="text-[11px] opacity-50 mt-0.5">
              {formatDate(conv.updatedAt)}
            </p>
          </div>
        )}

        {/* Menu button */}
        {!isEditing && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onToggleMenu();
            }}
            className="
              opacity-0 group-hover:opacity-100 p-1 rounded
              text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white
              transition-opacity
            "
          >
            <svg
              className="w-3.5 h-3.5"
              fill="currentColor"
              viewBox="0 0 16 16"
            >
              <circle cx="8" cy="3" r="1.5" />
              <circle cx="8" cy="8" r="1.5" />
              <circle cx="8" cy="13" r="1.5" />
            </svg>
          </button>
        )}
      </div>

      {/* Dropdown menu */}
      {isMenuOpen && (
        <div
          className="
            absolute right-0 top-full mt-1 z-50 w-36
            bg-white dark:bg-gray-800 rounded-lg shadow-lg
            border border-gray-200 dark:border-gray-700 py-1 animate-fade-in
          "
        >
          <button
            onClick={(e) => {
              e.stopPropagation();
              onStartEdit();
            }}
            className="
              w-full flex items-center gap-2 px-3 py-2
              text-sm text-gray-700 dark:text-gray-300
              hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors
            "
          >
            <Pencil className="w-3.5 h-3.5" />
            Rename
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            className="
              w-full flex items-center gap-2 px-3 py-2
              text-sm text-red-600 dark:text-red-400
              hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors
            "
          >
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

// ============================================================
// Settings panel
// ============================================================
function SettingsPanel({
  settings,
  onChange,
}: {
  settings: GenerationSettings;
  onChange: (s: GenerationSettings) => void;
}) {
  return (
    <div className="px-3 py-3 bg-gray-100 dark:bg-gray-800 rounded-lg space-y-3 text-xs">
      <label className="flex flex-col gap-1">
        <div className="flex justify-between text-gray-600 dark:text-gray-400">
          <span>Max tokens</span>
          <span className="font-mono">{settings.maxNewTokens}</span>
        </div>
        <input
          type="range"
          min={10}
          max={300}
          step={10}
          value={settings.maxNewTokens}
          onChange={(e) =>
            onChange({ ...settings, maxNewTokens: Number(e.target.value) })
          }
          className="accent-brand-600"
        />
      </label>

      <label className="flex flex-col gap-1">
        <div className="flex justify-between text-gray-600 dark:text-gray-400">
          <span>Temperature</span>
          <span className="font-mono">{settings.temperature.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min={0.1}
          max={1.5}
          step={0.05}
          value={settings.temperature}
          onChange={(e) =>
            onChange({ ...settings, temperature: Number(e.target.value) })
          }
          className="accent-brand-600"
        />
      </label>

      <label className="flex flex-col gap-1">
        <div className="flex justify-between text-gray-600 dark:text-gray-400">
          <span>Top-K</span>
          <span className="font-mono">{settings.topK}</span>
        </div>
        <input
          type="range"
          min={1}
          max={100}
          step={1}
          value={settings.topK}
          onChange={(e) =>
            onChange({ ...settings, topK: Number(e.target.value) })
          }
          className="accent-brand-600"
        />
      </label>
    </div>
  );
}
