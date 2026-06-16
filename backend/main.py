from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routes
from routes import auth, chats, analysis
from database.db import initialize_database
from vectorstore.chroma_store import add_documents

# Initialize FastAPI app
app = FastAPI(
    title="MediAgent",
    description="AI Medical Research Assistant",
    version="1.0.0"
)

# Startup event to initialize database
@app.on_event("startup")
async def startup_event():
    await initialize_database()
    add_documents()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:5173")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chats.router)
app.include_router(analysis.router)


# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "MediAgent RAG AI Running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
