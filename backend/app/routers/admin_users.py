"""
Admin users API router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.admin_users import AdminUserCreate, AdminUserUpdate, AdminUserResponse
from app.services.admin_users import AdminUsersService
from app.dependencies.admin_auth import require_admin_role, get_current_admin_user

router = APIRouter()


@router.get("/me", response_model=AdminUserResponse)
async def get_current_user(
    user_info: dict = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated user info"""
    admin_service = AdminUsersService(db)
    admin = await admin_service.get_admin_by_id(user_info["user_id"])
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    return admin


@router.get("/", response_model=List[AdminUserResponse])
async def get_all_admin_users(
    skip: int = 0,
    limit: int = 100,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Get all admin users and managers (admin only)"""
    admin_service = AdminUsersService(db)
    admins = await admin_service.get_all_admins(skip, limit)
    return admins


@router.post("/", response_model=AdminUserResponse)
async def create_admin_user(
    admin_data: AdminUserCreate,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Create a new admin user or manager (admin only)"""
    admin_service = AdminUsersService(db)
    
    # Check if email already exists
    existing = await admin_service.get_admin_by_email(admin_data.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    admin = await admin_service.create_admin(admin_data)
    return admin


@router.get("/{admin_id}", response_model=AdminUserResponse)
async def get_admin_user(
    admin_id: int,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Get admin user by ID (admin only)"""
    admin_service = AdminUsersService(db)
    admin = await admin_service.get_admin_by_id(admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    return admin


@router.put("/{admin_id}", response_model=AdminUserResponse)
async def update_admin_user(
    admin_id: int,
    admin_data: AdminUserUpdate,
    _: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Update admin user (admin only)"""
    admin_service = AdminUsersService(db)
    
    # Check if email is being changed and if it's already in use
    if admin_data.email:
        existing = await admin_service.get_admin_by_email(admin_data.email)
        if existing and existing.id != admin_id:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )
    
    admin = await admin_service.update_admin(admin_id, admin_data)
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    return admin


@router.delete("/{admin_id}")
async def delete_admin_user(
    admin_id: int,
    user_info: dict = Depends(require_admin_role),
    db: AsyncSession = Depends(get_db)
):
    """Delete admin user (admin only)"""
    # Prevent self-deletion
    if admin_id == user_info["user_id"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete your own account"
        )
    
    admin_service = AdminUsersService(db)
    success = await admin_service.delete_admin(admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}
