"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import { Sidebar } from "./Sidebar";
import { ChatHeader } from "./ChatHeader";
import { ChatMessages } from "./ChatMessages";
import { MessageInput } from "./MessageInput";
import { WelcomeScreen } from "./WelcomeScreen";

import { sendMessage } from "@/lib/api";
import {
  addMessage,
  createConversation,
  deleteConversation,
  getAllConversations,
  getActiveConversationId,
  getConversation,
  renameConversation,
  saveConversation,
  setActiveConversationId,
  updateMessage,
} from "@/lib/storage";
import type {
  Conversation,
  GenerationSettings,
  LoadingState,
  Message,
} from "@/types/chat";
import { DEFAULT_SETTINGS } from "@/types/chat";

export function ChatLayout() {
  // ----------------------------------------------------------------
  // State
  // ----------------------------------------------------------------
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvId, setActiveConvId] = useState<string | null>(null);
  const [activeConv, setActiveConv] = useState<Conversation | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [settings, setSettings] = useState<GenerationSettings>(DEFAULT_SETTINGS);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const abortRef = useRef<AbortController | null>(null);

  // ----------------------------------------------------------------
  // Init from localStorage
  // ----------------------------------------------------------------
  useEffect(() => {
    const savedTheme = localStorage.getItem("nanogpt_theme") as
      | "light"
      | "dark"
      | null;
    if (savedTheme) {
      setTheme(savedTheme);
      if (savedTheme === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      setTheme("dark");
    }

    const convs = getAllConversations();
    setConversations(convs);

    const savedId = getActiveConversationId();
    if (savedId) {
      const found = convs.find((c) => c.id === savedId);
      if (found) {
        setActiveConvId(found.id);
        setActiveConv(found);
      }
    }
  }, []);

  // ----------------------------------------------------------------
  // Theme toggle
  // ----------------------------------------------------------------
  const toggleTheme = useCallback(() => {
    setTheme((prev) => {
      const next = prev === "light" ? "dark" : "light";
      localStorage.setItem("nanogpt_theme", next);
      if (next === "dark") {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      return next;
    });
  }, []);

  // ----------------------------------------------------------------
  // Refresh helpers
  // ----------------------------------------------------------------
  const refreshConversations = useCallback(() => {
    setConversations(getAllConversations());
  }, []);

  const refreshActive = useCallback((id: string) => {
    const conv = getConversation(id);
    if (conv) setActiveConv({ ...conv });
  }, []);

  // ----------------------------------------------------------------
  // New chat
  // ----------------------------------------------------------------
  const handleNewChat = useCallback(() => {
    const conv = createConversation();
    setActiveConvId(conv.id);
    setActiveConv(conv);
    setActiveConversationId(conv.id);
    setError(null);
    refreshConversations();
    setSidebarOpen(false);
  }, [refreshConversations]);

  // ----------------------------------------------------------------
  // Select conversation
  // ----------------------------------------------------------------
  const handleSelectConv = useCallback(
    (id: string) => {
      const conv = getConversation(id);
      if (!conv) return;
      setActiveConvId(id);
      setActiveConv(conv);
      setActiveConversationId(id);
      setError(null);
      setSidebarOpen(false);
    },
    []
  );

  // ----------------------------------------------------------------
  // Delete conversation
  // ----------------------------------------------------------------
  const handleDeleteConv = useCallback(
    (id: string) => {
      deleteConversation(id);
      if (activeConvId === id) {
        setActiveConvId(null);
        setActiveConv(null);
        setActiveConversationId(null);
      }
      refreshConversations();
    },
    [activeConvId, refreshConversations]
  );

  // ----------------------------------------------------------------
  // Rename conversation
  // ----------------------------------------------------------------
  const handleRenameConv = useCallback(
    (id: string, title: string) => {
      renameConversation(id, title);
      if (activeConvId === id) {
        refreshActive(id);
      }
      refreshConversations();
    },
    [activeConvId, refreshActive, refreshConversations]
  );

  // ----------------------------------------------------------------
  // Send message
  // ----------------------------------------------------------------
  const handleSend = useCallback(
    async (content: string) => {
      if (!content.trim() || loadingState === "loading") return;

      setError(null);

      // Get or create active conversation
      let convId = activeConvId;
      let conv: Conversation;

      if (!convId) {
        conv = createConversation();
        convId = conv.id;
        setActiveConvId(convId);
        setActiveConv(conv);
        setActiveConversationId(convId);
        refreshConversations();
      } else {
        conv = getConversation(convId) ?? createConversation();
      }

      // Add user message
      const userMsg: Message = {
        id: uuidv4(),
        role: "user",
        content: content.trim(),
        createdAt: Date.now(),
      };

      const updatedConv = addMessage(convId, userMsg);
      if (updatedConv) {
        setActiveConv({ ...updatedConv });
        refreshConversations();
      }

      // Generate assistant response
      setLoadingState("loading");

      try {
        const currentConv = getConversation(convId);
        const historyMessages = currentConv?.messages ?? [];

        const response = await sendMessage(historyMessages, {
          maxNewTokens: settings.maxNewTokens,
          temperature: settings.temperature,
          topK: settings.topK,
        });

        const assistantMsg: Message = {
          id: uuidv4(),
          role: "assistant",
          content: response,
          createdAt: Date.now(),
        };

        const finalConv = addMessage(convId, assistantMsg);
        if (finalConv) {
          setActiveConv({ ...finalConv });
          refreshConversations();
        }
      } catch (err) {
        const msg =
          err instanceof Error ? err.message : "An unknown error occurred";
        setError(msg);
      } finally {
        setLoadingState("idle");
      }
    },
    [
      activeConvId,
      loadingState,
      settings,
      refreshConversations,
    ]
  );

  // ----------------------------------------------------------------
  // Regenerate last response
  // ----------------------------------------------------------------
  const handleRegenerate = useCallback(async () => {
    if (!activeConvId || !activeConv || loadingState === "loading") return;

    const messages = activeConv.messages;
    if (messages.length < 1) return;

    // Find the last assistant message and remove it
    const lastAssistantIdx = [...messages]
      .reverse()
      .findIndex((m) => m.role === "assistant");
    if (lastAssistantIdx < 0) return;

    const realIdx = messages.length - 1 - lastAssistantIdx;
    const trimmed = messages.slice(0, realIdx);

    const conv = getConversation(activeConvId);
    if (!conv) return;

    const updatedConv: Conversation = {
      ...conv,
      messages: trimmed,
      updatedAt: Date.now(),
    };

    saveConversation(updatedConv);
    setActiveConv({ ...updatedConv });
    setError(null);
    setLoadingState("loading");

    try {
      const response = await sendMessage(trimmed, {
        maxNewTokens: settings.maxNewTokens,
        temperature: settings.temperature,
        topK: settings.topK,
      });

      const assistantMsg: Message = {
        id: uuidv4(),
        role: "assistant",
        content: response,
        createdAt: Date.now(),
      };

      const finalConv = addMessage(activeConvId, assistantMsg);
      if (finalConv) {
        setActiveConv({ ...finalConv });
        refreshConversations();
      }
    } catch (err) {
      const msg =
        err instanceof Error ? err.message : "An unknown error occurred";
      setError(msg);
    } finally {
      setLoadingState("idle");
    }
  }, [activeConvId, activeConv, loadingState, settings, refreshConversations]);

  // ----------------------------------------------------------------
  // Message feedback
  // ----------------------------------------------------------------
  const handleFeedback = useCallback(
    (messageId: string, liked: boolean) => {
      if (!activeConvId) return;
      updateMessage(activeConvId, messageId, { feedback: liked });
      refreshActive(activeConvId);
    },
    [activeConvId, refreshActive]
  );

  // ----------------------------------------------------------------
  // Retry on error
  // ----------------------------------------------------------------
  const handleRetry = useCallback(() => {
    if (!activeConv) return;
    const lastUser = [...activeConv.messages]
      .reverse()
      .find((m) => m.role === "user");
    if (lastUser) handleSend(lastUser.content);
  }, [activeConv, handleSend]);

  // ----------------------------------------------------------------
  // Render
  // ----------------------------------------------------------------
  const hasMessages = (activeConv?.messages.length ?? 0) > 0;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-white dark:bg-gray-950">
      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConvId={activeConvId}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNewChat={handleNewChat}
        onSelectConv={handleSelectConv}
        onDeleteConv={handleDeleteConv}
        onRenameConv={handleRenameConv}
        theme={theme}
        onToggleTheme={toggleTheme}
        settings={settings}
        onSettingsChange={setSettings}
      />

      {/* Main area */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <ChatHeader
          title={activeConv?.title ?? "NanoGPT"}
          onMenuClick={() => setSidebarOpen(true)}
          theme={theme}
          onToggleTheme={toggleTheme}
        />

        <main className="flex-1 overflow-y-auto">
          {hasMessages ? (
            <ChatMessages
              messages={activeConv!.messages}
              isLoading={loadingState === "loading"}
              error={error}
              onRegenerate={handleRegenerate}
              onFeedback={handleFeedback}
              onRetry={handleRetry}
            />
          ) : (
            <WelcomeScreen onSend={handleSend} />
          )}
        </main>

        <div className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 px-4 py-3">
          <MessageInput
            onSend={handleSend}
            isLoading={loadingState === "loading"}
          />
        </div>
      </div>

      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}
