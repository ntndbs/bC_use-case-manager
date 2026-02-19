import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { ChatResponse } from "../api/types";
import { useRefresh } from "../context/RefreshContext";

const MUTATING_TOOLS = new Set([
  "create_use_case",
  "update_use_case",
  "set_status",
  "archive_use_case",
  "restore_use_case",
  "analyze_transcript",
  "save_transcript",
  "create_company",
  "create_industry",
]);

const MAX_FILE_SIZE = 512_000; // 500 KB

interface Message {
  role: "user" | "assistant";
  text: string;
  toolCalls?: string[];
}

function generateSessionId() {
  return `s-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatPanel() {
  const { triggerRefresh } = useRefresh();
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = sessionStorage.getItem("chat_messages");
      return saved ? JSON.parse(saved) : [];
    } catch { return []; }
  });
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [sessionId] = useState(() => {
    const saved = sessionStorage.getItem("chat_session_id");
    if (saved) return saved;
    const id = generateSessionId();
    sessionStorage.setItem("chat_session_id", id);
    return id;
  });
  const [attachedFile, setAttachedFile] = useState<{ name: string; content: string } | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Persist messages to sessionStorage
  useEffect(() => {
    sessionStorage.setItem("chat_messages", JSON.stringify(messages));
  }, [messages]);

  // Auto-scroll on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = ""; // reset so same file can be selected again

    if (!file.name.endsWith(".txt")) {
      alert("Nur .txt-Dateien werden unterstützt.");
      return;
    }
    if (file.size === 0) {
      alert("Die Datei ist leer.");
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      alert("Datei ist zu groß (max. 500 KB).");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setAttachedFile({ name: file.name, content: reader.result as string });
    };
    reader.readAsText(file, "utf-8");
  }

  function handleClear() {
    setMessages([]);
    sessionStorage.removeItem("chat_messages");
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || sending) return;

    const displayText = attachedFile ? `${text}\n📎 ${attachedFile.name}` : text;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: displayText }]);
    setSending(true);

    const body: Record<string, string> = {
      message: text,
      session_id: sessionId,
    };
    if (attachedFile) {
      body.file_content = attachedFile.content;
      body.file_name = attachedFile.name;
    }
    setAttachedFile(null);

    try {
      const data = await api.post<ChatResponse>("/chat/", body);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.reply, toolCalls: data.tool_calls_made },
      ]);
      if (data.tool_calls_made.some((t) => MUTATING_TOOLS.has(t))) {
        triggerRefresh();
      }
    } catch (e: unknown) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `Fehler: ${e instanceof Error ? e.message : "Unbekannter Fehler"}` },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <aside className="w-[480px] border-l border-gray-200 bg-white flex flex-col shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h2 className="text-sm font-semibold text-gray-900">KI-Assistent</h2>
        {messages.length > 0 && (
          <button
            onClick={handleClear}
            className="text-gray-400 hover:text-red-500 p-1 transition-colors"
            title="Chat leeren"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </button>
        )}
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
        {/* Attached file badge */}
        {attachedFile && (
          <div className="flex items-center gap-2 mb-2 px-2 py-1 bg-blue-50 rounded-md text-sm text-blue-700">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clipRule="evenodd" />
            </svg>
            <span className="truncate flex-1">{attachedFile.name}</span>
            <button
              onClick={() => setAttachedFile(null)}
              className="text-blue-400 hover:text-blue-600 shrink-0"
            >
              &times;
            </button>
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex gap-2"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt"
            onChange={handleFileSelect}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={sending}
            className="px-2 py-2 text-gray-400 hover:text-gray-600 disabled:opacity-40 transition-colors"
            title="Datei anhängen (.txt)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clipRule="evenodd" />
            </svg>
          </button>
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
    </aside>
  );
}
