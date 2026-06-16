from fastapi import APIRouter, HTTPException, Depends
from models.models import UserSignup, UserLogin, TokenResponse
from repositories.user_repository import UserRepository
from services.user_service import UserService
from database.db import users_collection
from utils.exceptions import AuthenticationError, UserNotFoundError
from utils.exceptions import Logger

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = Logger("auth_router")


def get_user_service() -> UserService:
    """Dependency injection for UserService"""
    user_repo = UserRepository(users_collection)
    return UserService(user_repo)


@router.post("/signup")
async def signup(user: UserSignup, user_service: UserService = Depends(get_user_service)):
    """Register a new user"""
    try:
        result = await user_service.signup(user.username, user.password)
        return result
    except AuthenticationError as e:
        logger.error("Signup failed", error=str(e), username=user.username)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Signup error", error=str(e), username=user.username)
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin, user_service: UserService = Depends(get_user_service)):
    """Authenticate user and return JWT token"""
    try:
        result = await user_service.login(user.username, user.password)
        return TokenResponse(access_token=result["access_token"], token_type=result["token_type"])
    except AuthenticationError as e:
        logger.error("Login failed", error=str(e), username=user.username)
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error("Login error", error=str(e), username=user.username)
        raise HTTPException(status_code=500, detail="Login failed")
