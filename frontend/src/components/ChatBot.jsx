import { useState, useRef, useEffect, useCallback } from "react";
import "./ChatBot.css";

// ─── Constants ───────────────────────────────────────────────────────────────
const API_BASE_URL = "http://localhost:8000"; // 🔁 Change to your deployed backend URL

const DEPARTMENTS = [
  { value: "all",                    label: "All Departments" },
  { value: "CSE AI & ML",            label: "CSE — AI & ML" },
  { value: "CSE Data Science",       label: "CSE — Data Science" },
  { value: "CSE CSBS",               label: "CSE — CSBS" },
  { value: "CSE General",            label: "CSE — General" },
  { value: "IoT",                    label: "IoT" },
  { value: "ECE",                    label: "ECE" },
  { value: "EEE",                    label: "EEE" },
  { value: "IT",                     label: "IT" },
  { value: "Chemical Engineering",   label: "Chemical Engg." },
  { value: "Textile",                label: "Textile" },
  { value: "Food Technology",        label: "Food Technology" },
  { value: "Agriculture",            label: "B.Sc Agriculture" },
  { value: "Civil Engineering",      label: "Civil Engg." },
  { value: "Mechanical Engineering", label: "Mechanical Engg." },
  { value: "Biotechnology",          label: "Biotechnology" },
  { value: "Biomedical",             label: "Biomedical" },
];

const SUGGESTED_BY_DEPT = {
  all:                      ["NIRF Ranking", "Admission via EAMCET", "Application deadline", "Accreditations (NAAC/NBA)", "Other states apply?"],
  "CSE AI & ML":            ["Languages taught?", "AI labs available?", "Real-time projects?", "Industries hiring?"],
  "CSE Data Science":       ["Data Science curriculum", "Tools taught", "Career opportunities", "Internship availability"],
  "CSE CSBS":               ["What is CSBS?", "Business subjects?", "CSBS career options", "Industry-oriented?"],
  "CSE General":            ["Programming languages", "Coding labs?", "Cloud computing?", "Placement record"],
  "IoT":                    ["IoT curriculum", "Embedded systems?", "IoT project work", "Career after IoT"],
  "ECE":                    ["ECE career options", "Embedded systems?", "5G training?", "ECE lab facilities"],
  "EEE":                    ["EEE career options", "Power systems?", "EEE lab facilities", "Companies hiring?"],
  "IT":                     ["IT curriculum", "Software tools?", "IT internships", "IT placement record"],
  "Chemical Engineering":   ["Industries hiring?", "Chemical labs?", "Software tools?", "Safety training"],
  "Textile":                ["Textile industry career", "Lab facilities?", "Internship?", "Curriculum overview"],
  "Food Technology":        ["Food Tech careers", "Food labs?", "Food safety training", "FMCG companies?"],
  "Agriculture":            ["B.Sc Agri career", "Agri labs?", "Government jobs?", "Internship?"],
  "Civil Engineering":      ["Civil career options", "AutoCAD training?", "Construction internship?", "Smart city courses?"],
  "Mechanical Engineering": ["Mechanical careers", "CAD/CAM training?", "Core companies?", "Lab facilities?"],
  "Biotechnology":          ["Biotech careers", "Genetic engineering?", "Biotech labs?", "Pharma hiring?"],
  "Biomedical":             ["Biomedical careers", "Medical device training?", "Lab facilities?", "Healthcare hiring?"],
};

// ─── Utility ─────────────────────────────────────────────────────────────────
function formatTime(date) {
  return new Date(date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function generateId() {
  return Math.random().toString(36).slice(2, 9);
}

function getWelcomeMessage(department) {
  if (!department || department === "all") {
    return "👋 Hello! I'm <strong>Vignan's Admission Assistant</strong>. I can help with admissions, courses, eligibility, deadlines and more.<br/>What would you like to know?";
  }
  const dept = DEPARTMENTS.find((d) => d.value === department);
  return `👋 Hello! You've selected <strong>${dept?.label}</strong>. Ask me anything about this department — courses, careers, labs, internships and more!`;
}

// ─── API Call ─────────────────────────────────────────────────────────────────
async function fetchBotResponse(userMessage, department) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: userMessage,
      department: department === "all" ? null : department,
    }),
  });
  if (!response.ok) throw new Error(`Server error: ${response.status}`);
  const data = await response.json();
  return data.response;
}

