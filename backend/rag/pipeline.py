
#pipeline.py — Spaja retriever i Ollama LLM u jedan RAG pipeline.


import httpx
from rag.retriever import get_relevant_chunks
from sqlalchemy.orm import Session
from config import settings


def build_prompt(query: str, chunks: list[dict]) -> str:
    """
    Gradi augmented prompt koji sadrži:
        - System instrukciju
        - Kontekst iz pgvector (retrieved chunkovi)
        - Korisničko pitanje

    LLM dobija samo ono što je u kontekstu —
    ne može da izmišlja informacije koje nisu u dokumentaciji.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i}: {chunk['source']}]\n{chunk['content']}"
        )

    context_block = "\n\n".join(context_parts)

    return f"""You are a helpful customer support assistant for AeroNova Airlines.
Answer the passenger's question based ONLY on the information provided in the context below.
Be clear, friendly, and specific. If the answer involves numbers, fees, or deadlines, 
always state them explicitly.
If the context does not contain enough information to answer the question, say:
"I'm sorry, I don't have information about that. Please contact AeroNova support at +1 800 AERONOVA."

=== CONTEXT ===
{context_block}
=== END CONTEXT ===

Passenger question: {query}

Answer:"""


async def run_pipeline(query: str, db: Session) -> dict:
    """
    Kompletni RAG pipeline za jedan korisnički upit.

    Returna dict sa:
        answer  → LLM odgovor kao string
        sources → lista chunkova korišćenih kao kontekst
    """

    # ── RETRIEVAL ─────────────────────────────────────────────
    chunks = get_relevant_chunks(query=query, db=db)

    if not chunks:
        return {
            "answer":  "I'm sorry, I couldn't find relevant information. "
                       "Please contact AeroNova support at +1 800 AERONOVA.",
            "sources": []
        }

    # ── Similarity threshold check ────────────────────────────
    # Ako ni jedan chunk nije dovoljno sličan → ne šaljemo LLM-u
    best_similarity = chunks[0]["similarity"]
    if best_similarity < 0.25:
        return {
            "answer":  "I'm sorry, I can only answer questions related to "
                       "AeroNova Airlines services, policies, and procedures.",
            "sources": []
        }

    # ── AUGMENTATION ──────────────────────────────────────────
    prompt = build_prompt(query, chunks)

    # ── GENERATION (Ollama) ───────────────────────────────────
    # Šaljemo async HTTP POST na Ollama kontejner
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{settings.OLLAMA_HOST}/api/chat",
            json={
                "model":  settings.OLLAMA_MODEL,
                "stream": False,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "options": {
                    "temperature": 0.1,
                    "num_ctx":     2048, #4096
                }
            }
        )
        response.raise_for_status()
        data = response.json()

    answer = data["message"]["content"]

    print(f"[Pipeline] Odgovor dužine {len(answer)} karaktera.")

    return {
        "answer":  answer,
        "sources": chunks
    }