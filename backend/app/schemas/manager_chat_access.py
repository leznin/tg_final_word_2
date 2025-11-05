"""
Manager chat access Pydantic schemas
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ManagerChatAccessBase(BaseModel):
    """Base manager chat access schema"""
    admin_user_id: int
    chat_id: int


class ManagerChatAccessCreate(ManagerChatAccessBase):
    """Schema for creating a manager chat access"""
    pass


class ManagerChatAccessBulkCreate(BaseModel):
    """Schema for bulk creating manager chat accesses"""
    admin_user_id: int
    chat_ids: List[int]


class ManagerChatAccessResponse(ManagerChatAccessBase):
    """Schema for manager chat access response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ManagerChatInfo(BaseModel):
    """Schema for manager's chat info"""
    chat_id: int
    telegram_chat_id: int
    chat_title: Optional[str] = None
    chat_type: str


class ManagerChatsResponse(BaseModel):
    """Schema for manager's chats list response"""
    admin_user_id: int
    chats: List[ManagerChatInfo]
