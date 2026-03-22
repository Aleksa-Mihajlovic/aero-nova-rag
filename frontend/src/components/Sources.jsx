export default function Sources({ sources }) {
  if (!sources || sources.length === 0) return null

  return (
    <div style={styles.wrapper}>
      <div style={styles.label}>Context sources from documentation</div>
      <div style={styles.cards}>
        {sources.map((source, i) => (
          <div key={i} style={styles.card}>
            <div style={styles.cardTitle}>
              {source.source.replace(".md", "").replace(/_/g, " ")}
            </div>
            <div style={styles.cardMeta}>
              chunk {source.chunk_index + 1}
            </div>
            <div style={styles.cardSim}>
              {(source.similarity * 100).toFixed(1)}% match
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

const styles = {
  wrapper: {
    display:       "flex",
    flexDirection: "column",
    gap:           "8px",
    marginLeft:    "42px",
    marginTop:     "4px",
  },
  label: {
    fontSize:      "10px",
    color:         "#4a4a6a",
    letterSpacing: "1px",
    textTransform: "uppercase",
  },
  cards: {
    display:  "flex",
    flexWrap: "wrap",
    gap:      "8px",
  },
  card: {
    background:   "#0d0d14",
    border:       "1px solid #1e1e2e",
    borderRadius: "8px",
    padding:      "8px 12px",
    display:      "flex",
    flexDirection:"column",
    gap:          "3px",
    minWidth:     "140px",
  },
  cardTitle: {
    fontSize:   "12px",
    fontWeight: "500",
    color:      "#e2e2f0",
    textTransform: "capitalize",
  },
  cardMeta: {
    fontSize: "11px",
    color:    "#4a4a6a",
  },
  cardSim: {
    fontSize: "11px",
    color:    "#6366f1",
    fontWeight: "500",
  },
}