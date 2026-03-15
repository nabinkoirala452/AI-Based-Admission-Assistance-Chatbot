from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import chromadb, os
from dotenv import load_dotenv
from rag_graph import run_rag
 
load_dotenv()
 
app = FastAPI(title="University Admission Chatbot API", version="1.0.0")
 
# ── CORS — required for React frontend ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your Vercel URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)
 
# ── Request / Response models (matching BACKEND_CONTRACT.md) ──────────────────
class ChatRequest(BaseModel):
    message: str                  # frontend sends "message" (not "question")
    department: Optional[str] = None   # null = search all departments
 
class SourceInfo(BaseModel):
    department: str               # frontend sees "department" (mapped from "source")
    category: str
    distance: float
 
class ChatResponse(BaseModel):
    response: str                 # frontend expects "response" (not "answer")
    sources: List[SourceInfo]
 
# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}
 
 
@app.get("/sources")
def get_sources():
    """Return all unique department names for the filter dropdown."""
    chroma_path = os.getenv("CHROMA_PATH", "../Data PreProcessing/chroma_db")
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection("university_qa")
 
    all_meta = collection.get(include=["metadatas"])["metadatas"]
    # The ChromaDB metadata key is "source" — we expose it as department names
    departments = sorted(set(m["source"] for m in all_meta if m.get("source")))
    return {"sources": departments}
 
 
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
 
    # run_rag uses "source" internally (matches ChromaDB metadata key)
    result = run_rag(
        question=req.message.strip(),
        department=req.department if req.department not in (None, "All") else None,
    )
 
    # Rename "source" → "department" and "answer" → "response" for the contract
    sources = [
        SourceInfo(
            department=s.get("source", ""),
            category=s.get("category", ""),
            distance=s.get("distance", 0.0),
        )
        for s in result["sources"]
    ]
 
    return ChatResponse(response=result["answer"], sources=sources)