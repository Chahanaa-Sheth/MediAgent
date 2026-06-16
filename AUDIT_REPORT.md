# MediAgent Architecture Audit Report
**Date**: June 4, 2026  
**Status**: COMPREHENSIVE AUDIT COMPLETED  
**Production Readiness**: 4/10 (blocking issues identified)

---

## Executive Summary

MediAgent has been well-refactored into a modular architecture with separation of concerns, but multiple critical issues prevent it from functioning correctly:

1. **Async/Sync Mismatch**: All repository methods are `async` but execute synchronous MongoDB operations
2. **Chat Isolation Broken**: LangGraph receives empty history, defeating context per-conversation
3. **Data Format Inconsistencies**: RAG results passed incorrectly to prompt builder
4. **Frontend State Stale**: Chat selection loads from local state instead of fetching fresh data
5. **Missing Backend Dependency File**: No requirements.txt
6. **Specialist Routing Too Simplistic**: Single keyword matching, no confidence/severity scoring
7. **Chroma Database Stubbed**: Only 5 hardcoded documents, no real ingestion

---

## Architecture Overview

```
FRONTEND (React 19 + Vite)
├── App.jsx (main chat interface)
├── hooks/index.js (auth, chat, stream state)
└── services/api.js (API client)

BACKEND (FastAPI)
├── main.py (app setup, CORS, routers)
├── routes/
│   ├── auth.py (/api/auth/signup, /api/auth/login)
│   ├── chats.py (/api/chats/new, /api/chats/list, /api/chats/delete, /api/chats/rename)
│   └── analysis.py (/api/analyze, /api/upload-pdf, /api/ingest-pubmed)
├── services/
│   ├── chat_service.py (chat CRUD)
│   ├── analysis_service.py (orchestration, streaming)
│   ├── llm_service.py (Groq API)
│   ├── rag_service.py (multi-source search)
│   └── medical_reasoning.py (extraction, severity, routing)
├── repositories/
│   ├── base_repository.py (MongoDB CRUD layer)
│   ├── chat_repository.py (chat-specific queries)
│   └── user_repository.py (user queries)
├── agents/
│   ├── langgraph_orchestrator.py (LangGraph graph + state machine)
│   ├── specialist_agent.py (keyword → specialist)
│   ├── emergency_agent.py (emergency detection)
│   ├── research_agent.py (RAG + PubMed)
│   └── drug_agent.py (FDA OpenAPI)
├── models/models.py (Pydantic schemas)
├── database/db.py (MongoDB connection + indexes)
├── rag/
│   ├── rag_system.py (delegator to Pinecone)
│   ├── pinecone_store.py (Pinecone operations)
│   ├── pubmed_ingest.py (ingestion)
│   └── pdf_ingest.py (PDF processing)
├── vectorstore/chroma_store.py (Chroma local store)
└── prompts/
    ├── system_prompt.py (detailed medical prompt)
    └── prompt_builder.py (simpler version)

DATABASE (MongoDB)
├── users collection
│   └── {username, password_hash, created_at, updated_at, is_active}
└── chats collection
    └── {chat_id, user_id, title, messages[], created_at, updated_at, is_active, metadata}
```

---

## CRITICAL ISSUES IDENTIFIED

### 1. ⚠️ ASYNC/SYNC MISMATCH (BLOCKING)

**Severity**: CRITICAL  
**Location**: `repositories/base_repository.py`, `repositories/chat_repository.py`

**Problem**:
- All repository methods are declared `async` but use **synchronous** MongoDB operations
- Routes call these `async` methods correctly, but they don't actually await anything
- This breaks Python's async execution model and can cause hanging/race conditions

**Evidence**:
```python
# repositories/base_repository.py line 13-17
async def create(self, data: Dict[str, Any]) -> str:
    result = self.collection.insert_one(data)  # ← SYNC CALL IN ASYNC FUNCTION
    self.logger.info(...)
    return str(result.inserted_id)
```

**Fix Required**: Convert all MongoDB calls to use Motor (async MongoDB driver) or remove `async` and make callers blocking.

---

### 2. ⚠️ CHAT CONTEXT ISOLATION BROKEN (CRITICAL)

**Severity**: CRITICAL  
**Location**: `agents/langgraph_orchestrator.py` line 130

