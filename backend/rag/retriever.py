"""
retriever.py — Prima korisnički query, embeduje ga
i pretražuje pgvector bazu po cosine similarity.

Vraća top-N najrelevantnijih chunkova koji će biti
poslati kao kontekst LLM-u.
"""

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from db.models import DocumentChunk
from config import settings


def get_relevant_chunks(
    query:      str,
    db:         Session,
    n_results:  int = 3
) -> list[dict]:
    """
    RAG Retrieval korak:

    1. Embed korisničkog query-ja (isti model kao za ingest!)
    2. Cosine similarity search u pgvector
    3. Vrati top-N najrelevantnijih chunkova

    pgvector cosine distance operator: <=>
        0.0 = identično
        1.0 = potpuno različito

    Similarity = 1 - distance
    """

    # ── Korak 1: Embed query ──────────────────────────────────
    model       = SentenceTransformer(settings.EMBEDDING_MODEL)
    query_vec   = model.encode(query).tolist()

    # ── Korak 2: Similarity search ────────────────────────────
    #
    # pgvector cosine distance u SQLAlchemy:
    #   DocumentChunk.embedding.cosine_distance(query_vec)
    #
    # .order_by(distance) → najmanji distance prvi = najsličniji
    # .limit(n_results)   → samo top-N
    #
    results = (
        db.query(DocumentChunk, DocumentChunk.embedding.cosine_distance(query_vec).label("distance"))
        .order_by("distance")
        .limit(n_results)
        .all()
    )

    # ── Korak 3: Formatiraj rezultate ─────────────────────────
    chunks = []
    for chunk, distance in results:
        chunks.append({
            "source":      chunk.source,
            "chunk_index": chunk.chunk_index,
            "content":     chunk.content,
            "similarity":  round(1 - distance, 4)
        })

    print(f"[Retriever] Query: '{query}'")
    print(f"[Retriever] Top {n_results} rezultata:")
    for c in chunks:
        print(f"  • {c['source']} (chunk {c['chunk_index']}) "
              f"— similarity: {c['similarity']}")

    return chunks