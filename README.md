#  MediAgent

### Multi-Agent Medical AI Assistant powered by LangGraph, FastAPI, React, RAG, PubMed, Pinecone, and ChromaDB

MediAgent is an AI-powered healthcare research assistant that combines multiple specialized medical agents, Retrieval-Augmented Generation (RAG), medical literature retrieval, PDF intelligence, and clinical reasoning workflows to generate structured medical analysis reports.

> ⚠️ Disclaimer: MediAgent is intended for educational and informational purposes only and does not provide medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.

---

# Demo

## Medical Emergency Detection

![MediAgent Demo](images/chest-pain-demo.png)

MediAgent can identify emergency symptoms, estimate severity, generate differential diagnoses, recommend specialists, and provide evidence-based follow-up questions.

---

# Features

## Multi-Agent Architecture

MediAgent uses specialized AI agents coordinated through LangGraph orchestration.

### Emergency Agent

- Detects red-flag symptoms
- Identifies medical emergencies
- Escalates urgent cases

### Diagnosis Agent

- Generates differential diagnoses
- Assigns confidence scores
- Explains diagnostic reasoning

### Specialist Agent

- Recommends appropriate medical specialists
- Suggests care pathways

### Follow-Up Agent

- Generates targeted clinical questions
- Improves diagnostic accuracy

### Research Agent

- Retrieves evidence from:
  - PubMed
  - ChromaDB
  - Pinecone
  - Uploaded PDFs
- Provides supporting medical knowledge

---

# Key Capabilities

### Symptom Analysis

- Medical symptom extraction
- Confidence scoring
- Severity assessment
- Clinical reasoning

### PDF Medical Report Analysis

- Upload blood reports
- Upload laboratory reports
- Upload medical documents
- Automatic medical summarization

### Retrieval-Augmented Generation (RAG)

- PubMed integration
- Pinecone vector search
- ChromaDB local retrieval
- PDF knowledge base retrieval

### Research-Augmented Responses

- Evidence-supported recommendations
- Retrieved medical context
- Source transparency

### User Features

- JWT Authentication
- User Accounts
- Chat History
- Persistent Conversations
- Medical Analysis Trace

---

# System Architecture

![System Architecture](images/architecture.png)

---

# RAG Pipeline

![RAG Pipeline](images/rag-pipeline.png)

---

# AI Workflow

MediAgent follows a multi-stage medical reasoning pipeline:

```text
User Input
      │
      ▼
Symptom Extraction
      │
      ▼
Severity Analysis
      │
      ▼
Agent Routing
      │
      ├── Emergency Agent
      ├── Diagnosis Agent
      ├── Specialist Agent
      ├── Follow-Up Agent
      └── Research Agent
      │
      ▼
RAG Retrieval
      │
      ├── PubMed
      ├── ChromaDB
      ├── Pinecone
      └── PDF Knowledge Base
      │
      ▼
LLM Synthesis
      │
      ▼
Clinical Response
```

---

# Multi-Agent Routing

The LangGraph orchestrator dynamically activates only the agents required for a specific medical case.

![Agent Routing](images/routing.png)

Activated agents may include:

- emergency_agent
- diagnosis_agent
- specialist_agent
- followup_agent
- research_agent

---

# Symptom Extraction & Severity Assessment

MediAgent automatically extracts clinically relevant symptoms and determines urgency levels.

![Symptom Extraction](images/extraction.png)

Features:

- Symptom normalization
- Confidence scoring
- Duration extraction
- Severity classification
- Emergency detection

Severity levels:

- LOW
- MODERATE
- HIGH
- CRITICAL

---

# PDF Medical Report Analysis

Users can upload laboratory reports and medical documents for automated analysis.

![PDF Analysis](images/pdf-analysis.png)

Capabilities:

- PDF ingestion
- Text extraction
- Vector indexing
- Medical summarization
- Context-aware retrieval

---

# Example Analysis

Input:

```text
I have crushing chest pain radiating to my left arm,
sweating, dizziness, and shortness of breath.
```

Output:

- Severity: CRITICAL
- Recommended Specialist: Cardiologist
- Differential Diagnoses:
  - Myocardial Infarction
  - Pulmonary Embolism
  - Angina
- Follow-up Questions
- Emergency Guidance

---

# Project Structure

```text
mediagent
│
├── backend
│   │
│   ├── agents
│   │   ├── diagnosis_agent.py
│   │   ├── emergency_agent.py
│   │   ├── specialist_agent.py
│   │   ├── followup_agent.py
│   │
│   ├── auth
│   ├── database
│   ├── models
│   ├── prompts
│   ├── repositories
│   ├── routes
│   ├── services
│   ├── tools
│   ├── vectorstore
│   │
│   └── main.py
│
├── frontend
│   │
│   ├── public
│   ├── src
│   │   ├── components
│   │   ├── hooks
│   │   ├── services
│   │   └── App.jsx
│   │
│   └── package.json
│
├── images
│
└── README.md
```

---

# Tech Stack

## Backend

- FastAPI
- LangGraph
- LangChain
- MongoDB
- ChromaDB
- Pinecone
- Groq API
- Pydantic

## Frontend

- React
- Vite
- Axios
- React Markdown
- CSS

## AI / RAG

- LangGraph
- Retrieval-Augmented Generation
- Semantic Search
- Vector Databases
- Medical Literature Retrieval

---

# Security Features

- JWT Authentication
- Password Hashing
- Protected Routes
- User Isolation
- Environment Variable Secrets
- Request Validation

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Chahanaa-Sheth/MediAgent.git

cd MediAgent
```

---

## Backend Setup

```bash
cd backend

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
```

### Environment Variables

Create:

```env
GROQ_API_KEY=your_groq_key

PINECONE_API_KEY=your_pinecone_key

MONGO_URI=your_mongodb_uri

SECRET_KEY=your_secret_key
```

### Run Backend

```bash
uvicorn main:app --reload
```

Backend:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# Future Improvements

- Medical citation viewer
- Streaming token responses
- Pinecone hybrid search
- Advanced reranking
- Drug interaction engine
- Clinical guideline integration
- Agent observability dashboard
- Docker deployment
- Kubernetes deployment
- Evaluation framework

---

# What This Project Demonstrates

This project showcases:

- Multi-Agent Systems
- LangGraph Orchestration
- Retrieval-Augmented Generation
- FastAPI Backend Development
- React Frontend Development
- Medical AI Workflows
- Semantic Search
- Vector Databases
- Production Software Architecture
- Full-Stack Engineering

---

# Author

### Chahanaa Sheth

AI/ML Engineer • Full-Stack Developer • Medical AI Enthusiast

GitHub:
https://github.com/Chahanaa-Sheth

LinkedIn:
https://linkedin.com/in/chahanaa-sheth

---

# 📄 License

MIT License

Copyright (c) 2026 Chahanaa Sheth
