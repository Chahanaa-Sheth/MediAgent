from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from repositories.user_repository import UserRepository
from utils.exceptions import Logger, AuthenticationError, UserNotFoundError
from auth.auth_handler import hash_password, verify_password
from auth.jwt_handler import create_access_token


class UserService:
    """Service for user authentication and management"""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.logger = Logger("UserService")

    async def signup(self, username: str, password: str) -> Dict[str, Any]:
        """Register a new user"""
        # Check if user exists
        if await self.user_repo.user_exists(username):
            raise AuthenticationError("User already exists")

        # Hash password
        password_hash = hash_password(password)

        # Create user
        user_id = await self.user_repo.create_user(username, password_hash)
        self.logger.info("User created", username=username, user_id=user_id)

        return {"user_id": user_id, "username": username, "message": "User created successfully"}

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return JWT token"""
        # Get user
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise AuthenticationError("User not found")

        # Verify password
        if not verify_password(password, user["password"]):
            raise AuthenticationError("Wrong password")

        # Create token
        token = create_access_token({"sub": username})
        self.logger.info("User logged in", username=username)

        return {
            "access_token": token,
            "token_type": "bearer",
            "username": username
        }

    async def get_user(self, username: str) -> Dict[str, Any]:
        """Get user information"""
        user = await self.user_repo.get_by_username(username)
        if not user:
            raise UserNotFoundError(f"User {username} not found")

        # Don't return password hash
        user.pop("password", None)
        return user

    async def user_exists(self, username: str) -> bool:
        """Check if user exists"""
        return await self.user_repo.user_exists(username)
