# AeroNova RAG — AI Customer Support Chatbot

AI-powered customer support assistant for AeroNova Airlines built with
Retrieval-Augmented Generation (RAG).

## Tech Stack
- **Backend** — Python, FastAPI
- **Vector Database** — PostgreSQL + pgvector
- **Embeddings** — sentence-transformers (all-MiniLM-L6-v2)
- **LLM** — Ollama (llama3.2)
- **Frontend** — React + Vite
- **Infrastructure** — Docker, Docker Compose

## How it works
1. Airline documentation is chunked and embedded into pgvector
2. User question is embedded using the same model
3. pgvector finds the most similar chunks (cosine similarity)
4. Retrieved chunks + question are sent to Ollama as context
5. LLM generates an answer based only on the documentation

## Getting Started

### Prerequisites
- Docker and Docker Desktop installed

### Run
cp .env.example .env
docker-compose up --build

### Load documentation
After all containers start, open http://localhost:3000
and click "Load Documentation".

### Pull LLM model (first time only)
docker exec -it aero-nova-rag-ollama-1 ollama pull llama3.2:1b