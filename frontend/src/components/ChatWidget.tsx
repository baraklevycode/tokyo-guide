"use client";

import { useEffect, useRef, useState } from "react";
import ChatMessage from "./ChatMessage";
import SuggestedQuestions from "./SuggestedQuestions";
import {
  sendChatMessage,
  getSuggestions,
  type SourceReference,
} from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
}

const DEFAULT_SUGGESTIONS = [
  "מה כדאי לאכול בטוקיו?",
  "איפה הכי כדאי לישון?",
  "איך עובד המטרו בטוקיו?",
];

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>(DEFAULT_SUGGESTIONS);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load session ID from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("tokyo_chat_session_id");
    if (stored) setSessionId(stored);
  }, []);

  // Load suggestions from API
  useEffect(() => {
    async function loadSuggestions() {
      try {
        const data = await getSuggestions();
        if (data.suggestions.length > 0) {
          setSuggestions(data.suggestions.slice(0, 5));
        }
      } catch {
        // Keep default suggestions
      }
    }
    loadSuggestions();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen]);

  const handleSend = async (text?: string) => {
    const question = text || input.trim();
    if (!question || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(question, sessionId);

      // Save session ID
      if (response.session_id) {
        setSessionId(response.session_id);
        localStorage.setItem("tokyo_chat_session_id", response.session_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources,
        },
      ]);

      // Update suggestions with follow-up questions
      if (response.suggested_questions.length > 0) {
        setSuggestions(response.suggested_questions);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "מצטער, אירעה שגיאה. נסו שוב בעוד רגע.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Chat toggle button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 left-6 z-50 w-14 h-14 bg-pink-600 text-white rounded-full shadow-lg shadow-pink-300 hover:bg-pink-700 transition-all hover:scale-105 flex items-center justify-center"
        aria-label={isOpen ? "סגור צ׳אט" : "פתח צ׳אט"}
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        )}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="fixed bottom-24 left-6 z-50 w-[550px] max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-8rem)] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col animate-slide-up overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-l from-pink-600 to-rose-500 text-white px-4 py-3 flex items-center gap-3 shrink-0">
            <span className="text-xl">⛩️</span>
            <div>
              <h3 className="font-bold text-sm">מדריך טוקיו</h3>
              <p className="text-xs opacity-80">שאלו אותי הכל על טוקיו</p>
            </div>
          </div>

          {/* Messages area */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.length === 0 && (
              <div className="text-center text-gray-400 text-sm mt-8">
                <p className="text-2xl mb-2">🌸</p>
                <p>שלום! שאלו אותי כל שאלה על טוקיו.</p>
                <p className="mt-1">מסעדות, שכונות, תחבורה, קניות...</p>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatMessage
                key={i}
                role={msg.role}
                content={msg.content}
                sources={msg.sources}
              />
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="flex justify-end animate-fade-in">
                <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                    <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested questions */}
          {messages.length === 0 && (
            <SuggestedQuestions
              questions={suggestions.slice(0, 3)}
              onSelect={handleSend}
            />
          )}
          {messages.length > 0 && !loading && (
            <SuggestedQuestions
              questions={suggestions.slice(0, 3)}
              onSelect={handleSend}
            />
          )}

          {/* Input area */}
          <div className="border-t border-gray-100 p-3 shrink-0">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="שאלו שאלה על טוקיו..."
                className="flex-1 text-sm border border-gray-200 rounded-xl px-3 py-2.5 focus:outline-none focus:border-pink-400 focus:ring-1 focus:ring-pink-200 transition-colors"
                disabled={loading}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || loading}
                className="w-10 h-10 bg-pink-600 text-white rounded-xl hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center shrink-0"
                aria-label="שלח"
              >
                <svg className="w-5 h-5 rotate-180" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
