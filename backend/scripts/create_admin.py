from backend.auth.security import get_password_hash
from backend.auth.models import UserCreate, UserRole
from backend.db import init_mongodb
import asyncio
import os
from dotenv import load_dotenv

async def create_admin_user():
    # Load environment variables
    load_dotenv()
    
    # Get admin credentials from environment
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Initialize MongoDB
    client = await init_mongodb()
    
    # Create admin user if it doesn't exist
    from backend.auth.models import User
    existing_admin = await User.find_one({"email": admin_email})
    
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )
        await admin_user.insert()
        print(f"Admin user created successfully with email: {admin_email}")
    else:
        print(f"Admin user already exists with email: {admin_email}")

if __name__ == "__main__":
    asyncio.run(create_admin_user())