"""
main.py — FastAPI aplikacija sa svim endpointima.

Endpoints:
    GET  /api/health   → provera da li backend radi
    POST /api/ingest   → pokreće ingest pipeline
    POST /api/query    → RAG query pipeline
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
from rag.ingest import run_ingest
from rag.pipeline import run_pipeline

app = FastAPI(title="AeroNova RAG API", version="1.0.0")

# CORS — dozvoljava React frontendu da poziva backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ════════════════════════════════════════════════════════════════
# PYDANTIC MODELI
# ════════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    question: str


# ════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.get("/api/health")
def health():
    """
    Proverava da li backend radi.
    Frontend zove ovo na startup.
    """
    return {"status": "ok", "service": "AeroNova RAG API"}


@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    """
    Pokreće kompletan ingest pipeline:
        1. Čita sve .md fajlove iz docs/
        2. Deli na chunkove
        3. Embeduje sa sentence-transformers
        4. Čuva u pgvector

    Poziva se jednom pri prvom pokretanju ili
    kada se dokumentacija promeni.
    """
    try:
        result = run_ingest(db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query(req: QueryRequest, db: Session = Depends(get_db)):
    """
    Kompletni RAG pipeline za jedan korisnički upit:
        1. Embed query
        2. Similarity search u pgvector
        3. Build augmented prompt
        4. Ollama LLM generacija
        5. Vrati odgovor i izvore

    Request:  { "question": "What is the baggage allowance for Basic fare?" }
    Response: { "answer": "...", "sources": [...] }
    """
    if not req.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question ne sme biti prazan."
        )

    try:
        result = await run_pipeline(query=req.question, db=db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))