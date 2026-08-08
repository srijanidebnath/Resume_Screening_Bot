import RatingStars from "./RatingStars.jsx";

export default function MessageBubble({ role, content, onRate, isStreaming }) {
  const isUser = role === "user";
  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="avatar">{isUser ? "🧑" : "📄"}</div>
      <div>
        <div className="bubble">
          {content}
          {isStreaming && (
            <span className="typing-dots" style={{ marginLeft: 6 }}>
              <span></span><span></span><span></span>
            </span>
          )}
        </div>
        {!isUser && !isStreaming && content && onRate && (
          <RatingStars onRate={onRate} />
        )}
      </div>
    </div>
  );
}
