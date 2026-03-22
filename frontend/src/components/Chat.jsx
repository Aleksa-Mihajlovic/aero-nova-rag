import { useState, useRef, useEffect } from "react"
import Message from "./Message"
import Sources from "./Sources"

const EXAMPLE_QUESTIONS = [
  "What is the baggage allowance for Basic fare?",
  "Can I change my flight if I have a Standard fare ticket?",
  "How do I report delayed baggage?",
  "What are the benefits of Gold tier in AeroRewards?",
  "Can I travel while pregnant?",
]

export default function Chat() {
  const [messages,  setMessages]  = useState([])
  const [input,     setInput]     = useState("")
  const [loading,   setLoading]   = useState(false)
  const [ingested,  setIngested]  = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  async function handleIngest() {
    setIngesting(true)
    try {
      const res = await fetch("http://0.0.0.0:8000/api/ingest", { method: "POST" })
      const data = await res.json()
      if (data.status === "success") {
        setIngested(true)
        setMessages([{
          role:    "assistant",
          content: `Documentation loaded. I processed ${data.docs_processed} files and created ${data.chunks_created} chunks. You can now ask me anything about AeroNova Airlines.`,
          sources: []
        }])
      }
    } catch (e) {
      alert("Ingest failed: " + e.message)
    } finally {
      setIngesting(false)
    }
  }

  async function handleSend() {
    const question = input.trim()
    if (!question || loading) return

    setMessages(prev => [...prev, { role: "user", content: question }])
    setInput("")
    setLoading(true)

    try {
      const res = await fetch("/api/query", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ question })
      })
      const data = await res.json()
      setMessages(prev => [...prev, {
        role:    "assistant",
        content: data.answer,
        sources: data.sources
      }])
    } catch (e) {
      setMessages(prev => [...prev, {
        role:    "assistant",
        content: "Something went wrong. Please try again.",
        sources: []
      }])
    } finally {
      setLoading(false)
    }
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={styles.wrapper}>

      {/* HEADER */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <span style={styles.logo}>✈ AeroNova</span>
          <span style={styles.headerSub}>AI Support Assistant</span>
        </div>
        <button
          onClick={handleIngest}
          disabled={ingesting}
          style={{
            ...styles.ingestBtn,
            ...(ingested ? styles.ingestBtnDone : {})
          }}
        >
          {ingesting ? "Loading docs..." : ingested ? "✓ Docs Loaded" : "Load Documentation"}
        </button>
      </div>

      {/* MESSAGES */}
      <div style={styles.messages}>
        {messages.length === 0 && (
          <div style={styles.welcome}>
            <div style={styles.welcomeIcon}>✈</div>
            <h2 style={styles.welcomeTitle}>AeroNova Support</h2>
            <p style={styles.welcomeText}>
              Load the documentation first, then ask anything about
              baggage, fares, check-in, loyalty program, and more.
            </p>
            <div style={styles.examples}>
              {EXAMPLE_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  style={styles.exampleChip}
                  onClick={() => setInput(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i}>
            <Message role={msg.role} content={msg.content} />
            {msg.sources?.length > 0 && (
              <Sources sources={msg.sources} />
            )}
          </div>
        ))}

        {loading && (
          <div style={styles.thinking}>
            <span style={styles.dot} />
            <span style={styles.dot} />
            <span style={styles.dot} />
            <span style={styles.thinkingText}>Searching documentation...</span>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* INPUT */}
      <div style={styles.inputArea}>
        <textarea
          style={styles.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKey}
          placeholder={ingested
            ? "Ask anything about AeroNova Airlines..."
            : "Load documentation first..."}
          disabled={!ingested || loading}
          rows={1}
        />
        <button
          style={{
            ...styles.sendBtn,
            opacity: (!ingested || loading || !input.trim()) ? 0.4 : 1
          }}
          onClick={handleSend}
          disabled={!ingested || loading || !input.trim()}
        >
          ➤
        </button>
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display:       "flex",
    flexDirection: "column",
    height:        "100vh",
    background:    "#0a0a0f",
  },
  header: {
    display:        "flex",
    alignItems:     "center",
    justifyContent: "space-between",
    padding:        "16px 24px",
    borderBottom:   "1px solid #1e1e2e",
    background:     "#0d0d14",
    flexShrink:     0,
  },
  headerLeft: {
    display:    "flex",
    alignItems: "baseline",
    gap:        "12px",
  },
  logo: {
    fontSize:   "20px",
    fontWeight: "700",
    color:      "#6366f1",
  },
  headerSub: {
    fontSize: "12px",
    color:    "#4a4a6a",
  },
  ingestBtn: {
    padding:      "8px 18px",
    background:   "transparent",
    border:       "1px solid #6366f1",
    borderRadius: "8px",
    color:        "#6366f1",
    fontSize:     "12px",
    cursor:       "pointer",
    transition:   "all 0.2s",
  },
  ingestBtnDone: {
    borderColor: "#3ecf8e",
    color:       "#3ecf8e",
  },
  messages: {
    flex:      1,
    overflowY: "auto",
    padding:   "24px",
    display:   "flex",
    flexDirection: "column",
    gap:       "16px",
  },
  welcome: {
    display:        "flex",
    flexDirection:  "column",
    alignItems:     "center",
    justifyContent: "center",
    flex:           1,
    textAlign:      "center",
    gap:            "16px",
    padding:        "40px 20px",
  },
  welcomeIcon: {
    fontSize: "48px",
  },
  welcomeTitle: {
    fontSize:   "24px",
    fontWeight: "600",
    color:      "#e2e2f0",
  },
  welcomeText: {
    fontSize:  "14px",
    color:     "#6b6b8a",
    maxWidth:  "400px",
    lineHeight: "1.6",
  },
  examples: {
    display:        "flex",
    flexWrap:       "wrap",
    gap:            "8px",
    justifyContent: "center",
    maxWidth:       "600px",
    marginTop:      "8px",
  },
  exampleChip: {
    padding:      "8px 14px",
    background:   "transparent",
    border:       "1px solid #1e1e2e",
    borderRadius: "20px",
    color:        "#6b6b8a",
    fontSize:     "12px",
    cursor:       "pointer",
    textAlign:    "left",
    transition:   "all 0.15s",
  },
  thinking: {
    display:    "flex",
    alignItems: "center",
    gap:        "6px",
    padding:    "12px 16px",
    background: "#13131a",
    border:     "1px solid #1e1e2e",
    borderRadius: "10px",
    maxWidth:   "220px",
  },
  dot: {
    display:      "inline-block",
    width:        "6px",
    height:       "6px",
    borderRadius: "50%",
    background:   "#6366f1",
    animation:    "bounce 1.2s ease infinite",
  },
  thinkingText: {
    fontSize: "12px",
    color:    "#4a4a6a",
  },
  inputArea: {
    display:    "flex",
    gap:        "12px",
    padding:    "16px 24px",
    borderTop:  "1px solid #1e1e2e",
    background: "#0d0d14",
    flexShrink: 0,
  },
  textarea: {
    flex:        1,
    background:  "#13131a",
    border:      "1px solid #1e1e2e",
    borderRadius: "10px",
    color:       "#e2e2f0",
    fontSize:    "14px",
    padding:     "12px 16px",
    resize:      "none",
    outline:     "none",
    fontFamily:  "inherit",
    lineHeight:  "1.5",
  },
  sendBtn: {
    width:        "44px",
    height:       "44px",
    background:   "#6366f1",
    border:       "none",
    borderRadius: "10px",
    color:        "white",
    fontSize:     "16px",
    cursor:       "pointer",
    flexShrink:   0,
  },
}