"""
Admin users service for authentication and user management
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
import secrets
import string

from app.models.admin_users import AdminUser, UserRole
from app.schemas.admin_users import AdminUserCreate, AdminUserUpdate


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

    def generate_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        # Define character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        symbols = '!@#$%^&*'
        all_chars = uppercase + lowercase + digits + symbols
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # Fill the rest with random characters
        password += [secrets.choice(all_chars) for _ in range(length - 4)]
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)

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

    async def get_all_admins(self, skip: int = 0, limit: int = 100) -> List[AdminUser]:
        """Get all admin users"""
        result = await self.db.execute(
            select(AdminUser)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_managers(self, skip: int = 0, limit: int = 100) -> List[AdminUser]:
        """Get all managers"""
        result = await self.db.execute(
            select(AdminUser)
            .where(AdminUser.role == UserRole.MANAGER.value)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

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
            is_active=admin_data.is_active,
            role=admin_data.role.value
        )
        
        self.db.add(admin)
        await self.db.commit()
        await self.db.refresh(admin)
        
        return admin

    async def update_admin(self, admin_id: int, admin_data: AdminUserUpdate) -> Optional[AdminUser]:
        """Update admin user"""
        admin = await self.get_admin_by_id(admin_id)
        if not admin:
            return None

        # Update fields if provided
        if admin_data.username is not None:
            admin.username = admin_data.username
        if admin_data.email is not None:
            admin.email = admin_data.email
        if admin_data.password is not None:
            admin.password_hash = self.hash_password(admin_data.password)
        if admin_data.is_active is not None:
            admin.is_active = admin_data.is_active
        if admin_data.role is not None:
            admin.role = admin_data.role.value

        await self.db.commit()
        await self.db.refresh(admin)
        
        return admin

    async def delete_admin(self, admin_id: int) -> bool:
        """Delete admin user"""
        admin = await self.get_admin_by_id(admin_id)
        if not admin:
            return False

        await self.db.delete(admin)
        await self.db.commit()
        
        return True

    async def update_admin_password(self, admin_id: int, new_password: str) -> Optional[AdminUser]:
        """Update admin user password"""
        admin = await self.get_admin_by_id(admin_id)
        if not admin:
            return None

        admin.password_hash = self.hash_password(new_password)
        
        await self.db.commit()
        await self.db.refresh(admin)
        
        return admin