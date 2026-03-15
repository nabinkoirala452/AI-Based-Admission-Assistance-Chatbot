# 🎓 AI-Based Admission Assistance Chatbot
### Vignan's Foundation for Science, Technology & Research 

---

## 📌 Table of Contents

- [Introduction](#introduction)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Frontend](#frontend)
- [Backend](#backend) ← _to be filled by backend team_
- [How to Run](#how-to-run)
- [Deployment](#deployment)
- [Team](#team)

---

## 📖 Introduction

This project is an **AI-powered Admission Assistance Chatbot** built for **Vignan's FSTR University**. It is designed to be embedded on the university's official website to assist prospective students with instant, personalized guidance on:

- Admission procedures and eligibility criteria
- Course and department details
- Application deadlines
- EAMCET and other entrance exam guidance
- University rankings, accreditations, and facilities

The chatbot uses **Retrieval-Augmented Generation (RAG)** — a cutting-edge AI technique that combines a vector knowledge base (built from real university Q&A data) with a Large Language Model (LLaMA 3 via Groq) to generate accurate, context-aware answers.

---

## ❗ Problem Statement

Prospective students often face challenges in obtaining accurate information about:
- Admission procedures and eligibility criteria
- Course details and department-specific queries
- Important deadlines

This leads to confusion, delays, and missed opportunities. The goal is to develop an AI-powered chatbot that provides **instant, personalized guidance** — ensuring a smooth and efficient admission experience for every student.

---

## ✅ Solution Overview

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

## 🛠️ Tech Stack

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

## 📁 Project Structure

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

## 🎨 Frontend

The frontend is a **React application** built with Vite. It consists of two parts:

1. **University Landing Page** — a full informational webpage about Vignan's FSTR University
2. **Floating Chatbot Widget** — an AI chat assistant in the bottom-right corner

### Features

| Feature | Description |
|---|---|
| 🏠 Landing Page | Hero section, stats bar, departments, highlights, contact |
| 💬 Floating Chat Widget | Opens/closes with a toggle button (bottom-right) |
| 🏫 Department Filter | Dropdown to filter questions by department (17 departments) |
| 💡 Suggested Questions | Dynamic chips that change based on selected department |
| 📜 Chat History | Logs all conversations in a separate History tab |
| ⌨️ Typing Indicator | Animated dots while bot is generating a response |
| ⚠️ Error Handling | Shows retry button if backend is unreachable |
| 📱 Responsive Design | Works on desktop and mobile screens |

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

## ⚙️ Backend

> 📝 _This section is to be completed by the backend team._

The backend should be a **FastAPI** application that exposes a `/chat` endpoint. It must:

- Parse the Excel knowledge base and ingest Q&A pairs into ChromaDB with department metadata
- Accept `{ message, department }` from the frontend
- Run the RAG pipeline (embed → retrieve → generate)
- Return `{ response }` to the frontend
- Enable CORS for all origins

**See `BACKEND_CONTRACT.md` for the full technical specification.**

---

## 🚀 Deployment

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

## 👥 Team

| Role | Responsibility |
|---|---|
| Frontend Developer | React UI, Chatbot Widget, Landing Page |
| Backend Developer | FastAPI, RAG Pipeline, ChromaDB, Groq Integration |
| Data / AI Engineer | Excel preprocessing, Embeddings, LangChain |

---

## 📄 License

This project is developed for academic and institutional purposes at **Vignan's FSTR University**.

---

> 💡 _Have questions about the codebase? Check `BACKEND_CONTRACT.md` for the full API specification or raise an issue in the repository._
