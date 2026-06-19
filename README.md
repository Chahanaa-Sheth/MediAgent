# MediAgent

**Multi-Agent Medical AI Assistant powered by LangGraph, RAG, FastAPI, React, PubMed, Pinecone, and ChromaDB**

MediAgent is a production-style AI healthcare assistant that combines multiple specialized agents, retrieval-augmented generation (RAG), medical research retrieval, and reasoning workflows to provide evidence-based medical guidance.

> ⚠️ MediAgent is for educational and informational purposes only and does not replace professional medical advice, diagnosis, or treatment.

---

## Features

### Multi-Agent Architecture

MediAgent uses specialized AI agents orchestrated through LangGraph:

* Research Agent

  * Retrieves evidence from PubMed and knowledge bases
  * Summarizes medical literature

* Specialist Agent

  * Suggests appropriate medical specialists
  * Recommends care pathways

* Drug Agent

  * Reviews medications
  * Detects potential interactions

* Emergency Agent

  * Detects red-flag symptoms
  * Escalates urgent situations
 
* Multi-Agent Medical Analysis
* Differential Diagnosis Engine
* Severity Assessment
* Follow-up Question Generation
* PubMed Research Retrieval
* RAG Pipeline
* PDF Medical Report Analysis
* Real-Time Streaming Responses
* Chat History & Persistence
* JWT Authentication

---

## AI Capabilities

### Retrieval-Augmented Generation (RAG)

Supports retrieval from:

* PubMed
* Uploaded PDF documents
* ChromaDB
* Pinecone Vector Database

### Medical Reasoning

Workflow:

1. Symptom Extraction
2. Severity Analysis
3. Medical Research Retrieval
4. Specialist Recommendation
5. Response Generation

### Source Transparency

Responses can include:

* Research citations
* Retrieved medical documents
* Supporting evidence
* Confidence indicators

---

## System Architecture

```text
User
 │
 ▼
React Frontend
 │
 ▼
FastAPI Backend
 │
 ▼
LangGraph Orchestrator
 │
 ├── Research Agent
 ├── Specialist Agent
 ├── Drug Agent
 └── Emergency Agent
 │
 ▼
RAG Layer
 │
 ├── PubMed
 ├── Pinecone
 ├── ChromaDB
 └── Uploaded PDFs
 │
 ▼
LLM Provider (Groq)
```

---

## Project Structure

```text
mediagent/
│
├── backend/
│   ├── agents/
│   ├── auth/
│   ├── database/
│   ├── models/
│   ├── prompts/
│   ├── rag/
│   ├── repositories/
│   ├── routes/
│   ├── services/
│   ├── tools/
│   ├── vectorstore/
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
│
└── README.md
```

---

## Tech Stack

### Backend

* FastAPI
* LangGraph
* LangChain
* MongoDB
* ChromaDB
* Pinecone
* Groq API

### Frontend

* React
* Vite
* Axios
* React Markdown

### AI / RAG

* Vector Search
* Semantic Retrieval
* Medical Research Retrieval
* PDF Knowledge Bases

---

## Installation

### Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create:

```env
GROQ_API_KEY=your_api_key
PINECONE_API_KEY=your_api_key
MONGO_URI=your_mongodb_uri
SECRET_KEY=your_secret
```

### Run Backend

```bash
uvicorn main:app --reload
```

---

### Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Security Features

* JWT Authentication
* Password Hashing
* User Isolation
* Environment-Based Secrets
* Input Validation
* Protected API Routes

---

## Medical Safety

* Emergency symptom detection
* Specialist recommendations
* Evidence-supported responses
* Medical disclaimers
* Confidence-aware outputs

---

## Future Improvements

* Agent execution traces
* Confidence scoring
* Advanced reranking
* Streaming responses
* Medical citation viewer
* Observability and monitoring
* Production deployment pipeline

---

## Why This Project Matters

MediAgent demonstrates:

* Multi-Agent Systems
* LangGraph Orchestration
* Retrieval-Augmented Generation
* Medical AI Workflows
* Vector Databases
* Full-Stack Development
* Production-Oriented Architecture

---

## License

MIT License