// ─── Sub-components ───────────────────────────────────────────────────────────
function BotAvatar() {
  return (
    <div className="msg-avatar bot-msg-avatar" aria-hidden="true">
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24">
        <rect x="3" y="6" width="18" height="13" rx="3" fill="white" />
        <circle cx="9" cy="12" r="1.5" fill="#1a56c4" />
        <circle cx="15" cy="12" r="1.5" fill="#1a56c4" />
        <path d="M9 16h6" stroke="#1a56c4" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    </div>
  );
}

function UserAvatar() {
  return <div className="msg-avatar user-msg-avatar" aria-hidden="true">U</div>;
}

function TypingIndicator() {
  return (
    <div className="msg-row" aria-live="polite" aria-label="Bot is typing">
      <BotAvatar />
      <div className="typing-indicator">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`msg-row ${isUser ? "user" : ""}`}>
      {!isUser && <BotAvatar />}
      <div>
        <div
          className={`bubble ${isUser ? "user-bubble" : "bot-bubble"}`}
          dangerouslySetInnerHTML={{ __html: msg.text }}
        />
        <div className={`msg-time ${isUser ? "" : "bot-time"}`}>
          {formatTime(msg.timestamp)}
          {isUser && msg.department && msg.department !== "all" && (
            <span className="msg-dept-tag">{msg.department}</span>
          )}
        </div>
      </div>
      {isUser && <UserAvatar />}
    </div>
  );
}

function ErrorMessage({ onRetry }) {
  return (
    <div className="msg-row">
      <BotAvatar />
      <div>
        <div className="bubble bot-bubble error-bubble">
          ⚠️ Sorry, I couldn't connect to the server. Please try again.
          <button className="retry-btn" onClick={onRetry}>Retry</button>
        </div>
      </div>
    </div>
  );
}

function DepartmentDropdown({ value, onChange }) {
  return (
    <div className="dept-dropdown-wrap">
      <svg className="dept-icon" width="11" height="11" fill="none" viewBox="0 0 24 24">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke="rgba(255,255,255,0.85)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        <polyline points="9 22 9 12 15 12 15 22" stroke="rgba(255,255,255,0.85)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
      <select
        className="dept-dropdown"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label="Select department"
      >
        {DEPARTMENTS.map((d) => (
          <option key={d.value} value={d.value}>{d.label}</option>
        ))}
      </select>
      <svg className="dept-chevron" width="10" height="10" fill="none" viewBox="0 0 24 24">
        <path d="M6 9l6 6 6-6" stroke="rgba(255,255,255,0.85)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </div>
  );
}

function HistoryItem({ item, onClick }) {
  return (
    <button className="history-item" onClick={onClick} aria-label={`Resume chat: ${item.userMsg}`}>
      {item.department && item.department !== "all" && (
        <div className="history-dept-badge">{item.department}</div>
      )}
      <div className="history-title">{item.userMsg}</div>
      <div className="history-preview">{item.botMsg}</div>
      <div className="history-date">{item.date} · {item.time}</div>
    </button>
  );
}