**Problem**:
- LangGraph always receives empty history: `"history": []`
- Medical reasoning extracts context from history (see `medical_reasoning.py` line 61-65)
- This means **every chat receives NO context from previous messages**
- Duplicate symptoms aren't deduplicated across turns within the same chat
- Users lose conversation continuity

**Evidence**:
```python
# analysis_service.py line 32
chat = await self.chat_service.get_chat_history(chat_id, limit=50)
history = [msg for msg in chat.get("messages", [])]  # ← Correctly fetched

# agents/langgraph_orchestrator.py line 128-131
result = app_graph.invoke({
    "symptom": symptom,
    "history": [],  # ← ALWAYS EMPTY! BUG!
    ...
})
```

**Fix Required**: Pass `history` from `analysis_service.py` into LangGraph.

---

### 3. ⚠️ RAG RESULTS FORMAT MISMATCH (CRITICAL)

**Severity**: HIGH  
**Location**: `services/analysis_service.py` line 74-77

**Problem**:
- `rag_service.search_all_sources()` returns a dict with keys: `{"local_documents": [...], "pubmed_papers": [...], "pinecone_results": [...]}`
- `prompt_builder.build_user_turn()` expects `rag_results` to be a string
- Passing a dict to a function expecting a string causes format errors

**Evidence**:
```python
# analysis_service.py line 67-68
rag_results = await self.rag_service.search_all_sources(symptom)
# Returns: {"local_documents": [...], "pubmed_papers": [...], "pinecone_results": [...]}

# analysis_service.py line 74-77
user_prompt = build_user_turn(
    symptom=symptom,
    rag_results=rag_results.get("local_documents", []),  # ← ONLY LOCAL! Missing PubMed + Pinecone
    formatted_history=formatted_history
)

# prompt_builder.py line 9-10
rag_block = (
    rag_results.strip()  # ← EXPECTS STRING, but might get list!
    ...
)
```

**Fix Required**: Format `rag_results` as a concatenated string before passing to `build_user_turn()`.

---

### 4. ⚠️ FRONTEND LOADS STALE CHAT (HIGH)

**Severity**: HIGH  
**Location**: `frontend/src/App.jsx` line 54-57

**Problem**:
- When user clicks a chat in sidebar, `loadChat()` uses the chat object from state
- This is the chat from the last `/api/chats/list` call, which may be stale
- If messages were added externally, the frontend won't see them
- No refresh mechanism

**Evidence**:
```javascript
// App.jsx line 54-57
const loadChat = (selectedChat) => {
    chat.setCurrentChatId(selectedChat.chat_id);
    chat.setMessages(selectedChat.messages || []);  // ← Uses stale .messages from state
};
```

**Fix Required**: Fetch chat history from server when selected.

---

### 5. ⚠️ MISSING REQUIREMENTS.TXT (BLOCKER)

**Severity**: HIGH  
**Location**: `/Users/macbook/Desktop/mediagent/backend/`

**Problem**:
- No `requirements.txt` or `pyproject.toml`
- Dependencies are undocumented
- Cannot reproduce environment
- Cannot run backend without guessing dependencies

**Fix Required**: Create `requirements.txt` from observed imports.

---

### 6. ⚠️ SPECIALIST RECOMMENDATION OVERSIMPLIFIED (MEDICAL)

**Severity**: MEDIUM  
**Location**: `agents/specialist_agent.py`

**Problem**:
- Uses single keyword matching: `if "headache" in symptom`
- No confidence scoring, no severity consideration
- Maps incorrectly:
  - "headache" → Neurologist (❌ Could be tension headache → general practitioner)
  - "headache + chest pain" → Neurologist (❌ Should be Cardiologist first)
  - "fever" → General Physician (✓ Correct, but too broad)

**Example of Incorrect Routing**:
- User: "I have a mild headache after too much coffee"
- System: "Recommended Specialist: Neurologist"
- Should be: "General Physician first; no specialist needed"

**Fix Required**: Use `medical_reasoning.py` AgentRouter logic instead of simple keyword matching.

---

### 7. ⚠️ CHROMA DATABASE STUBBED (INTEGRATION)

**Severity**: MEDIUM  
**Location**: `vectorstore/chroma_store.py` line 19-42

