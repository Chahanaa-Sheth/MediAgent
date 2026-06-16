from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import fitz
import shutil
from models.models import AnalysisRequest
from services.chat_service import ChatService
from services.analysis_service import AnalysisService
from services.rag_service import RAGService
from services.llm_service import LLMService
from repositories.chat_repository import ChatRepository
from database.db import chat_collection
from rag.pdf_ingest import ingest_pdf
from rag.pubmed_ingest import ingest_pubmed
from utils.exceptions import Logger, ChatNotFoundError
from uuid import uuid4

router = APIRouter(prefix="/api", tags=["analysis"])
logger = Logger("analysis_router")


def get_services():
    """Dependency injection for services"""
    chat_repo = ChatRepository(chat_collection)
    chat_service = ChatService(chat_repo)
    rag_service = RAGService()
    llm_service = LLMService()
    analysis_service = AnalysisService(chat_service, rag_service, llm_service)
    return {
        "chat_service": chat_service,
        "analysis_service": analysis_service,
        "rag_service": rag_service
    }


@router.post("/analyze")
async def analyze_symptom(request: AnalysisRequest, services: Dict[str, Any] = Depends(get_services)):
    """Stream medical analysis with real-time updates"""
    try:
        chat_id = request.chat_id
        symptom = request.symptom

        # Verify chat exists
        if not chat_id:
            chat_id = str(uuid4())

        logger.info("Starting analysis", chat_id=chat_id, symptom_length=len(symptom))

        # Return streaming response
        async def event_generator():
            async for event in services["analysis_service"].analyze_symptom_stream(symptom, chat_id):
                yield event

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.error("Analysis failed", error=str(e), chat_id=request.chat_id)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), services: Dict[str, Any] = Depends(get_services)):
    """Upload and ingest PDF"""
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        logger.info("Uploading PDF", filename=file.filename)

        # Save file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract text with fitz
        doc = fitz.open(file_path)
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()

        # Ingest into vector store
        await services["rag_service"].ingest_pdf(pdf_text, file.filename)

        logger.info("PDF uploaded successfully", filename=file.filename)
        return {"success": True, "message": f"{file.filename} uploaded successfully"}

    except Exception as e:
        logger.error("PDF upload failed", error=str(e), filename=file.filename)
        raise HTTPException(status_code=500, detail=f"PDF upload failed: {str(e)}")


@router.post("/ingest-pubmed")
async def ingest_research(data: Dict[str, Any], services: Dict[str, Any] = Depends(get_services)):
    """Ingest PubMed research papers"""
    try:
        topic = data.get("topic")
        if not topic:
            raise HTTPException(status_code=400, detail="topic required")

        logger.info("Ingesting PubMed papers", topic=topic)

        # Ingest papers
        ingest_pubmed(topic)

        logger.info("PubMed papers ingested", topic=topic)
        return {"success": True, "message": f"Research papers added for {topic}"}

    except Exception as e:
        logger.error("PubMed ingestion failed", error=str(e), topic=data.get("topic"))
        raise HTTPException(status_code=500, detail=f"PubMed ingestion failed: {str(e)}")
