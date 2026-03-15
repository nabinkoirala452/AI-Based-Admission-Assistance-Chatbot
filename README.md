# AI-Based Admission Assistance Chatbot
### Vignan's Foundation for Science, Technology & Research 

---

## Table of Contents

- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Frontend](#frontend)
- [Backend](#backend)
- [Deployment](#deployment)


---

## Introduction

This project is an **AI-powered Admission Assistance Chatbot** built for **Vignan's University**. It is designed to be embedded on the university's official website to assist prospective students with instant, personalized guidance on:

- Admission procedures and eligibility criteria
- Course and department details
- Application deadlines
- EAMCET and other entrance exam guidance
- University rankings, accreditations, and facilities

The chatbot uses **Retrieval-Augmented Generation (RAG)** — a cutting-edge AI technique that combines a vector knowledge base (built from real university Q&A data) with a Large Language Model (LLaMA 3 via Groq) to generate accurate, context-aware answers.

---

## Problem Statement

Prospective students often face challenges in obtaining accurate information about:
- Admission procedures and eligibility criteria
- Course details and department-specific queries
- Important deadlines

This leads to confusion, delays, and missed opportunities. The goal is to develop an AI-powered chatbot that provides **instant, personalized guidance** — ensuring a smooth and efficient admission experience for every student.

---

## Solution Overview

```
Student asks a question on the university website
              ↓
     React Frontend (Chatbot UI)
              ↓
     FastAPI Backend (REST API)
              ↓
  RAG Pipeline (LangChain + ChromaDB)
    - Embed the query
    - Search university Q&A knowledge base
    - Retrieve top matching answers
              ↓
   LLaMA 3 via Groq API generates response
              ↓
        Answer shown to student
```

The knowledge base is built from **489 Q&A pairs** across **9 department sheets** extracted from the university's internal Excel file.

---

## Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| **Frontend** | React (Vite) | Free |
| **Backend** | FastAPI (Python) | Free |
| **LLM** | LLaMA 3 via Groq API | Free |
| **Embeddings** | sentence-transformers `all-MiniLM-L6-v2` | Free (local) |
| **Vector Database** | ChromaDB | Free (local) |
| **RAG Framework** | LangChain | Free |
| **Frontend Deploy** | Vercel | Free |
| **Backend Deploy** | Render | Free |

---

## Project Structure

```
AI-Based-Admission-Assistance-Chatbot/
│
├── frontend/                        ← React Application (this repo)
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatBot.jsx          ← Main chatbot floating widget
│   │   │   └── ChatBot.css          ← Chatbot styles
│   │   ├── App.jsx                  ← University landing page + chatbot mount
│   │   ├── App.css                  ← Landing page styles
│   │   ├── main.jsx                 ← React entry point
│   │   └── index.css                ← Global styles
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── backend/                         ← FastAPI Application (backend team)
│   ├── main.py                      ← FastAPI server & /chat endpoint
│   ├── rag_pipeline.py              ← LangChain RAG logic
│   ├── ingest.py                    ← Excel → ChromaDB ingestion script
│   ├── chroma_db/                   ← Local vector database (auto-generated)
│   ├── requirements.txt
│   └── .env                         ← GROQ_API_KEY (never commit this)
│
├── Data/
│   └── QA_Sessions_for_AI_.xlsx     ← Knowledge base (9 sheets, 489 Q&As)
│
├── Data PreProcessing/              ← Excel parsing & cleaning scripts
│
└── README.md                        ← You are here
```

---

## Frontend

The frontend is a **React application** built with Vite. It consists of two parts:

1. **University Landing Page** — a full informational webpage about Vignan's  University
2. **Floating Chatbot Widget** — an AI chat assistant in the bottom-right corner

### Features

| Feature | Description |
|---|---|
| Landing Page | Hero section, stats bar, departments, highlights, contact |
| Floating Chat Widget | Opens/closes with a toggle button (bottom-right) |
| Department Filter | Dropdown to filter questions by department (17 departments) |
| Suggested Questions | Dynamic chips that change based on selected department |
| Chat History | Logs all conversations in a separate History tab |
| Typing Indicator | Animated dots while bot is generating a response |
| Error Handling | Shows retry button if backend is unreachable |
| Responsive Design | Works on desktop and mobile screens |

### Frontend File Overview

```
src/
├── components/
│   ├── ChatBot.jsx    ← All chatbot logic & UI (department filter, messages, history)
│   └── ChatBot.css    ← All chatbot styles (animations, bubbles, dropdown)
├── App.jsx            ← Landing page (navbar, hero, stats, departments, footer)
└── App.css            ← Landing page styles
```

### API Call the Frontend Makes

The frontend sends this request to the backend:

```js
POST /chat
Content-Type: application/json

{
  "message": "What is the fee structure?",
  "department": "CSE AI & ML"   // null if "All Departments" selected
}
```

And expects this response:

```js
{
  "response": "The fee structure for CSE AI & ML is..."
}
```

The backend URL is configured in one place — `ChatBot.jsx`:

```js
const API_BASE_URL = "http://localhost:8000"; // Change to deployed URL
```

### Frontend Setup & Run

**Prerequisites:** Node.js (v16+)

```bash
# Step 1 — Navigate to frontend folder
cd frontend

# Step 2 — Install dependencies
npm install

# Step 3 — Start development server
npm run dev

# Step 4 — Open in browser
# http://localhost:5173
```

**Build for production:**
```bash
npm run build
```
This generates a `dist/` folder ready for deployment.

### Testing Frontend Without Backend

To test the UI without the backend running, temporarily replace `fetchBotResponse` in `ChatBot.jsx`:

```js
async function fetchBotResponse(userMessage, department) {
  await new Promise((res) => setTimeout(res, 1000)); // simulate delay
  return `Mock response for: <strong>${userMessage}</strong><br/>
          Department: ${department || "All"}`;
}
```

---

## Backend

The backend is a **FastAPI** application with a **Retrieval-Augmented Generation (RAG)** pipeline that powers the chatbot. Here's what happens on the backend:

### Backend Architecture

```
Student Question (from Frontend)
              ↓
FastAPI /chat endpoint receives request
              ↓
1. Greeting Check (fast-track for "hi", "hello", etc.)
              ↓
2. Embed Query (sentence-transformers)
              ↓
3. Retrieve from ChromaDB (vector similarity search)
              ↓
4. Grade Relevance (filter by threshold)
              ↓
5. Generate Answer (LLaMA 3.1 via Groq API using RAG context)
              ↓
Response sent back to Frontend with sources
```

### Backend Features

| Feature | Details |
|---|---|
| **LLM Model** | LLaMA 3.1 8B Instant (via Groq API) |
| **Embedding Model** | sentence-transformers `all-MiniLM-L6-v2` (local, no API key) |
| **Vector Database** | ChromaDB (local, persistent) |
| **RAG Framework** | LangChain + LanGraph |
| **Server** | FastAPI with CORS enabled |
| **Chat Endpoints** | `/chat` (POST), `/sources` (GET), `/health` (GET) |

### Backend Files Overview

```
backend/
├── main.py               ← FastAPI application & REST endpoints
├── rag_graph.py          ← LangChain graph (retrieve → grade → generate)
├── requirements.txt      ← Python dependencies
└── .env                  ← GROQ_API_KEY (⚠️ never commit this)
```

### Backend Setup & Run

**Prerequisites:**
- Python 3.9 or higher
- A free Groq API key (get it at [console.groq.com](https://console.groq.com))

#### Step 1 — Create One Python Virtual Environment (All-in-One)

Create a single shared Python virtual environment at the project root for both data preprocessing and backend:

```bash
# Navigate to project root (AI-Based-Admission-Assistance-Chatbot/)
cd ..

# Create a Python virtual environment
python -m venv venv

# Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies at once
pip install -r requirements.txt
```

> ℹ️ **One venv for everything** — You'll use this same activated environment for both data preprocessing and backend. No need to create separate environments. Your terminal should show `(venv)` at the prompt after activation.

#### Step 2 — Generate Q&A Embeddings (One-Time Setup)

Convert the Excel Q&A file into embeddings and store them in ChromaDB:

```bash
# Make sure venv is still activated, then navigate to data preprocessing
cd data_preprocessing

# Run the embedding generation script
python generate_embeddings.py
```

**What this does:**
- Reads `Data/qa_complete_pairs.json` (489 Q&A pairs)
- Converts each Q&A into 384-dimensional vectors using `all-MiniLM-L6-v2`
- Stores everything in `data_preprocessing/chroma_db/` (about 5–10 seconds on a normal laptop)
- The ChromaDB is now ready for the backend to query

**Expected output:**
```
✓ Loaded 489 Q&A pairs
✓ Prepared 489 text entries
✓ Model loaded!
✓ Generated 489 embeddings
✓ Added 489 entries to ChromaDB
```

#### Step 3 — Create `.env` File with Groq API Key

Create a file named `.env` in the `backend/` folder:

```bash
# backend/.env
GROQ_API_KEY=your_api_key_here
CHROMA_PATH=../data_preprocessing/chroma_db
```

**To get your free Groq API key:**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email or Google
3. Navigate to API Keys → Create New Key
4. Copy the key and paste it into `.env`

⚠️ **Never commit `.env` to Git!** It's already in `.gitignore`.

#### Step 4 — Start the FastAPI Server

```bash
# Make sure you're in the backend/ folder and venv is activated
cd backend
source venv/bin/activate  # (or venv\Scripts\activate on Windows)

# Start the server on port 8000
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### Step 5 — Test the Backend API

The backend exposes three endpoints:

**1. Health Check**
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

**2. Get Departments/Sources**
```bash
curl http://localhost:8000/sources
# Response: {"sources": ["CSE AI & ML", "CSE Data Science", "CSE CSBS", ...]}
```

**3. Chat Endpoint** — This is what the frontend calls
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the fee structure?",
    "department": "CSE AI & ML"
  }'

# Response:
# {
#   "response": "The fee structure for CSE AI & ML is...",
#   "sources": [
#     {"department": "CSE AI & ML", "category": "Fee Structure", "distance": 0.25},
#     ...
#   ]
# }
```

### Backend Flow Example

**User**: "How do I get an admission in ECE?"

1. **Greeting Check**: Not a greeting → continue
2. **Embedding**: "How do I get an admission in ECE?" → 384-dim vector
3. **Retrieve**: Search ChromaDB with department filter (if selected)
   - Find top 4 most similar Q&A pairs from ECE/Engineering sheets
4. **Grade**: Filter by relevance threshold (only keep distance < 0.70)
5. **Generate**: Pass relevant Q&A context + question to LLaMA 3.1 8B
   - LLM returns: "To get admission in ECE, you must meet the following eligibility criteria..."
6. **Return**: Frontend displays answer + sources

### Backend Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'langchain'` | Run `pip install -r requirements.txt` again |
| `CHROMA_PATH not found` | Make sure you ran `python generate_embeddings.py` first |
| `GROQ_API_KEY not set` | Create `.env` file with your API key |
| `Port 8000 already in use` | Change port: `uvicorn main:app --reload --port 8001` |
| `Connection refused` | Make sure backend server is running on port 8000 |
| `ChromaDB is empty` | Re-run: `cd data_preprocessing && python generate_embeddings.py` |

### Backend Environment Variables

| Variable | Required | Default | Example |
|---|---|---|---|
| `GROQ_API_KEY` | Yes | None | `gsk_abc123xyz...` |
| `CHROMA_PATH` | No | `../data_preprocessing/chroma_db` | `/absolute/path/to/chroma_db` |

### Common Workflow: Start Everything Fresh

```bash
# 1. Create and activate the shared venv (do this once)
cd ..
python -m venv venv

# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# 2. Generate embeddings (one-time setup)
cd data_preprocessing
python generate_embeddings.py

# 3. Start backend (from project root with venv still active)
cd ../backend
# Create .env with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env
echo "CHROMA_PATH=../data_preprocessing/chroma_db" >> .env
uvicorn main:app --reload --port 8000

# 4. Start frontend (in another terminal, keep backend running)
cd frontend
npm install
npm run dev

# 5. Open browser
# http://localhost:5173
```

---

## Deployment

### Frontend — Deploy on Vercel (Free)

```bash
# Install Vercel CLI
npm install -g vercel

# Inside frontend folder
cd frontend
vercel

# Follow prompts → get a live URL like:
# https://vignan-chatbot.vercel.app
```

### Backend — Deploy on Render (Free)

1. Push backend code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variable: `GROQ_API_KEY=your_key_here`
5. Deploy → get a live URL like: `https://vignan-chatbot-api.onrender.com`

### Connect Frontend to Backend

After backend is deployed, update this one line in `frontend/src/components/ChatBot.jsx`:

```js
const API_BASE_URL = "https://vignan-chatbot-api.onrender.com";
```

Then redeploy the frontend.

---



---

## License

This project is developed for academic and institutional purposes at VFSTR .

---

