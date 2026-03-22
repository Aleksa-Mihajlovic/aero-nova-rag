export default function Message({ role, content }) {
  const isUser = role === "user"

  return (
    <div style={{
      ...styles.wrapper,
      justifyContent: isUser ? "flex-end" : "flex-start"
    }}>
      {!isUser && <div style={styles.avatar}>✈</div>}
      <div style={{
        ...styles.bubble,
        ...(isUser ? styles.userBubble : styles.assistantBubble)
      }}>
        <div style={styles.role}>
          {isUser ? "You" : "AeroNova Support"}
        </div>
        <div style={styles.content}>
          {content}
        </div>
      </div>
      {isUser && <div style={styles.avatarUser}>👤</div>}
    </div>
  )
}

const styles = {
  wrapper: {
    display:    "flex",
    alignItems: "flex-start",
    gap:        "10px",
  },
  avatar: {
    width:          "32px",
    height:         "32px",
    borderRadius:   "50%",
    background:     "#1a1a2e",
    border:         "1px solid #2a2a3e",
    display:        "flex",
    alignItems:     "center",
    justifyContent: "center",
    fontSize:       "14px",
    flexShrink:     0,
  },
  avatarUser: {
    width:          "32px",
    height:         "32px",
    borderRadius:   "50%",
    background:     "#1a1a2e",
    border:         "1px solid #2a2a3e",
    display:        "flex",
    alignItems:     "center",
    justifyContent: "center",
    fontSize:       "14px",
    flexShrink:     0,
  },
  bubble: {
    maxWidth:     "680px",
    padding:      "12px 16px",
    borderRadius: "12px",
    display:      "flex",
    flexDirection:"column",
    gap:          "6px",
  },
  userBubble: {
    background: "rgba(99,102,241,0.1)",
    border:     "1px solid rgba(99,102,241,0.25)",
  },
  assistantBubble: {
    background: "#13131a",
    border:     "1px solid #1e1e2e",
  },
  role: {
    fontSize:   "10px",
    fontWeight: "600",
    letterSpacing: "1.5px",
    textTransform: "uppercase",
    color:      "#4a4a6a",
  },
  content: {
    fontSize:   "14px",
    lineHeight: "1.7",
    color:      "#e2e2f0",
    whiteSpace: "pre-wrap",
  },
}