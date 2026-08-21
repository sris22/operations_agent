import { useState, useRef, useEffect, FormEvent } from "react";
import { sendMessage, getConversations, getConversationMessages } from "../services/api";
import type { Conversation, Message, SourceInfo, ToolExecutionInfo } from "../types";

export default function Chat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [toolExecutions, setToolExecutions] = useState<ToolExecutionInfo[]>([]);
  const [approvalPending, setApprovalPending] = useState<{ id: number; type: string } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    getConversations().then((res) => setConversations(res.conversations));
  }, []);

  useEffect(() => {
    if (activeConversationId) {
      getConversationMessages(activeConversationId).then((res) =>
        setMessages(res.messages)
      );
    }
  }, [activeConversationId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput("");
    setLoading(true);

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        role: "USER",
        content: userMessage,
        metadata_: null,
        created_at: new Date().toISOString(),
      },
    ]);

    try {
      const res = await sendMessage({
        conversation_id: activeConversationId ?? undefined,
        message: userMessage,
      });

      setActiveConversationId(res.conversation_id);
      setSources(res.sources);
      setToolExecutions(res.tool_executions);

      if (res.approval_required && res.approval_id) {
        setApprovalPending({ id: res.approval_id, type: "refund" });
      }

      setMessages((prev) => [
        ...prev,
        {
          id: res.message_id,
          role: "ASSISTANT",
          content: res.response,
          metadata_: { sources: res.sources, tool_executions: res.tool_executions },
          created_at: new Date().toISOString(),
        },
      ]);

      getConversations().then((r) => setConversations(r.conversations));
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "ASSISTANT",
          content: "Failed to process your message. Please try again.",
          metadata_: null,
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-layout">
      <aside className="chat-sidebar">
        <h3>Conversations</h3>
        <button
          className="btn btn-primary btn-full"
          onClick={() => {
            setActiveConversationId(null);
            setMessages([]);
            setSources([]);
            setToolExecutions([]);
            setApprovalPending(null);
          }}
        >
          New Conversation
        </button>
        <div className="conversation-list">
          {conversations.map((c) => (
            <div
              key={c.id}
              className={`conversation-item ${c.id === activeConversationId ? "active" : ""}`}
              onClick={() => setActiveConversationId(c.id)}
            >
              <span className="conv-id">#{c.id}</span>
              <span className="conv-status">{c.status}</span>
              <span className="conv-date">
                {new Date(c.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </aside>

      <main className="chat-main">
        <div className="messages-area">
          {messages.length === 0 && (
            <div className="empty-state">
              <h3>AI Customer Operations Agent</h3>
              <p>Start a conversation to get help with customer issues.</p>
            </div>
          )}
          {messages.map((m) => (
            <div key={m.id} className={`message message-${m.role.toLowerCase()}`}>
              <div className="message-role">{m.role === "USER" ? "You" : "Agent"}</div>
              <div className="message-content">{m.content}</div>
            </div>
          ))}
          {loading && (
            <div className="message message-assistant">
              <div className="message-role">Agent</div>
              <div className="message-content typing">Processing...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input" onSubmit={handleSend}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe the customer issue..."
            disabled={loading}
          />
          <button type="submit" className="btn btn-primary" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </main>

      <aside className="chat-trace">
        {approvalPending && (
          <div className="trace-section approval-alert">
            <h4>Approval Required</h4>
            <p>#{approvalPending.id} — {approvalPending.type}</p>
            <a href="/approvals" className="btn btn-sm">Go to Approvals</a>
          </div>
        )}

        {toolExecutions.length > 0 && (
          <div className="trace-section">
            <h4>Tool Activity</h4>
            {toolExecutions.map((t, i) => (
              <div key={i} className="trace-item">
                <span className={`trace-status ${t.status === "SUCCESS" ? "ok" : "fail"}`}>
                  {t.status === "SUCCESS" ? "check" : "x"}
                </span>
                <span>{t.tool_name}</span>
              </div>
            ))}
          </div>
        )}

        {sources.length > 0 && (
          <div className="trace-section">
            <h4>Retrieved Sources</h4>
            {sources.map((s, i) => (
              <div key={i} className="trace-item source">
                <strong>{s.document_name}</strong>
                <span className="similarity">
                  {(s.similarity_score * 100).toFixed(0)}% match
                </span>
                <p className="source-preview">
                  {s.content.substring(0, 120)}...
                </p>
              </div>
            ))}
          </div>
        )}
      </aside>
    </div>
  );
}
