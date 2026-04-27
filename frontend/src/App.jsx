import React, { useMemo, useState, useEffect } from "react";
import ChatWindow from "./components/ChatWindow";
import TrendChart from "./components/TrendChart";
import AuthForm from "./components/AuthForm";
import { fetchTrends, sendChat, getProfile, checkHealth } from "./api";

export default function App() {
  const [user, setUser] = useState(null);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [messages, setMessages] = useState([]);
  const [trendData, setTrendData] = useState({ latest_emotions: [] });
  const [error, setError] = useState("");
  const [darkMode, setDarkMode] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      getProfile().then(setUser).catch(() => localStorage.removeItem("authToken"));
    }
  }, []);

  const hasTrend = useMemo(
    () => (trendData.latest_emotions || []).length > 1,
    [trendData]
  );

  async function handleSend(text) {
    const trimmed = text.trim();
    if (!trimmed) return;
    setError("");

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setInput("");
    setIsTyping(true);

    try {
      const reply = await sendChat({ message: trimmed });

      // Temporary console.log to inspect backend response
      console.log("Backend reply:", reply);

      // Safe response handling: ensure content is always a string
      let responseText = "";
      if (typeof reply.response === "string") {
        responseText = reply.response;
      } else if (reply.response && typeof reply.response === "object") {
        responseText = reply.response.text || JSON.stringify(reply.response);
      } else {
        responseText = JSON.stringify(reply);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: responseText,
          emotion: reply.emotion,
          intensity: reply.emotion_intensity,
        },
      ]);

      const trends = await fetchTrends();
      setTrendData(trends);
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setIsTyping(false);
    }
  }

  if (!user) {
    return <AuthForm onLogin={setUser} />;
  }

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>
      <div className="background-gradient"></div>
      <header className="header">
        <h1>Emotion-Aware Support Chatbot</h1>
        <div className="header-controls">
          <button onClick={() => setDarkMode(!darkMode)} className="mode-toggle">
            {darkMode ? "☀️" : "🌙"}
          </button>
          <button onClick={() => setShowSidebar(!showSidebar)} className="sidebar-toggle">
            📊
          </button>
        </div>
      </header>

      <div className="main-content">
        <div className="chat-container">
          <div className="chat-header">
            <h2>Hi {user.name || user.username}, how are you feeling?</h2>
            <button
              className="checkin-btn"
              onClick={() => handleSend("How are you feeling today?")}
            >
              Daily Check-In
            </button>
          </div>

          <ChatWindow messages={messages} isTyping={isTyping} />

          {error && <p className="error">{error}</p>}

          <form
            className="composer"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your thoughts here..."
            />
            <button type="submit">Send</button>
          </form>
        </div>

        {showSidebar && hasTrend && (
          <div className="sidebar">
            <TrendChart latestEmotions={trendData.latest_emotions} />
          </div>
        )}
      </div>
    </div>
  );
}
