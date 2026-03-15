import os
from dotenv import load_dotenv
from typing import TypedDict, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

# ── Constants ──────────────────────────────────────────────────────────────────
CHROMA_PATH = os.getenv("CHROMA_PATH", "../Data PreProcessing/chroma_db")
COLLECTION_NAME = "university_qa"
EMBED_MODEL = "all-MiniLM-L6-v2"
RELEVANCE_THRESHOLD = 0.70   # ChromaDB cosine distance — below this = relevant
TOP_K = 4

# ── Source mapping ─────────────────────────────────────────────────────────────
# The JSON/ChromaDB stores combined pipe-separated source values.
# This maps individual department names (what the frontend sends)
# to the exact source string stored in ChromaDB.
DEPT_TO_SOURCE = {
    # ── CSE group ──────────────────────────────────────────────────────────────
    "CSE AI & ML":              "CSE AI & ML | CSE Data Science",
    "CSE Data Science":         "CSE AI & ML | CSE Data Science",
    "CSE CSBS":                 "CSE CSBS | IoT",
    "IoT":                      "CSE CSBS | IoT",
    # ── Engineering group ─────────────────────────────────────────────────────
    "Chemical Engineering":     "Chemical |Textile",
    "Textile":                  "Chemical |Textile",
    # ── Science/Agriculture group ─────────────────────────────────────────────
    "Food Technology":          "Food Tech | B.Sc Agriculture",
    "Agriculture":              "Food Tech | B.Sc Agriculture",
}
# NOTE: "QA Session for AI" is intentionally excluded here.
# Those are general university Q&As — covered by "All Departments" (no filter).

# Individual department names exposed to the UI dropdown
ALL_DEPARTMENTS = sorted(DEPT_TO_SOURCE.keys())


# ── Singletons (loaded once at startup) ────────────────────────────────────────
_embedder = SentenceTransformer(EMBED_MODEL)
_chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _chroma_client.get_collection(COLLECTION_NAME)

_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,           # deterministic — no creative wandering
    max_tokens=512,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ── Greeting detection ────────────────────────────────────────────────────────
# Checked before ChromaDB is ever queried — short-circuits the whole RAG pipeline.
GREETINGS = {
    "hi", "hello", "hey", "hii", "hiii", "heya", "hiya",
    "how are you", "how are you?", "how r u", "how r you", "how are u",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "thank you!", "thanks!",
    "bye", "goodbye", "see you", "see ya",
    "ok", "okay", "alright", "sure", "great",
}

GREETING_RESPONSE = (
    "👋 Hi there! Welcome to Vignan's Admission Assistant.\n\n"
    "I can help you with:\n"
    "• Admissions & eligibility\n"
    "• Fee structure & scholarships\n"
    "• Rankings & accreditations\n"
    "• Department-specific courses & placements\n\n"
    "What would you like to know?"
)

def _is_greeting(text: str) -> bool:
    cleaned = text.strip().lower().rstrip("!.,?")
    return cleaned in GREETINGS


# ── Graph state ────────────────────────────────────────────────────────────────
class RAGState(TypedDict):
    question: str
    department: Optional[str]
    retrieved_docs: List[dict]
    relevant_docs: List[dict]
    answer: str
    source_info: List[dict]
    is_greeting: bool          # True → skip retrieve/grade/generate entirely


# ── Node 0: Greeting check ────────────────────────────────────────────────────
def greeting_node(state: RAGState) -> RAGState:
    if _is_greeting(state["question"]):
        return {**state, "is_greeting": True,
                "answer": GREETING_RESPONSE, "source_info": []}
    return {**state, "is_greeting": False}


# ── Node 1: Retrieve from ChromaDB ────────────────────────────────────────────
def retrieve_node(state: RAGState) -> RAGState:
    question   = state["question"]
    department = state.get("department")

    query_vector = _embedder.encode(question).tolist()

    # Map UI department name → exact ChromaDB source string
    where_clause = None
    if department:
        chroma_source = DEPT_TO_SOURCE.get(department)
        if chroma_source:
            where_clause = {"source": chroma_source}
        # Unknown department string → search all (safe fallback)

    results = _collection.query(
        query_embeddings=[query_vector],
        n_results=TOP_K,
        where=where_clause,
        include=["documents", "metadatas", "distances"],
    )

    docs = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        docs.append({
            "document": doc,
            "metadata": meta,
            "distance": dist,
        })

    return {**state, "retrieved_docs": docs}


# ── Node 2: Grade relevance ────────────────────────────────────────────────────
def grade_node(state: RAGState) -> RAGState:
    relevant = [
        d for d in state["retrieved_docs"]
        if d["distance"] < RELEVANCE_THRESHOLD
    ]
    return {**state, "relevant_docs": relevant}


# ── Node 3: Generate answer ────────────────────────────────────────────────────
# Strict prompt + temperature=0 is the hallucination guard.
# Guard node removed — it caused false negatives with Llama 3.1 8B because
# the model rarely returns a bare single word as instructed.

ANSWER_PROMPT = ChatPromptTemplate.from_template("""
You are a university admission assistant. Your ONLY job is to answer questions
using the provided context.

STRICT RULES:
- Answer ONLY from the context below. Do not use any outside knowledge.
- If the context contains the answer, give it directly and concisely.
- If the context does NOT contain enough information, respond EXACTLY with:
  "I'm sorry, I don't have information about that. Please contact the admissions office directly."
- Do NOT guess, infer, or add any information not present in the context.
- Do NOT say "based on my knowledge" or any similar phrase.

Context:
{context}

Question: {question}

Answer:""")

answer_chain = ANSWER_PROMPT | _llm | StrOutputParser()

def generate_node(state: RAGState) -> RAGState:
    relevant_docs = state["relevant_docs"]

    if not relevant_docs:
        return {
            **state,
            "answer": "I'm sorry, I don't have information about that. Please contact the admissions office directly.",
            "source_info": [],
        }

    context_parts = []
    source_info   = []
    for doc in relevant_docs:
        context_parts.append(doc["document"])
        source_info.append({
            "category": doc["metadata"].get("category", ""),
            "source":   doc["metadata"].get("source", ""),
            "distance": round(doc["distance"], 4),
        })

    context = "\n\n---\n\n".join(context_parts)
    answer  = answer_chain.invoke({"context": context, "question": state["question"]})

    return {**state, "answer": answer, "source_info": source_info}


# ── Build the graph ────────────────────────────────────────────────────────────
def build_rag_graph():
    graph = StateGraph(RAGState)

    graph.add_node("greeting", greeting_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade",    grade_node)
    graph.add_node("generate", generate_node)

    graph.set_entry_point("greeting")

    # Greetings short-circuit to END — answer already set in greeting_node.
    # Everything else goes through the full RAG pipeline.
    graph.add_conditional_edges(
        "greeting",
        lambda s: END if s["is_greeting"] else "retrieve",
    )
    graph.add_edge("retrieve", "grade")
    graph.add_edge("grade",    "generate")
    graph.add_edge("generate", END)

    return graph.compile()


rag_app = build_rag_graph()


def run_rag(question: str, department: Optional[str] = None) -> dict:
    """Main entry point called by FastAPI."""
    initial_state: RAGState = {
        "question":       question,
        "department":     department,
        "retrieved_docs": [],
        "relevant_docs":  [],
        "answer":         "",
        "source_info":    [],
        "is_greeting":    False,
    }
    result = rag_app.invoke(initial_state)
    return {
        "answer":  result["answer"],
        "sources": result["source_info"],
    }