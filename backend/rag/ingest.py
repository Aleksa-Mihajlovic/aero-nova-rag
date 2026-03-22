import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from db.models import DocumentChunk
from db.session import engine, Base
from config import settings

DOCS_PATH  = Path("/app/docs")
CHUNK_SIZE = 150
OVERLAP    = 30


def load_docs() -> list[dict]:
    """
    Čita sve .md fajlove iz docs/ foldera.
    Vraća listu diktova sa filename i content.
    """
    docs = []
    for filepath in DOCS_PATH.glob("*.md"):
        content = filepath.read_text(encoding="utf-8")
        docs.append({
            "source":  filepath.name,
            "content": content
        })
        print(f"[Ingest] Učitan: {filepath.name} ({len(content.split())} reči)")
    return docs


def chunk_text(text: str) -> list[str]:
    """
    Deli tekst na chunkove sa overlapom.

    CHUNK_SIZE=150, OVERLAP=30 znači:
        chunk 0: reč[0:150]
        chunk 1: reč[120:270]   ← 30 reči overlap
        chunk 2: reč[240:390]   ← 30 reči overlap
    """
    words  = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(" ".join(words[start:end]))
        start += CHUNK_SIZE - OVERLAP

    return chunks


def run_ingest(db: Session) -> dict:
    """
    Kompletni ingest pipeline:
        1. Kreiraj tabelu ako ne postoji
        2. Učitaj sve .md fajlove
        3. Podeli na chunkove
        4. Embed svaki chunk
        5. Sačuvaj u pgvector

    Briše postojeće podatke pre svakog ingesta
    kako bi dokumentacija uvek bila ažurna.
    """

    # ── Korak 1: Kreiraj tabelu ───────────────────────────────
    Base.metadata.create_all(bind=engine)
    print("[Ingest] Tabele kreirane / proverene.")

    # ── Korak 2: Obriši stare chunkove ────────────────────────
    deleted = db.query(DocumentChunk).delete()
    db.commit()
    print(f"[Ingest] Obrisano {deleted} starih chunkova.")

    # ── Korak 3: Učitaj fajlove ───────────────────────────────
    docs = load_docs()
    if not docs:
        return {"status": "error", "message": "Nema .md fajlova u docs/"}

    # ── Korak 4: Chunking ─────────────────────────────────────
    all_chunks = []   # lista (source, chunk_index, tekst)

    for doc in docs:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "source":      doc["source"],
                "chunk_index": i,
                "content":     chunk
            })

    print(f"[Ingest] Ukupno chunkova: {len(all_chunks)}")

    # ── Korak 5: Embedding ────────────────────────────────────
    print(f"[Ingest] Učitavam embedding model: {settings.EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    texts      = [c["content"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # ── Korak 6: Čuvanje u pgvector ───────────────────────────
    print("[Ingest] Čuvam u pgvector...")

    for chunk, embedding in zip(all_chunks, embeddings):
        db.add(DocumentChunk(
            source      = chunk["source"],
            chunk_index = chunk["chunk_index"],
            content     = chunk["content"],
            embedding   = embedding.tolist()
        ))

    db.commit()
    print(f"[Ingest] ✓ Sačuvano {len(all_chunks)} chunkova u bazi.")

    return {
        "status":         "success",
        "docs_processed": len(docs),
        "chunks_created": len(all_chunks),
    }