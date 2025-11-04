"""
Admin users service for authentication and user management
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.models.admin_users import AdminUser
from app.schemas.admin_users import AdminUserCreate


class AdminUsersService:
    """Service for managing admin users"""

    def __init__(self, db: AsyncSession):
        self.db = db
        # Configure password hashing with bcrypt
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def get_admin_by_email(self, email: str) -> Optional[AdminUser]:
        """Get admin user by email"""
        result = await self.db.execute(
            select(AdminUser).where(AdminUser.email == email)
        )
        return result.scalar_one_or_none()

    async def get_admin_by_id(self, admin_id: int) -> Optional[AdminUser]:
        """Get admin user by ID"""
        result = await self.db.execute(
            select(AdminUser).where(AdminUser.id == admin_id)
        )
        return result.scalar_one_or_none()

    async def authenticate_admin(self, email: str, password: str) -> Optional[AdminUser]:
        """Authenticate admin user with email and password"""
        admin = await self.get_admin_by_email(email)
        if not admin:
            return None
        
        if not admin.is_active:
            return None
            
        if not self.verify_password(password, admin.password_hash):
            return None
            
        return admin

    async def create_admin(self, admin_data: AdminUserCreate) -> AdminUser:
        """Create a new admin user"""
        # Hash the password
        hashed_password = self.hash_password(admin_data.password)
        
        # Create admin user
        admin = AdminUser(
            username=admin_data.username,
            email=admin_data.email,
            password_hash=hashed_password,
            is_active=admin_data.is_active
        )
        
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)
        
        return admin