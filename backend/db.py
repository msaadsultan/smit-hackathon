from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from dotenv import load_dotenv

from .models import User, Student, ActivityLog, Conversation

# Load environment variables
load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "campus_ai_agent")

async def init_mongodb():
    """Initialize MongoDB connection and Beanie ODM"""
    # Create motor client
    client = AsyncIOMotorClient(MONGODB_URL)
    
    # Initialize beanie with the document models
    await init_beanie(
        database=client[DATABASE_NAME],
        document_models=[
            User,
            Student,
            ActivityLog,
            Conversation
        ]
    )
    
    return client

async def close_mongodb(client: AsyncIOMotorClient):
    """Close MongoDB connection"""
    client.close()

# Database dependency
async def get_db():
    """Get database client"""
    client = await init_mongodb()
    try:
        yield client
    finally:
        await close_mongodb(client)
