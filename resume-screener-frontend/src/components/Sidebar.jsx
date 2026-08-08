export default function Sidebar({ chats, activeChatId, onSelectChat, onNewChat, onDeleteChat }) {
  return (
    <aside className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        + New screening session
      </button>

      <div className="session-list-label">Sessions</div>
      <div className="session-list">
        {chats.length === 0 && (
          <div style={{ color: "#8B90A6", fontSize: "0.8rem", padding: "8px 10px" }}>
            No sessions yet.
          </div>
        )}
        {chats.map((chat) => (
          <button
            key={chat.id}
            className={`session-item ${chat.id === activeChatId ? "active" : ""}`}
            onClick={() => onSelectChat(chat.id)}
          >
            <span>{chat.title}</span>
            <span
              className="session-delete"
              role="button"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteChat(chat.id);
              }}
            >
              ✕
            </span>
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        Screens resumes against job descriptions using RAG. Ask it to “screen”,
        “evaluate”, or “match” an uploaded resume against a role.
      </div>
    </aside>
  );
}
