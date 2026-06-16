from typing import Dict, List, Any, Optional
from datetime import datetime
from repositories.base_repository import BaseRepository
from utils.exceptions import Logger, ChatNotFoundError


class ChatRepository(BaseRepository):
    """Repository for chat operations"""

    async def get_by_chat_id(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat by chat_id"""
        return await self.read({"chat_id": chat_id})

    async def get_user_chats(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all chats for a user"""
        return await self.read_many(
            {"user_id": user_id, "is_active": True},
            limit=limit
        )

    async def create_chat(self, chat_id: str, user_id: str, title: str = "New Chat") -> str:
        """Create a new chat"""
        chat_data = {
            "chat_id": chat_id,
            "user_id": user_id,
            "title": title,
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "metadata": {}
        }
        return await self.create(chat_data)

    async def add_message(self, chat_id: str, role: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Add a message to a chat"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        result = await self.collection.update_one(
            {"chat_id": chat_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0

    async def get_chat_history(self, chat_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
        """Get chat with full message history"""
        chat = await self.read({"chat_id": chat_id})
        if chat and limit:
            chat['messages'] = chat.get('messages', [])[-limit:]
        return chat

    async def update_title(self, chat_id: str, title: str) -> bool:
        """Update chat title"""
        return await self.update({"chat_id": chat_id}, {"title": title})

    async def deactivate_chat(self, chat_id: str) -> bool:
        """Deactivate a chat (soft delete)"""
        return await self.update({"chat_id": chat_id}, {"is_active": False})

    async def chat_exists(self, chat_id: str) -> bool:
        """Check if chat exists"""
        chat = await self.get_by_chat_id(chat_id)
        return chat is not None and chat.get("is_active", True)
