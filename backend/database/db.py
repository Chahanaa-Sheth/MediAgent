from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db: AsyncIOMotorDatabase = client["mediagent"]

users_collection = db["users"]
chat_collection = db["chats"]


async def initialize_database():
    """Initialize database with proper indexes and schema validation"""

    # Users collection indexes
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("created_at")
    await users_collection.create_index("is_active")

    # Chats collection indexes
    await chat_collection.create_index("chat_id", unique=True)
    await chat_collection.create_index("user_id")
    await chat_collection.create_index("created_at")
    await chat_collection.create_index("is_active")
    await chat_collection.create_index([("user_id", ASCENDING), ("created_at", -1)])

    # Compound index for efficient user chat queries
    await chat_collection.create_index([("user_id", ASCENDING), ("is_active", ASCENDING)])

    print("✓ Database indexes initialized")