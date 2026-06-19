from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from uuid import uuid4
from models.models import Chat
from repositories.chat_repository import ChatRepository
from services.chat_service import ChatService
from database.db import chat_collection
from utils.exceptions import ChatNotFoundError, Logger
from auth.jwt_handler import get_username_from_token

router = APIRouter(prefix="/api/chats", tags=["chats"])
logger = Logger("chats_router")


def get_chat_service() -> ChatService:
    """Dependency injection for ChatService"""
    chat_repo = ChatRepository(chat_collection)
    return ChatService(chat_repo)


def get_user_id_from_token(token: str = None) -> str:
    if not token:
        return "anonymous"

    username = get_username_from_token(token)
    return username if username else "anonymous"


@router.post("/new")
async def new_chat(data: Dict[str, Any], chat_service: ChatService = Depends(get_chat_service)):
    """Create a new chat"""
    try:
        token = data.get("token")
        user_id = get_user_id_from_token(token)

        result = await chat_service.create_chat(user_id, "New Chat")
        logger.info("New chat created", user_id=user_id, chat_id=result["chat_id"])
        return result
    except Exception as e:
        logger.error("Failed to create chat", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create chat")


@router.post("/list")
async def get_chats(data: Dict[str, Any], chat_service: ChatService = Depends(get_chat_service)):
    """Get all chats for user"""
    try:
        token = data.get("token")
        user_id = get_user_id_from_token(token)

        chats = await chat_service.get_user_chats(user_id, limit=50)
        logger.info("Fetched chats", user_id=user_id, count=len(chats))
        return {"chats": chats}
    except Exception as e:
        logger.error("Failed to fetch chats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch chats")


@router.post("/delete")
async def delete_chat(data: Dict[str, Any], chat_service: ChatService = Depends(get_chat_service)):
    """Delete a chat"""
    try:
        chat_id = data.get("chat_id")
        if not chat_id:
            raise HTTPException(status_code=400, detail="chat_id required")

        await chat_service.delete_chat(chat_id)
        logger.info("Chat deleted", chat_id=chat_id)
        return {"success": True}
    except ChatNotFoundError:
        raise HTTPException(status_code=404, detail="Chat not found")
    except Exception as e:
        logger.error("Failed to delete chat", error=str(e), chat_id=data.get("chat_id"))
        raise HTTPException(status_code=500, detail="Failed to delete chat")


@router.post("/history")
async def get_chat_history(data: Dict[str, Any], chat_service: ChatService = Depends(get_chat_service)):
    """Get full chat history"""
    try:
        chat_id = data.get("chat_id")
        if not chat_id:
            raise HTTPException(status_code=400, detail="chat_id required")

        chat = await chat_service.get_chat_history(chat_id, limit=100)
        logger.info("Chat history fetched", chat_id=chat_id, message_count=len(chat.get("messages", [])))
        return chat
    except ChatNotFoundError:
        raise HTTPException(status_code=404, detail="Chat not found")
    except Exception as e:
        logger.error("Failed to fetch chat history", error=str(e), chat_id=data.get("chat_id"))
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")

