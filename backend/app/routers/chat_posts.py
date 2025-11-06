"""
Chat Posts API Router
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import os
from pathlib import Path
import mimetypes

from app.core.database import get_db
from app.services.chat_posts import ChatPostService
from app.schemas.chat_posts import (
    ChatPostCreate,
    ChatPostUpdate,
    ChatPostResponse,
    ChatPostListResponse,
    PinPostRequest,
    MediaUploadResponse
)
from app.dependencies.admin_auth import get_current_admin_user

router = APIRouter()


def get_chat_post_service(db: AsyncSession = Depends(get_db)):
    """Get chat post service with bot instance"""
    import app.main
    bot_instance = app.main.telegram_bot_instance
    
    if not bot_instance:
        raise HTTPException(status_code=500, detail="Telegram bot not initialized")
    
    return ChatPostService(db, bot_instance.bot)


@router.post("/", response_model=ChatPostResponse)
async def create_chat_post(
    post_data: ChatPostCreate,
    service: ChatPostService = Depends(get_chat_post_service),
    user_info: dict = Depends(get_current_admin_user)
):
    """Create and send a new post to a Telegram chat"""
    return await service.create_post(post_data, user_info["user_id"])


@router.get("/chat/{chat_id}", response_model=ChatPostListResponse)
async def get_chat_posts(
    chat_id: int,
    page: int = 1,
    page_size: int = 20,
    include_deleted: bool = False,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Get all posts for a specific chat"""
    posts, total = await service.get_chat_posts(chat_id, page, page_size, include_deleted)
    
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    return ChatPostListResponse(
        posts=posts,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{post_id}", response_model=ChatPostResponse)
async def get_chat_post(
    post_id: int,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Get a specific post by ID"""
    post = await service.get_post_by_id(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post


@router.put("/{post_id}", response_model=ChatPostResponse)
async def update_chat_post(
    post_id: int,
    post_data: ChatPostUpdate,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Update an existing post (edit message text)"""
    return await service.update_post(post_id, post_data)


@router.delete("/{post_id}")
async def delete_chat_post(
    post_id: int,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Delete a post"""
    success = await service.delete_post(post_id)
    
    if success:
        return {"message": "Post deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete post")


@router.post("/{post_id}/pin", response_model=ChatPostResponse)
async def pin_chat_post(
    post_id: int,
    pin_request: PinPostRequest,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Pin a post in the chat"""
    return await service.pin_post(post_id, pin_request.pin_duration_minutes)


@router.post("/{post_id}/unpin", response_model=ChatPostResponse)
async def unpin_chat_post(
    post_id: int,
    service: ChatPostService = Depends(get_chat_post_service),
    _: dict = Depends(get_current_admin_user)
):
    """Unpin a post from the chat"""
    return await service.unpin_post(post_id)


@router.post("/upload-media", response_model=MediaUploadResponse)
async def upload_media_file(
    file: UploadFile = File(...),
    _: dict = Depends(get_current_admin_user)
):
    """Upload a media file for use in chat posts"""
    try:
        # Validate file size (max 50MB)
        content = await file.read()
        file_size = len(content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")
        
        # Determine content type
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("static/chat_posts")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return URL (relative to static folder)
        file_url = f"/static/chat_posts/{unique_filename}"
        
        return MediaUploadResponse(
            url=file_url,
            filename=file.filename,
            content_type=content_type,
            size=file_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
