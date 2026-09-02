"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import {
  Copy,
  Check,
  RefreshCw,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  User,
} from "lucide-react";
import type { Message } from "@/types/chat";

interface MessageBubbleProps {
  message: Message;
  isLastAssistant: boolean;
  onRegenerate: () => void;
  onFeedback: (messageId: string, liked: boolean) => void;
}

export function MessageBubble({
  message,
  isLastAssistant,
  onRegenerate,
  onFeedback,
}: MessageBubbleProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(message.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  if (isUser) {
    return (
      <div className="flex items-start gap-3 justify-end animate-fade-in">
        <div className="max-w-[80%]">
          <div className="bg-brand-600 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </p>
          </div>
        </div>
        <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center flex-shrink-0 mt-0.5">
          <User className="w-4 h-4 text-gray-600 dark:text-gray-400" />
        </div>
      </div>
    );
  }

  // Assistant message
  return (
    <div className="flex items-start gap-3 animate-fade-in">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0 mt-0.5">
        <MessageSquare className="w-4 h-4 text-white" />
      </div>

      <div className="flex-1 min-w-0">
        {/* Content */}
        <div className="prose-chat text-gray-800 dark:text-gray-200">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || "");
                const isBlock = !!(node?.position && (node.position.end.line - node.position.start.line) > 0);

                if (isBlock && match) {
                  return (
                    <CodeBlock
                      language={match[1]}
                      code={String(children).replace(/\n$/, "")}
                    />
                  );
                }

                return (
                  <code
                    className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm font-mono"
                    {...props}
                  >
                    {children}
                  </code>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Action bar */}
        <div className="flex items-center gap-1 mt-2">
          {/* Copy */}
          <ActionButton
            onClick={handleCopy}
            label={copied ? "Copied" : "Copy"}
            icon={
              copied ? (
                <Check className="w-3.5 h-3.5 text-green-500" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )
            }
          />

          {/* Regenerate (only on last assistant message) */}
          {isLastAssistant && (
            <ActionButton
              onClick={onRegenerate}
              label="Regenerate"
              icon={<RefreshCw className="w-3.5 h-3.5" />}
            />
          )}

          {/* Feedback */}
          <ActionButton
            onClick={() => onFeedback(message.id, true)}
            label="Good response"
            icon={
              <ThumbsUp
                className={`w-3.5 h-3.5 ${
                  message.feedback === true
                    ? "text-green-500 fill-green-500"
                    : ""
                }`}
              />
            }
          />
          <ActionButton
            onClick={() => onFeedback(message.id, false)}
            label="Bad response"
            icon={
              <ThumbsDown
                className={`w-3.5 h-3.5 ${
                  message.feedback === false
                    ? "text-red-500 fill-red-500"
                    : ""
                }`}
              />
            }
          />
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Action button
// ============================================================
function ActionButton({
  onClick,
  label,
  icon,
}: {
  onClick: () => void;
  label: string;
  icon: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className="
        p-1.5 rounded-md text-gray-400 hover:text-gray-700
        dark:text-gray-600 dark:hover:text-gray-300
        hover:bg-gray-100 dark:hover:bg-gray-800
        transition-colors
      "
    >
      {icon}
    </button>
  );
}

// ============================================================
// Code block with copy button + syntax highlighting
// ============================================================
function CodeBlock({
  language,
  code,
}: {
  language: string;
  code: string;
}) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  // Detect dark mode from the <html> class
  const isDark =
    typeof document !== "undefined" &&
    document.documentElement.classList.contains("dark");

  return (
    <div className="relative group rounded-lg overflow-hidden my-2 border border-gray-200 dark:border-gray-700">
      {/* Header bar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
          {language}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-white transition-colors"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-green-500" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy
            </>
          )}
        </button>
      </div>

      <SyntaxHighlighter
        language={language}
        style={isDark ? oneDark : oneLight}
        customStyle={{
          margin: 0,
          borderRadius: 0,
          fontSize: "0.8125rem",
        }}
        PreTag="div"
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}
