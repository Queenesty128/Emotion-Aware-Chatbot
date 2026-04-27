import React, { useEffect, useRef } from "react";

const EMOJI_BY_EMOTION = {
  joy: "😊",
  sadness: "😔",
  anger: "😠",
  fear: "😟",
  neutral: "😐",
};

const INTENSITY_COLORS = {
  low: "#e3f2fd",
  medium: "#bbdefb",
  high: "#90caf9",
};

export default function ChatWindow({ messages, isTyping }) {
  const chatRef = useRef(null);

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  return (
    <div className="chat-window" ref={chatRef}>
      {messages.map((msg, idx) => (
        <div key={idx} className={`bubble-row ${msg.role}`}>
          <div
            className={`bubble ${msg.role}`}
            style={
              msg.emotion
                ? { backgroundColor: INTENSITY_COLORS[msg.intensity] || "#f5f5f5" }
                : {}
            }
          >
            <p>{typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)}</p>
            {msg.emotion && (
              <span className="emotion-pill">
                {EMOJI_BY_EMOTION[msg.emotion] || "🙂"} {msg.emotion} ({msg.intensity})
              </span>
            )}
          </div>
        </div>
      ))}
      {isTyping && (
        <div className="bubble-row assistant">
          <div className="bubble assistant typing">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}
    </div>
  );
}
