# backend/db.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "campus_admin")

client = AsyncIOMotorClient(MONGODB_URI)
db = client[MONGODB_DB]