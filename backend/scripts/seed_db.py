import asyncio
import sys
import os

# Add backend directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.session import async_session
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def seed_admin():
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(select(User).filter(User.email == "admin@example.com"))
        user = result.scalars().first()
        
        if not user:
            print("Creating admin user...")
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@example.com",
                password_hash=hashed_password,
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("Admin user created successfully. Email: admin@example.com | Password: admin123")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(seed_admin())
