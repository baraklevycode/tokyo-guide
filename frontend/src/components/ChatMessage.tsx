import type { SourceReference } from "@/lib/api";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  sources?: SourceReference[];
}

export default function ChatMessage({
  role,
  content,
  sources,
}: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-start" : "justify-end"} animate-slide-up`}
    >
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-pink-600 text-white rounded-br-sm"
            : "bg-gray-100 text-gray-800 rounded-bl-sm"
        }`}
      >
        {/* Avatar indicator */}
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs font-medium opacity-70">
            {isUser ? "אתם" : "⛩️ מדריך טוקיו"}
          </span>
        </div>

        {/* Message content */}
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}
        </div>

        {/* Source references (only for assistant messages) */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200">
            <p className="text-xs text-gray-500 mb-1">מקורות:</p>
            <div className="flex flex-wrap gap-1">
              {sources.map((source) => (
                <span
                  key={source.id}
                  className="text-xs bg-white text-gray-600 px-2 py-0.5 rounded-full border border-gray-200"
                >
                  {source.title_hebrew}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
