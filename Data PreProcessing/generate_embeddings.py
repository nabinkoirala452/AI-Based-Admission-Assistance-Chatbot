"""
Embedding Generator for University Q&A Chatbot
================================================
Reads qa_complete_pairs.json and converts all Q&A pairs
into vector embeddings using all-MiniLM-L6-v2.

Saves everything into a ChromaDB folder:
  - chroma_db/   → the vector database (vectors + text + metadata all in one)

Run:
    pip install sentence-transformers chromadb
    python generate_embeddings.py
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

# ── Step 1: Load your Q&A JSON file ───────────────────────────────────────────

print("\n📂 Step 1: Loading Q&A data...")

with open("qa_complete_pairs.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"   ✓ Loaded {len(data)} Q&A pairs")

# ── Step 2: Prepare text for embedding ────────────────────────────────────────
#
# We combine question + answer together so the embedding captures
# the full meaning — not just the question wording.
# Format: "question: <Q> answer: <A>"
# This gives much better search results when a student asks something.

print("\n📝 Step 2: Preparing text for embedding...")

ids         = []   # unique ID for each entry (ChromaDB requires this)
texts       = []   # what gets embedded (question + answer combined)
metadatas   = []   # source + category + Q + A (all stored inside ChromaDB)

for i, item in enumerate(data):
    q = item["question"].strip()
    a = item["answer"].strip()

    ids.append(f"qa_{i}")                        # unique ID like qa_0, qa_1 ...
    texts.append(f"question: {q} answer: {a}")   # combined text for embedding
    metadatas.append({
        "question":  q,
        "answer":    a,
        "source":    item.get("source", ""),      # e.g. "CSE AI & ML"
        "category":  item.get("category", "")     # e.g. "Placements"
    })

print(f"   ✓ Prepared {len(texts)} text entries")
print(f"   Example text : {texts[0][:80]}...")
print(f"   Example meta : source='{metadatas[0]['source']}' | category='{metadatas[0]['category']}'")

# ── Step 3: Load the embedding model ──────────────────────────────────────────
#
# all-MiniLM-L6-v2:
#   - Free, runs 100% on your laptop (no API key needed)
#   - Downloads once (~90 MB), then cached automatically
#   - Produces 384-dimensional vectors
#   - Perfect for short Q&A similarity matching

print("\n🤖 Step 3: Loading all-MiniLM-L6-v2 model...")
print("   (First run downloads ~90MB — this is a one-time download)")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("   ✓ Model loaded!")

# ── Step 4: Generate embeddings ───────────────────────────────────────────────
#
# encode() converts each text string into a 384-number vector.
# show_progress_bar=True shows a live progress bar in the terminal.
# For 451 entries this takes about 5–10 seconds on a normal laptop.

print("\n⚡ Step 4: Generating embeddings...")
print("   Converting each Q&A into a 384-dimensional vector...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    batch_size=32         # process 32 at a time (efficient for CPU)
)

print(f"\n   ✓ Generated {len(embeddings)} embeddings")
print(f"   ✓ Each vector has {len(embeddings[0])} dimensions")

# ── Step 5: Set up ChromaDB ───────────────────────────────────────────────────
#
# ChromaDB saves everything into a local folder called "chroma_db".
# No separate .pkl file needed — questions, answers, source, category
# are all stored together inside the database automatically.
#
# PersistentClient = saves to disk so data survives after script ends.

print("\n🗄️  Step 5: Setting up ChromaDB...")

client = chromadb.PersistentClient(path="chroma_db")

# Delete old collection if it exists (so re-running the script starts fresh)
try:
    client.delete_collection("university_qa")
    print("   ↻ Deleted old collection to start fresh")
except Exception:
    pass

collection = client.create_collection(
    name="university_qa",
    metadata={"hnsw:space": "cosine"}   # cosine similarity — better than L2 for text
)

print("   ✓ Collection 'university_qa' created")

# ── Step 6: Add everything into ChromaDB ──────────────────────────────────────
#
# We add in batches of 100 to avoid memory issues.
# ChromaDB stores: vectors + original text + metadata all together.
# No need for a separate .pkl file like FAISS required.

print("\n💾 Step 6: Storing embeddings + metadata into ChromaDB...")

batch_size = 100
total      = len(ids)

for start in range(0, total, batch_size):
    end = min(start + batch_size, total)
    collection.add(
        ids        = ids[start:end],
        embeddings = embeddings[start:end].tolist(),
        documents  = texts[start:end],
        metadatas  = metadatas[start:end]
    )
    print(f"   ✓ Stored batch {start}–{end} of {total}")

print(f"\n   ✓ All {collection.count()} entries saved to chroma_db/ folder")

# ── Step 7: Quick test — make sure search actually works ──────────────────────

print("\n🧪 Step 7: Running a quick search test...")

def search(query, top_k=3, filter_source=None):
    """
    Given a question, find the top_k most similar Q&A pairs.
    Optionally filter by source department using the where parameter.

    Examples:
        search("placement record")
        search("AI projects", filter_source="CSE AI & ML | CSE Data Science")
    """
    query_vector = model.encode([f"question: {query}"]).tolist()

    where = {"source": filter_source} if filter_source else None

    results = collection.query(
        query_embeddings = query_vector,
        n_results        = top_k,
        where            = where        # None = search across all departments
    )

    matches = []
    for i in range(len(results["ids"][0])):
        meta = results["metadatas"][0][i]
        matches.append({
            "rank":      i + 1,
            "question":  meta["question"],
            "answer":    meta["answer"],
            "source":    meta["source"],
            "category":  meta["category"],
            "score":     round(results["distances"][0][i], 4)  # lower = more similar
        })
    return matches


# Test 1 — general search across all departments
test_query = "What is the placement record of the college?"
print(f"\n   Test 1 (general): \"{test_query}\"")
for r in search(test_query, top_k=3):
    print(f"   [{r['rank']}] {r['source']} → {r['category']}")
    print(f"        Q: {r['question']}")
    print(f"        A: {r['answer'][:100]}...")
    print(f"        Score (lower = better): {r['score']}")
    print()

# Test 2 — filtered by department (this is the ChromaDB advantage over FAISS!)
test_query2 = "What programming languages are taught?"
print(f"   Test 2 (filtered to CSE AI & ML): \"{test_query2}\"")
for r in search(test_query2, top_k=2, filter_source="CSE AI & ML | CSE Data Science"):
    print(f"   [{r['rank']}] {r['source']} → {r['category']}")
    print(f"        Q: {r['question']}")
    print(f"        A: {r['answer'][:100]}...")
    print()

# ── Done ──────────────────────────────────────────────────────────────────────

print("=" * 55)
print("✅ All done! Your ChromaDB is ready:")
print()
print("   chroma_db/   → vector database folder")
print("                  (vectors + Q&A + metadata, all in one place)")
print()
print("📌 Next step: load this in your Streamlit chatbot:")
print()
print("   import chromadb")
print("   from sentence_transformers import SentenceTransformer")
print()
print("   client     = chromadb.PersistentClient(path='chroma_db')")
print("   collection = client.get_collection('university_qa')")
print("   model      = SentenceTransformer('all-MiniLM-L6-v2')")
print("=" * 55)
