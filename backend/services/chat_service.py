from typing import Dict, List, Any, Optional
from uuid import uuid4
from datetime import datetime
from repositories.chat_repository import ChatRepository
from utils.exceptions import Logger, ChatNotFoundError
from models.models import Chat, Message


class ChatService:
    """Service for chat management"""

    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
        self.logger = Logger("ChatService")

    async def create_chat(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """Create a new chat"""
        chat_id = str(uuid4())
        chat_repo_id = await self.chat_repo.create_chat(chat_id, user_id, title)
        self.logger.info("Chat created", chat_id=chat_id, user_id=user_id)

        return {
            "chat_id": chat_id,
            "title": title,
            "messages": [],
            "created_at": datetime.utcnow().isoformat()
        }

    async def get_user_chats(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all chats for a user"""
        chats = await self.chat_repo.get_user_chats(user_id, limit=limit)
        self.logger.info("Fetched user chats", user_id=user_id, count=len(chats))
        return chats

    async def get_chat_history(self, chat_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get chat with message history"""
        chat = await self.chat_repo.get_chat_history(chat_id, limit=limit)
        if not chat:
            raise ChatNotFoundError(f"Chat {chat_id} not found")
        return chat

    async def add_message(self, chat_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a message to a chat"""
        success = await self.chat_repo.add_message(chat_id, role, content, metadata)
        if not success:
            raise ChatNotFoundError(f"Chat {chat_id} not found")

        self.logger.info("Message added", chat_id=chat_id, role=role)
        return True

    async def update_title(self, chat_id: str, title: str) -> bool:
        """Update chat title"""
        success = await self.chat_repo.update_title(chat_id, title)
        if not success:
            raise ChatNotFoundError(f"Chat {chat_id} not found")

        self.logger.info("Chat title updated", chat_id=chat_id, title=title)
        return True

    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat"""
        success = await self.chat_repo.deactivate_chat(chat_id)
        if not success:
            raise ChatNotFoundError(f"Chat {chat_id} not found")

        self.logger.info("Chat deleted", chat_id=chat_id)
        return True

    async def chat_exists(self, chat_id: str) -> bool:
        """Check if chat exists and is active"""
        return await self.chat_repo.chat_exists(chat_id)

    async def auto_title_chat(self, chat_id: str, first_message: str) -> bool:
        """Auto-title a chat based on first message"""
        title = first_message[:40].strip()
        return await self.update_title(chat_id, title)
