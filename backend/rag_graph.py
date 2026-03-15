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
RELEVANCE_THRESHOLD = 0.55   # ChromaDB distance: lower = more similar; above this = not relevant
TOP_K = 4

# ── Singletons (loaded once at startup) ────────────────────────────────────────
_embedder = SentenceTransformer(EMBED_MODEL)
_chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _chroma_client.get_collection(COLLECTION_NAME)

_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,           # 0 = deterministic, no creative wandering
    max_tokens=512,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ── Graph state ────────────────────────────────────────────────────────────────
class RAGState(TypedDict):
    question: str
    department: Optional[str]    # department filter from UI
    retrieved_docs: List[dict]
    relevant_docs: List[dict]
    answer: str
    source_info: List[dict]

# ── Node 1: Retrieve from ChromaDB ────────────────────────────────────────────
def retrieve_node(state: RAGState) -> RAGState:
    question = state["question"]
    department = state.get("department")

    query_vector = _embedder.encode(question).tolist()

    # Build metadata filter if department is selected
    where_clause = {"source": department} if department else None

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
# The prompt is the single most important hallucination guard.
# "ONLY use the context" + no context → "I don't know" forces the model to stay on-rails.

ANSWER_PROMPT = ChatPromptTemplate.from_template("""
You are a university admission assistant. Your ONLY job is to answer questions
using the provided context. 

STRICT RULES:
- Answer ONLY from the context below. Do not use any outside knowledge.
- If the context contains the answer, give it directly and concisely.
- If the context does NOT contain enough information, respond EXACTLY:
  "I'm sorry, I don't have information about that in my knowledge base. Please contact the admissions office directly."
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
            "answer": "I'm sorry, I don't have information about that in my knowledge base. Please contact the admissions office directly.",
            "source_info": [],
        }

    # Build context from retrieved Q&A pairs
    context_parts = []
    source_info = []
    for doc in relevant_docs:
        context_parts.append(doc["document"])
        source_info.append({
            "category": doc["metadata"].get("category", ""),
            "source": doc["metadata"].get("source", ""),
            "distance": round(doc["distance"], 4),
        })

    context = "\n\n---\n\n".join(context_parts)

    answer = answer_chain.invoke({
        "context": context,
        "question": state["question"],
    })

    return {**state, "answer": answer, "source_info": source_info}


# ── Node 4: Hallucination guard ────────────────────────────────────────────────
# A lightweight second LLM call that checks whether the answer is grounded.
GUARD_PROMPT = ChatPromptTemplate.from_template("""
You are a fact-checker. Given the context and answer below, decide if the answer
is FULLY supported by the context, or if it contains information NOT in the context.

Context:
{context}

Answer:
{answer}

Respond with ONLY one word: "GROUNDED" or "UNGROUNDED".
""")

guard_chain = GUARD_PROMPT | _llm | StrOutputParser()

def guard_node(state: RAGState) -> RAGState:
    if not state["relevant_docs"] or not state["answer"]:
        return state

    context = "\n\n".join(d["document"] for d in state["relevant_docs"])
    verdict = guard_chain.invoke({
        "context": context,
        "answer": state["answer"],
    }).strip().upper()

    if verdict != "GROUNDED":
        return {
            **state,
            "answer": "I'm sorry, I don't have reliable information about that. Please contact the admissions office directly.",
            "source_info": [],
        }
    return state


# ── Build the graph ────────────────────────────────────────────────────────────
def build_rag_graph():
    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("grade", grade_node)
    graph.add_node("generate", generate_node)
    graph.add_node("guard", guard_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "grade")
    graph.add_edge("grade", "generate")
    graph.add_edge("generate", "guard")
    graph.add_edge("guard", END)

    return graph.compile()


# Compiled graph — imported by main.py
rag_app = build_rag_graph()


def run_rag(question: str, department: Optional[str] = None) -> dict:
    """Main entry point called by FastAPI."""
    initial_state: RAGState = {
        "question": question,
        "department": department,
        "retrieved_docs": [],
        "relevant_docs": [],
        "answer": "",
        "source_info": [],
    }
    result = rag_app.invoke(initial_state)
    return {
        "answer": result["answer"],
        "sources": result["source_info"],
    }