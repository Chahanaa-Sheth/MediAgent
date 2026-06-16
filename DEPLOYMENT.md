# MediAgent - Setup & Deployment Guide

## Project Structure

```
mediagent/
├── backend/           # FastAPI backend
│   ├── models/       # Pydantic data models
│   ├── repositories/ # Data access layer
│   ├── services/     # Business logic layer
│   ├── routes/       # API endpoints
│   ├── agents/       # Medical reasoning agents
│   ├── rag/          # RAG system
│   ├── auth/         # Authentication
│   ├── utils/        # Utilities & error handling
│   ├── database/     # Database configuration
│   ├── prompts/      # LLM prompts
│   ├── main.py       # FastAPI app setup
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── services/ # API service layer
│   │   ├── hooks/    # Custom React hooks
│   │   ├── App.jsx   # Main component
│   │   └── main.jsx  # Entry point
│   ├── .env.local    # Environment variables
│   └── package.json
└── README.md
```

## Backend Setup

### Prerequisites
- Python 3.9+
- MongoDB (local or Atlas)
- Groq API key
- Pinecone API key (optional)

### Installation

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```
   
   **Update .env with your credentials:**
   ```
   MONGO_URI=mongodb://localhost:27017  # or MongoDB Atlas URI
   GROQ_API_KEY=your_groq_api_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX=your_index_name
   SECRET_KEY=your_secret_key_here
   FRONTEND_URL=http://localhost:5173
   ```

5. **Run backend**
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Backend will be available at `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Create `.env.local`** (already created, but you can customize)
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

## Architecture Overview

### Backend Architecture

**Layered Architecture:**
- **Routes** (FastAPI endpoints) → **Services** (Business logic) → **Repositories** (Data access) → **Database**

**Key Components:**
1. **API Routes** (`routes/`)
   - `auth.py` - User authentication
   - `chats.py` - Chat management
   - `analysis.py` - Medical analysis (main endpoint)

2. **Services** (`services/`)
   - `UserService` - User management
   - `ChatService` - Chat lifecycle
   - `AnalysisService` - Medical analysis orchestration
   - `RAGService` - Knowledge retrieval
   - `LLMService` - LLM operations
   - `medical_reasoning.py` - Symptom extraction, severity scoring, agent routing

3. **Medical Reasoning Pipeline**
   - **SymptomExtractor** - Converts free text to structured medical context
   - **SeverityScorer** - Calculates 0-100 severity score with level classification
   - **AgentRouter** - Intelligently routes to necessary agents (emergency, specialist, drug, research)
   - **LangGraph Orchestrator** - Executes agents based on routing decisions

4. **Data Models** (`models/`)
   - Strongly typed Pydantic models for all data
   - Medical context with confidence scores

### Frontend Architecture

**Component Structure:**
- Monolithic App.jsx with modular hooks
- Real-time streaming with Server-Sent Events
- Custom hooks for auth, chat, and streaming

**API Integration:**
- APIService handles all backend communication
- Automatic SSE parsing and event handling
- Streaming chunks rendered in real-time

## Key Features

### Backend Features
✅ **Service/Repository Pattern** - Clean architecture with separation of concerns
✅ **Medical Reasoning** - Symptom extraction, severity scoring, confidence calculation
✅ **Intelligent Agent Routing** - Only runs necessary agents based on input
✅ **Real-time Streaming** - Server-Sent Events for live response streaming
✅ **Error Handling** - Structured exception handling with logging
✅ **Database Optimization** - Proper indexes for efficient queries
✅ **RAG System** - Multi-source knowledge retrieval (local, PubMed, Pinecone)

### Frontend Features
✅ **Real-time Streaming** - Display response chunks as they arrive
✅ **Chat History** - Persistent conversation management
✅ **Error Handling** - User-friendly error messages
✅ **Modern UI** - Dark mode with Tailwind CSS
✅ **Responsive Design** - Works on desktop and tablet
✅ **PDF Upload** - Upload and ingest medical documents

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token

### Chats
- `POST /api/chats/new` - Create new chat
- `POST /api/chats/list` - Get user's chats
- `POST /api/chats/delete` - Delete a chat
- `POST /api/chats/rename` - Rename a chat

### Analysis
- `POST /api/analyze` - Stream medical analysis (Server-Sent Events)
- `POST /api/upload-pdf` - Upload PDF for RAG
- `POST /api/ingest-pubmed` - Ingest PubMed research papers

## Stream Response Format

The `/api/analyze` endpoint streams Server-Sent Events with the following types:

```javascript
// Status update
{ type: "status", data: { message: "Extracting medical context..." } }

// Symptom extraction
{ type: "extraction", data: { symptoms: [...], confidence: 0.85 } }

// Severity scoring
{ type: "severity", data: { score: 45, level: "HIGH", reasoning: "..." } }

// Agent routing
{ type: "routing", data: { agents: ["emergency_agent", "specialist_agent"] } }

// LLM chunk (streaming)
{ type: "chunk", data: { content: "text chunk..." } }

// Completion
{ type: "done", data: { success: true } }

// Error
{ type: "error", data: { message: "error message" } }
```

## Environment Variables

### Backend (.env)
```
MONGO_URI=mongodb://...
GROQ_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX=...
SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

## Running Tests

### Backend
```bash
# (Add pytest setup when ready)
pytest
```

### Frontend
```bash
# (Add Vitest setup when ready)
npm run test
```

## Production Deployment

### Backend (Railway/Render)
1. Set environment variables in deployment platform
2. Deploy from git repository
3. Ensure MongoDB Atlas is configured
4. Set CORS_ORIGINS to your frontend domain

### Frontend (Vercel)
1. Set `VITE_API_URL` to production backend URL
2. Deploy from git repository
3. Vercel will automatically build with `npm run build`

## Monitoring & Logging

- All services use structured logging via `Logger` class
- Logs include timestamps, severity, and context
- Check backend logs for medical reasoning decisions (extracted context, agents run, confidence)

## Troubleshooting

### Backend won't start
- Check MongoDB connection: `MONGO_URI` is correct
- Verify all API keys are set in `.env`
- Run `python -m pip install -r requirements.txt` to update dependencies

### Frontend can't connect to backend
- Ensure `VITE_API_URL` in `.env.local` matches backend URL
- Check CORS configuration in `main.py`
- Verify backend is running on port 8000

### Streaming not working
- Check browser console for errors
- Verify backend is returning Server-Sent Events format
- Check network tab to see response type

## Next Steps for Production

1. **Add Input Validation** - Sanitize all user inputs
2. **Implement Rate Limiting** - Prevent abuse of endpoints
3. **Add Request Logging** - Track API usage
4. **Setup Monitoring** - Use Sentry or similar for error tracking
5. **Add Tests** - Unit tests for services, integration tests for endpoints
6. **Optimize Models** - Cache LLM responses, optimize RAG retrieval
7. **Add User Analytics** - Track user behavior and symptom patterns
8. **Implement Feedback Loop** - Let users rate response quality

## Support & Questions

Refer to code comments for implementation details. Each service includes docstrings explaining functionality.