// ─── Main ChatBot Component ───────────────────────────────────────────────────
export default function ChatBot() {
  const [isOpen, setIsOpen]           = useState(false);
  const [activeTab, setActiveTab]     = useState("chat");
  const [department, setDepartment]   = useState("all");
  const [messages, setMessages]       = useState([]);
  const [inputValue, setInputValue]   = useState("");
  const [isTyping, setIsTyping]       = useState(false);
  const [hasError, setHasError]       = useState(false);
  const [history, setHistory]         = useState([]);
  const [lastUserMsg, setLastUserMsg] = useState("");

  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);
  const textareaRef    = useRef(null);

  // Set welcome message on mount
  useEffect(() => {
    setMessages([{
      id: "welcome",
      role: "bot",
      text: getWelcomeMessage("all"),
      timestamp: new Date(),
    }]);
  }, []);

  // When department changes, inject a context-switch system message
  const handleDepartmentChange = useCallback((newDept) => {
    setDepartment(newDept);
    const dept = DEPARTMENTS.find((d) => d.value === newDept);
    setMessages((prev) => [
      ...prev,
      {
        id: generateId(),
        role: "bot",
        text: newDept === "all"
          ? "Switched to <strong>All Departments</strong>. Ask me anything about Vignan's admissions!"
          : `Now focused on <strong>${dept?.label}</strong>. Ask me anything specific to this department!`,
        timestamp: new Date(),
      },
    ]);
    setHasError(false);
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Auto-focus input when chat opens
  useEffect(() => {
    if (isOpen && activeTab === "chat") {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen, activeTab]);

  const addToHistory = useCallback((userMsg, botMsg, dept) => {
    setHistory((prev) => [
      {
        id: generateId(),
        userMsg,
        botMsg: botMsg.replace(/<[^>]+>/g, "").substring(0, 60) + "...",
        department: dept,
        date: new Date().toLocaleDateString(),
        time: formatTime(new Date()),
      },
      ...prev,
    ]);
  }, []);

  const sendMessage = useCallback(
    async (text) => {
      const trimmed = (text || inputValue).trim();
      if (!trimmed || isTyping) return;

      setInputValue("");
      setHasError(false);
      setLastUserMsg(trimmed);
      if (textareaRef.current) textareaRef.current.style.height = "auto";

      const userMsg = {
        id: generateId(),
        role: "user",
        text: trimmed,
        department,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsTyping(true);

      try {
        const responseText = await fetchBotResponse(trimmed, department);
        const botMsg = {
          id: generateId(),
          role: "bot",
          text: responseText,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, botMsg]);
        addToHistory(trimmed, responseText, department);
      } catch (err) {
        console.error("Chat error:", err);
        setHasError(true);
      } finally {
        setIsTyping(false);
      }
    },
    [inputValue, isTyping, department, addToHistory]
  );

  const handleRetry = useCallback(() => {
    setHasError(false);
    sendMessage(lastUserMsg);
  }, [lastUserMsg, sendMessage]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTextareaChange = (e) => {
    setInputValue(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 90) + "px";
  };

  const clearChat = () => {
    setMessages([{
      id: "welcome",
      role: "bot",
      text: getWelcomeMessage(department),
      timestamp: new Date(),
    }]);
    setHasError(false);
  };

  const currentSuggestions  = SUGGESTED_BY_DEPT[department] || SUGGESTED_BY_DEPT["all"];
  const selectedDeptLabel   = DEPARTMENTS.find((d) => d.value === department)?.label;

  return (
    <>
      {/* ── Chat Window ── */}
      {isOpen && (
        <div className="chat-window" role="dialog" aria-label="Admission Assistant Chat">

          {/* Header */}
          <div className="chat-header">
            <div className="bot-avatar-header">
              <svg width="22" height="22" fill="none" viewBox="0 0 24 24">
                <rect x="3" y="6" width="18" height="13" rx="3" fill="rgba(255,255,255,0.9)" />
                <circle cx="9" cy="12" r="1.5" fill="#1a56c4" />
                <circle cx="15" cy="12" r="1.5" fill="#1a56c4" />
                <path d="M9 16h6" stroke="#1a56c4" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M8 6V4M16 6V4" stroke="rgba(255,255,255,0.7)" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </div>
            <div className="header-info">
              <div className="bot-name">Vignan Admission Assistant</div>
              <div className="bot-status">
                <span className="status-dot" />
                Online · Replies instantly
              </div>
            </div>
            <div className="header-actions">
              <button className="header-btn" onClick={clearChat} title="Clear chat" aria-label="Clear chat">
                <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                  <path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <button className="header-btn" onClick={() => setIsOpen(false)} title="Close" aria-label="Close chat">
                <svg width="13" height="13" fill="none" viewBox="0 0 24 24">
                  <path d="M18 6L6 18M6 6l12 12" stroke="white" strokeWidth="2" strokeLinecap="round" />
                </svg>
              </button>
            </div>
          </div>

          {/* ── Department Filter Bar ── */}
          <div className="dept-bar">
            <span className="dept-bar-label">Dept:</span>
            <DepartmentDropdown value={department} onChange={handleDepartmentChange} />
            {department !== "all" && (
              <button
                className="dept-clear-btn"
                onClick={() => handleDepartmentChange("all")}
                title="Clear filter"
                aria-label="Clear department filter"
              >
                ✕
              </button>
            )}
          </div>

          {/* Tabs */}
          <div className="chat-tabs" role="tablist">
            <button
              role="tab"
              aria-selected={activeTab === "chat"}
              className={`tab-btn ${activeTab === "chat" ? "active" : ""}`}
              onClick={() => setActiveTab("chat")}
            >
              Chat
            </button>
            <button
              role="tab"
              aria-selected={activeTab === "history"}
              className={`tab-btn ${activeTab === "history" ? "active" : ""}`}
              onClick={() => setActiveTab("history")}
            >
              History {history.length > 0 && <span className="history-badge">{history.length}</span>}
            </button>
          </div>

          {/* ── Chat Tab ── */}
          {activeTab === "chat" && (
            <div className="tab-content">
              <div className="messages-area" role="log" aria-live="polite">
                {messages.map((msg) => (
                  <Message key={msg.id} msg={msg} />
                ))}
                {isTyping && <TypingIndicator />}
                {hasError && <ErrorMessage onRetry={handleRetry} />}
                <div ref={messagesEndRef} />
              </div>

              {/* Suggested questions — change dynamically with department */}
              <div className="suggestions-area">
                <div className="suggestions-label">
                  {department !== "all" ? `Suggested for ${selectedDeptLabel}` : "Suggested Questions"}
                </div>
                <div className="suggestions-scroll">
                  {currentSuggestions.map((q) => (
                    <button
                      key={q}
                      className="suggestion-chip"
                      onClick={() => sendMessage(q)}
                      disabled={isTyping}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input */}
              <div className="input-area">
                <textarea
                  ref={(el) => { inputRef.current = el; textareaRef.current = el; }}
                  className="msg-input"
                  value={inputValue}
                  onChange={handleTextareaChange}
                  onKeyDown={handleKeyDown}
                  placeholder={
                    department === "all"
                      ? "Ask about admissions, courses..."
                      : `Ask about ${selectedDeptLabel}...`
                  }
                  rows={1}
                  aria-label="Type your message"
                  disabled={isTyping}
                />
                <button
                  className="send-btn"
                  onClick={() => sendMessage()}
                  disabled={!inputValue.trim() || isTyping}
                  aria-label="Send message"
                >
                  <svg width="16" height="16" fill="none" viewBox="0 0 24 24">
                    <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* ── History Tab ── */}
          {activeTab === "history" && (
            <div className="tab-content history-tab-content">
              {history.length === 0 ? (
                <div className="history-empty">
                  <svg width="40" height="40" fill="none" viewBox="0 0 24 24" style={{ opacity: 0.25, marginBottom: 12 }}>
                    <path d="M12 8v4l3 3M21 12a9 9 0 11-18 0 9 9 0 0118 0z" stroke="#1a56c4" strokeWidth="1.5" strokeLinecap="round" />
                  </svg>
                  No chat history yet.<br />Start a conversation!
                </div>
              ) : (
                history.map((item) => (
                  <HistoryItem
                    key={item.id}
                    item={item}
                    onClick={() => setActiveTab("chat")}
                  />
                ))
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Toggle Button ── */}
      <button
        className={`chat-toggle ${isOpen ? "open" : ""}`}
        onClick={() => setIsOpen((v) => !v)}
        aria-label={isOpen ? "Close chat" : "Open admission assistant"}
        aria-expanded={isOpen}
      >
        {!isOpen && <span className="notif-dot" aria-hidden="true" />}
        {isOpen ? (
          <svg width="22" height="22" fill="none" viewBox="0 0 24 24">
            <path d="M18 6L6 18M6 6l12 12" stroke="white" strokeWidth="2.5" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="26" height="26" fill="none" viewBox="0 0 24 24">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z" fill="white" />
          </svg>
        )}
      </button>
    </>
  );
}
