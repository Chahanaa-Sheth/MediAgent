from typing import Dict, List, Any, Optional
from datetime import datetime
from repositories.base_repository import BaseRepository
from utils.exceptions import Logger, UserNotFoundError


class UserRepository(BaseRepository):
    """Repository for user operations"""

    async def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return await self.read({"username": username})

    async def create_user(self, username: str, password_hash: str) -> str:
        """Create a new user"""
        user_data = {
            "username": username,
            "password": password_hash,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        return await self.create(user_data)

    async def update_password(self, username: str, new_password_hash: str) -> bool:
        """Update user password"""
        return await self.update(
            {"username": username},
            {"password": new_password_hash}
        )

    async def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        user = await self.get_by_username(username)
        return user is not None

    async def deactivate_user(self, username: str) -> bool:
        """Deactivate a user"""
        return await self.update(
            {"username": username},
            {"is_active": False}
        )
