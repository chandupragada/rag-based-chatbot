import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.embedder import Embedder
from app.vector_store import VectorStore
from app.retriever import Retriever
from app.generator import Generator

load_dotenv()

embedder = Embedder()
vector_store = VectorStore(embedding_dim=3072)
retriever = Retriever(vector_store, embedder, top_k=3)
generator = Generator()

VECTOR_STORE_DIR = "vector_store_data"
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Server] Loading curriculum knowledge base...")
    vector_store.load(VECTOR_STORE_DIR)
    if vector_store.total_chunks == 0:
        print("[Server] No curriculum found!")
        print("[Server] Please run: python ingest.py first")
    else:
        files = list({c.source_file for c in vector_store.chunks})
        print(f"[Server] Loaded {vector_store.total_chunks} chunks from:")
        for f in files:
            print(f"  → {f}")
    yield
    print("[Server] Shutting down.")

app = FastAPI(
    title="Academic RAG Chatbot",
    description="Ask questions about your curriculum!",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str
class Source(BaseModel):
    file: str
    page: int
    score: float
    preview: str
class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if vector_store.total_chunks == 0:
        raise HTTPException(
            503,
            "Curriculum not loaded yet. Please contact your administrator."
        )

    if not request.question.strip():
        raise HTTPException(400, "Please type a question!")
    results = retriever.retrieve(request.question)
    context = retriever.format_context(results)
    try:
        answer = generator.generate(request.question, context)
    except Exception as e:
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            raise HTTPException(429, "Too many requests! Please wait 1 minute and try again.")
        raise HTTPException(500, f"Error generating answer: {str(e)}")

    
    sources = [
        Source(
            file=r["chunk"].source_file,
            page=r["chunk"].page_number,
            score=round(r["score"], 3),
            preview=r["chunk"].text[:150] + "..."
        )
        for r in results
    ]

    return ChatResponse(answer=answer, sources=sources)

@app.get("/status")
async def status():
    files = list({c.source_file for c in vector_store.chunks})
    return {
        "total_chunks": vector_store.total_chunks,
        "curriculum_files": files,
        "ready": vector_store.total_chunks > 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
