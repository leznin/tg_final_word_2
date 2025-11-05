"""
Admin user Pydantic schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles enum"""
    ADMIN = "admin"
    MANAGER = "manager"


class AdminUserLogin(BaseModel):
    """Schema for admin user login"""
    email: EmailStr
    password: str


class AdminUserBase(BaseModel):
    """Base admin user schema"""
    username: Optional[str] = None
    email: EmailStr
    is_active: bool = True
    role: UserRole = UserRole.ADMIN


class AdminUserCreate(AdminUserBase):
    """Schema for creating an admin user"""
    password: str


class AdminUserUpdate(BaseModel):
    """Schema for updating an admin user"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class AdminUserResponse(AdminUserBase):
    """Schema for admin user response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True