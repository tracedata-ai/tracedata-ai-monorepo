"use client";

import React, { useState } from "react";

export default function ChatbotPage() {
  const [messages, setMessages] = useState<
    { role: "user" | "assistant"; content: string }[]
  >([]);
  const [input, setInput] = useState("");

  const sendQuery = async () => {
    if (!input.trim()) return;

    // Optimistic UI update
    setMessages((prev) => [...prev, { role: "user", content: input }]);
    setInput("");

    // Placeholder response simulation
    try {
      // Future API integration:
      // const response = await apiClient.post('/api/chat', { query: input });
      // const answer = response.data.answer;

      const answer =
        "I'm still learning! Ask me about fleet regulations or policies soon.";

      setMessages((prev) => [
        ...prev,
        { role: "user", content: input },
        { role: "assistant", content: answer },
      ]);
    } catch (error) {
      console.error("Failed to fetch response:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error." },
      ]);
    }
  };

  return (
    <div className="flex flex-col h-screen p-4 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-center">
        TraceData Fleet Assistant
      </h1>

      <div className="flex-1 overflow-y-auto mb-4 border rounded p-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 p-2 rounded-lg ${msg.role === "user" ? "bg-blue-100 self-end ml-12 text-right" : "bg-white self-start mr-12 border"}`}
          >
            <p className="text-sm font-semibold mb-1">
              {msg.role === "user" ? "You" : "Assistant"}
            </p>
            <p>{msg.content}</p>
          </div>
        ))}
        {messages.length === 0 && (
          <p className="text-gray-400 text-center mt-20">
            Ask me anything about fleet policies...
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question..."
          className="flex-1 border rounded px-4 py-2"
          onKeyDown={(e) => e.key === "Enter" && sendQuery()}
        />
        <button
          onClick={sendQuery}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Send
        </button>
      </div>
    </div>
  );
}
