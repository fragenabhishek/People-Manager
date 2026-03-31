"use client";
import { useState } from "react";
import { Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ai, ApiError } from "@/lib/api";

interface Message {
  role: "user" | "ai";
  content: string;
}

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;

    setMessages((m) => [...m, { role: "user", content: q }]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await ai.ask(q);
      setMessages((m) => [...m, { role: "ai", content: res.answer }]);
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "AI unavailable";
      setMessages((m) => [...m, { role: "ai", content: `Error: ${msg}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-3rem)] lg:h-[calc(100vh-3rem)]">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <Sparkles size={24} className="text-indigo-500" /> Ask AI
      </h1>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <Card className="text-center py-12 text-gray-500">
            <Sparkles size={32} className="mx-auto mb-3 text-indigo-400" />
            <p>Ask questions about your contacts.</p>
            <p className="text-sm mt-1">Examples: &ldquo;Who works in tech?&rdquo; &ldquo;Who should I follow up with?&rdquo;</p>
          </Card>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-md"
                  : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200 rounded-bl-md"
              }`}
            >
              {msg.role === "ai" ? (
                <div className="prose dark:prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: msg.content }} />
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div className="flex gap-1">
                <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                <div className="h-2 w-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask anything about your contacts..."
          className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2.5 text-sm dark:bg-gray-800 dark:text-white"
          disabled={loading}
        />
        <Button type="submit" disabled={loading || !question.trim()}>
          <Send size={16} />
        </Button>
      </form>
    </div>
  );
}
