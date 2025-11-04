#!/usr/bin/env python3
"""
Script to apply migration and create default admin user
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from passlib.context import CryptContext

# Import our models and config
from app.core.config import settings
from app.core.database import Base
from app.models.admin_users import AdminUser
from app.services.admin_users import AdminUsersService
from app.schemas.admin_users import AdminUserCreate


async def create_tables_and_default_user():
    """Create tables and default admin user"""
    
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create session factory
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Tables created successfully")
        
        # Check if admin user already exists
        async with async_session() as session:
            admin_service = AdminUsersService(session)
            existing_admin = await admin_service.get_admin_by_email("Maksimleznin30@gmail.com")
            
            if existing_admin:
                print("✅ Default admin user already exists")
                print(f"   Email: {existing_admin.email}")
                print(f"   Active: {existing_admin.is_active}")
            else:
                # Create default admin user
                # Truncate password to 72 bytes for bcrypt compatibility
                original_password = "696578As!@#$"
                truncated_password = original_password[:72]
                
                admin_data = AdminUserCreate(
                    username=None,
                    email="Maksimleznin30@gmail.com",
                    password=truncated_password,
                    is_active=True
                )
                
                new_admin = await admin_service.create_admin(admin_data)
                print("✅ Default admin user created successfully")
                print(f"   Email: {new_admin.email}")
                print(f"   ID: {new_admin.id}")
                print(f"   Active: {new_admin.is_active}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    print("🚀 Starting migration and admin user creation...")
    success = asyncio.run(create_tables_and_default_user())
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📝 Login credentials:")
        print("   Email: Maksimleznin30@gmail.com")
        print("   Password: 696578As!@#$")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)