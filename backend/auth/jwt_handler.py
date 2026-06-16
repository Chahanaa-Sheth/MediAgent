from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "mediagent_super_secret_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict):
    """Create a JWT access token"""
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str):
    """Decode a JWT token"""
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None


def get_username_from_token(token: str) -> str:
    """Extract username from token, return anonymous user ID if invalid"""
    if not token:
        return f"anonymous-{str(uuid4())[:8]}"

    payload = decode_token(token)
    if payload:
        return payload.get("sub")

    return f"anonymous-{str(uuid4())[:8]}"
