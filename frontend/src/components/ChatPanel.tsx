import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { ChatResponse } from "../api/types";
import { useRefresh } from "../context/RefreshContext";

const MUTATING_TOOLS = new Set([
  "create_use_case",
  "update_use_case",
  "set_status",
  "archive_use_case",
  "analyze_transcript",
]);

interface Message {
  role: "user" | "assistant";
  text: string;
  toolCalls?: string[];
}

interface Props {
  open: boolean;
  onClose: () => void;
}

function generateSessionId() {
  return `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatPanel({ open, onClose }: Props) {
  const { triggerRefresh } = useRefresh();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (open) inputRef.current?.focus();
  }, [open]);

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", text }]);
    setSending(true);

    try {
      const data = await api.post<ChatResponse>("/chat/", {
        message: text,
        session_id: sessionId,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply, toolCalls: data.tool_calls_made },
      ]);
      if (data.tool_calls_made.some((t) => MUTATING_TOOLS.has(t))) {
        triggerRefresh();
      }
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Fehler: ${e.message}` },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <>
      {/* Backdrop */}
      {open && (
        <div
          className="fixed inset-0 bg-black/20 z-40"
          onClick={onClose}
        />
      )}

      {/* Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-full max-w-md bg-white border-l border-gray-200 shadow-xl z-50 flex flex-col transition-transform duration-200 ${
          open ? "translate-x-0" : "translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-900">KI-Assistent</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-lg leading-none"
          >
            &times;
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 && (
            <p className="text-sm text-gray-400 text-center mt-8">
              Stell dem Agenten eine Frage, z.B.<br />
              &ldquo;Welche Use Cases gibt es?&rdquo;
            </p>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.toolCalls && msg.toolCalls.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200/50">
                    <p className="text-xs text-gray-500">
                      Tools: {msg.toolCalls.join(", ")}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}

          {sending && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm text-gray-500">
                Denkt nach...
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 px-4 py-3">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nachricht eingeben..."
              disabled={sending}
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-40 transition-colors"
            >
              Senden
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
