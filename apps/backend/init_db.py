"""Database initialization script."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from api.config import settings
from api.db.base import Base
from api.models import User
from api.core import get_password_hash
from api.db.session import AsyncSessionLocal


async def init_db():
    """Initialize database tables."""
    print("Creating database tables...")
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")
    await engine.dispose()


async def create_admin_user():
    """Create admin user."""
    print("\nCreating admin user...")
    
    async with AsyncSessionLocal() as db:
        # Check if admin user exists
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email="admin@safesurface.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"  Username: admin")
        print(f"  Password: admin123")
        print(f"  Email: admin@safesurface.com")


async def main():
    """Main initialization function."""
    print("=" * 60)
    print("SafeSurface Database Initialization")
    print("=" * 60)
    
    await init_db()
    await create_admin_user()
    
    print("\n" + "=" * 60)
    print("Database initialization completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
