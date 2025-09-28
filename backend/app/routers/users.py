"""
Users API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.users import UserCreate, UserResponse, UserWithChatsResponse
from app.services.users import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    user_service = UserService(db)
    return await user_service.create_user(user_data)


@router.get("/with-chats", response_model=List[UserWithChatsResponse])
async def get_users_with_chats(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all users with their chats information including linked channels and moderators"""
    user_service = UserService(db)
    return await user_service.get_users_with_chats(skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    user_service = UserService(db)
    return await user_service.get_user(user_id)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all users with pagination"""
    user_service = UserService(db)
    return await user_service.get_users(skip, limit)
