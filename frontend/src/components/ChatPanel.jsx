import { useState } from "react";
import { api } from "../api/client.js";

export default function ChatPanel({ documentId }) {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "I've processed your document. Feel free to ask me any questions about it!" },
  ]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);

  const sendMessage = async (event) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text || sending) return;

    const history = messages.map(({ role, content }) => ({ role, content }));
    setMessages((current) => [...current, { role: "user", content: text }]);
    setDraft("");
    setSending(true);

    try {
      const { answer } = await api.sendChatMessage(documentId, text, history);
      setMessages((current) => [...current, { role: "assistant", content: answer }]);
    } catch (err) {
      setMessages((current) => [...current, { role: "assistant", content: `Sorry, something went wrong: ${err.message}` }]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <h2 className="mb-3 flex items-center gap-2 font-semibold">💬 Chat</h2>

      <div className="mb-3 flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                message.role === "user" ? "bg-brand-500 text-white" : ""
              }`}
              style={message.role === "assistant" ? { background: "var(--surface-muted)" } : undefined}
            >
              {message.content}
            </div>
          </div>
        ))}
        {sending && <p className="text-xs" style={{ color: "var(--text-muted)" }}>Thinking...</p>}
      </div>

      <form onSubmit={sendMessage} className="flex gap-2">
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Type your message..."
          className="flex-1 rounded-lg border px-3 py-2 text-sm outline-none focus:border-brand-400"
          style={{ borderColor: "var(--border)", background: "var(--surface-muted)", color: "var(--text)" }}
        />
        <button
          type="submit"
          disabled={sending}
          className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
