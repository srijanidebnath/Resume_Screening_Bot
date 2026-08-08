import { useEffect, useRef, useState } from "react";
import Sidebar from "../components/Sidebar.jsx";
import MessageBubble from "../components/MessageBubble.jsx";
import FileUploader from "../components/FileUploader.jsx";
import { listChats, createChat, deleteChat, getChat, submitFeedback, streamQuery } from "../api.js";

const SCREEN_KEYWORDS = ["screen", "evaluate", "assess", "review", "match"];

function localChat(id) {
  return { id, title: `Chat ${id}`, created_at: new Date().toISOString(), messages: [] };
}

export default function ChatPage() {
  const [backendOnline, setBackendOnline] = useState(true);
  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [resumeFiles, setResumeFiles] = useState([]);
  const [streamingText, setStreamingText] = useState(null);
  const scrollRef = useRef(null);

  // Try the real backend; if it's not up yet, fall back to a local-only
  // session so you can build/style the UI before FastAPI exists.
  useEffect(() => {
    (async () => {
      try {
        const remoteChats = await listChats();
        setBackendOnline(true);
        if (remoteChats.length) {
          setChats(remoteChats);
          setActiveChatId(remoteChats[0].id);
          const full = await getChat(remoteChats[0].id);
          setMessages(full.messages || []);
        } else {
          const chat = await createChat();
          setChats([chat]);
          setActiveChatId(chat.id);
          setMessages([]);
        }
      } catch {
        setBackendOnline(false);
        const chat = localChat(1);
        setChats([chat]);
        setActiveChatId(1);
        setMessages([]);
      }
    })();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streamingText]);

  async function handleNewChat() {
    setResumeFiles([]);
    if (!backendOnline) {
      const id = Math.max(0, ...chats.map((c) => c.id)) + 1;
      const chat = localChat(id);
      setChats((prev) => [chat, ...prev]);
      setActiveChatId(id);
      setMessages([]);
      return;
    }
    const chat = await createChat();
    setChats((prev) => [chat, ...prev]);
    setActiveChatId(chat.id);
    setMessages([]);
  }

  async function handleDeleteChat(id) {
    setChats((prev) => prev.filter((c) => c.id !== id));
    if (backendOnline) await deleteChat(id).catch(() => {});
    if (id === activeChatId) {
      const remaining = chats.filter((c) => c.id !== id);
      if (remaining.length) {
        handleSelectChat(remaining[0].id);
      } else {
        handleNewChat();
      }
    }
  }

  async function handleSelectChat(id) {
    setActiveChatId(id);
    setResumeFiles([]);

    if (!backendOnline) {
      setMessages([]);
      return;
    }

    // Selecting a chat shouldn't feel like it wiped history while it loads,
    // but it also shouldn't show the *previous* chat's messages during the
    // fetch, so clear first.
    setMessages([]);
    try {
      const full = await getChat(id);
      // Guard against a stale response landing after the user clicked
      // to another chat again before this resolved.
      setActiveChatId((current) => {
        if (current === id) setMessages(full.messages || []);
        return current;
      });
    } catch {
      setMessages([
        { role: "assistant", content: "⚠️ Couldn't load this chat's history." },
      ]);
    }
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || streamingText !== null) return;

    const shouldAttachResumes =
      resumeFiles.length > 0 && SCREEN_KEYWORDS.some((k) => text.toLowerCase().includes(k));

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setStreamingText("");

    if (!backendOnline) {
      // Local preview mode: no backend yet, just echo so you can see the UI flow.
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content:
              "Backend not connected yet — this is local preview mode. Once your FastAPI /api/chats/{id}/query route is up, real screening responses will stream in here.",
          },
        ]);
        setStreamingText(null);
      }, 500);
      return;
    }

    try {
      const finalText = await streamQuery({
        chatId: activeChatId,
        message: text,
        resumeFiles: shouldAttachResumes ? resumeFiles : [],
        onChunk: (_chunk, full) => setStreamingText(full),
      });
      setMessages((prev) => [...prev, { role: "assistant", content: finalText }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ ${err.message}` },
      ]);
    } finally {
      setStreamingText(null);
    }
  }

  function handleRate(messageIndex, question, rating) {
    submitFeedback({ sessionId: activeChatId, messageIndex, question, rating }).catch(() => {});
  }

  const activeChat = chats.find((c) => c.id === activeChatId);

  return (
    <div className="app-shell">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      <div className="main">
        <div className="topbar">
          <div className="topbar-title">{activeChat?.title || "Screening session"}</div>
          <div className="topbar-meta">
            {backendOnline ? "● connected" : "○ local preview — backend offline"}
          </div>
        </div>

        <div className="chat-scroll" ref={scrollRef}>
          {messages.length === 0 && streamingText === null && (
            <div className="empty-state">
              <h3>Start a screening session</h3>
              <p>
                Upload resumes below, then ask something like “screen these against
                the Data Scientist role.”
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <MessageBubble
              key={i}
              role={m.role}
              content={m.content}
              onRate={
                m.role === "assistant"
                  ? (rating) => handleRate(i, messages[i - 1]?.content ?? "", rating)
                  : null
              }
            />
          ))}

          {streamingText !== null && (
            <MessageBubble role="assistant" content={streamingText} isStreaming />
          )}
        </div>

        <div className="composer">
          <FileUploader
            files={resumeFiles}
            onAdd={(files) => setResumeFiles((prev) => [...prev, ...files])}
            onRemove={(i) => setResumeFiles((prev) => prev.filter((_, idx) => idx !== i))}
          />
          <div className="input-row">
            <textarea
              rows={1}
              placeholder="Ask about a job description, or screen an uploaded resume…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button className="send-btn" onClick={handleSend} disabled={!input.trim()}>
              ↑
            </button>
          </div>
          <div className="hint">
            Tip: use “screen”, “evaluate”, “assess”, “review”, or “match” to trigger
            resume screening against uploaded PDFs.
          </div>
        </div>
      </div>
    </div>
  );
}