**Problem**:
- Only 5 hardcoded documents in Chroma initialization
- No real ingestion pipeline
- User-uploaded PDFs and custom documents not stored there
- `search_documents()` returns from tiny hardcoded set only

**Evidence**:
```python
def add_documents():
    docs = [
        "Migraine causes severe headaches...",
        "Fever may occur due to...",
        # ... only 5 total
    ]
```

**Fix Required**: 
- Implement proper PDF → Chroma ingestion in `rag/pdf_ingest.py`
- Use Pinecone as primary RAG, Chroma as secondary/local

---

### 8. ⚠️ SYNCHRONOUS RAG CALLS IN ASYNC CONTEXT

**Severity**: MEDIUM  
**Location**: `services/rag_service.py` line 28-44

**Problem**:
- Methods are `async` but call synchronous `search_documents()`, `search_pubmed()`
- No actual async operations happening
- Pinecone call is blocking
- Could cause performance issues

**Fix Required**: Use `asyncio.to_thread()` or make underlying calls async.

---

### 9. ⚠️ PROMPT BUILDER INCONSISTENCY

**Severity**: LOW  
**Location**: `prompts/prompt_builder.py` vs `prompts/system_prompt.py`

**Problem**:
- Two versions of `build_user_turn()` exist
- `system_prompt.py` (line 98) has more sophisticated version with better context management
- `prompts/prompt_builder.py` has simpler version  
- Code uses the simpler one

**Fix Required**: Use the sophisticated version from `system_prompt.py`.

---

### 10. ⚠️ EMPTY CHAT HANDLING

**Severity**: LOW  
**Location**: `repositories/chat_repository.py` line 52-57

**Problem**:
- `get_chat_history()` returns `None` for non-existent chats
- Calling code doesn't check for `None`, just calls `.get("messages", [])`
- Could cause AttributeError

**Fix Required**: Add explicit null check or ensure chat creation before retrieval.

---

## Database Schema Issues

✅ **Good**:
- Proper indexes on `chat_id`, `user_id`, `created_at`
- Soft delete with `is_active` flag
- Compound index on `(user_id, created_at)`

❌ **Issues**:
- No unique index on `(user_id, chat_id)` for enforcing ownership
- No TTL index on `created_at` for old chat cleanup
- No index on `is_active` for efficient soft-delete queries
- Chat title could have search index for "find chat" feature

---

## Frontend Issues Summary

| Issue | Severity | Impact |
|-------|----------|--------|
| Stale chat loading | HIGH | Users see old messages after deletion |
| No error boundaries | MEDIUM | App crashes on API errors |
| No reconnection logic | MEDIUM | Network errors not retried |
| Missing markdown rendering | LOW | Medical text not formatted nicely |
| No response metadata display | LOW | Users can't see confidence/sources |

---

## Tested Flows

✅ **Working**:
- Auth routes are properly defined
- Chat CRUD endpoints are wired correctly
- Route prefixes match frontend expectations (`/api/chats/*`, `/api/analyze`)
- Database connection and indexes initialize correctly
- LangGraph compilation succeeds
- FastAPI app starts without import errors

❌ **Broken or Untested**:
- Chat persistence across turns (context isolation)
- Streaming event format (RAG results format)
- Chat loading freshness
- Multi-source RAG aggregation

---

## Repair Priority

### **Phase 1 (Blocking - Fix First)**
1. Fix async/sync mismatch in repositories → use Motor or remove async
2. Pass history to LangGraph orchestrator
3. Fix RAG results format in prompt builder
4. Fetch chat fresh when selected in frontend
5. Create requirements.txt

### **Phase 2 (High Impact)**
6. Improve specialist routing with confidence scores
7. Fix synchronous RAG calls in async context
8. Add proper error handling in frontend
9. Implement PDF ingestion to Chroma

### **Phase 3 (Quality)**
10. Use sophisticated prompt builder
11. Add remaining database indexes
12. Add markdown rendering
13. Add response metadata display

---

## Next Steps

1. ✅ Architecture mapped
2. ⚠️ Issues identified (THIS DOCUMENT)
3. ➜ Begin Phase 1 repairs (backend async/sync, context isolation, RAG format)
4. ➜ Test each fix incrementally
5. ➜ Phase 2 repairs (routing, error handling)
6. ➜ Final validation and report
