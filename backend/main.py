from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from rag_graph import run_rag, ALL_DEPARTMENTS

load_dotenv()

app = FastAPI(title="University Admission Chatbot API", version="1.0.0")

# ── CORS — required for React frontend ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your Vercel URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    department: Optional[str] = None   # null = search all departments

class SourceInfo(BaseModel):
    department: str
    category: str
    distance: float

class ChatResponse(BaseModel):
    response: str
    sources: List[SourceInfo]

# ── Routes ─────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sources")
def get_sources():
    """
    Return individual department names for the frontend dropdown.
    These come from DEPT_TO_SOURCE in rag_graph.py — the single source
    of truth — so the filter values always match what ChromaDB has.
    """
    return {"sources": ALL_DEPARTMENTS}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = run_rag(
        question=req.message.strip(),
        department=req.department if req.department not in (None, "All") else None,
    )

    sources = [
        SourceInfo(
            department=s.get("source", ""),
            category=s.get("category", ""),
            distance=s.get("distance", 0.0),
        )
        for s in result["sources"]
    ]

    return ChatResponse(response=result["answer"], sources=sources)