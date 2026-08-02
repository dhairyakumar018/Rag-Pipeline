import { useState, useRef, useEffect } from "react";

const API_URL = "http://localhost:8000";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendQuestion() {
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Error reaching the server.", sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.header}>RAG Chat</h2>

      <div style={styles.messages}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.bubble,
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#5B5BFF" : "#f0f0f0",
              color: m.role === "user" ? "white" : "black",
            }}
          >
            <div>{m.text}</div>
            {m.sources && m.sources.length > 0 && (
              <div style={styles.sources}>
                Sources: {m.sources.join(", ")}
              </div>
            )}
          </div>
        ))}
        {loading && <div style={styles.loading}>Thinking...</div>}
        <div ref={bottomRef} />
      </div>

      <div style={styles.inputRow}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about your documents..."
          style={styles.textarea}
          rows={2}
        />
        <button onClick={sendQuestion} disabled={loading} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: 700,
    margin: "0 auto",
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    fontFamily: "system-ui, sans-serif",
    padding: 16,
    boxSizing: "border-box",
  },
  header: { marginBottom: 8, textAlign: "left" },
  messages: {
    flex: 1,
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    gap: 10,
    padding: 8,
  },
  bubble: {
    maxWidth: "75%",
    padding: "10px 14px",
    borderRadius: 12,
    textAlign: "left",
  },
  sources: { fontSize: 11, opacity: 0.6, marginTop: 6 },
  loading: { fontSize: 13, opacity: 0.6, fontStyle: "italic", textAlign: "left" },
  inputRow: { display: "flex", gap: 8, marginTop: 8 },
  textarea: {
    flex: 1,
    padding: 10,
    borderRadius: 8,
    border: "1px solid #ccc",
    resize: "none",
    fontFamily: "inherit",
  },
  button: {
    padding: "0 20px",
    borderRadius: 8,
    border: "none",
    background: "#5B5BFF",
    color: "white",
    fontWeight: 600,
    cursor: "pointer",
  },
};
