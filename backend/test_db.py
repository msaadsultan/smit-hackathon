import asyncio
import sys, os

# add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import db

async def test():
    try:
        result = await db.command("ping")
        print("MongoDB connection success:", result)
    except Exception as e:
        print("MongoDB connection error:", e)

asyncio.run(test())
