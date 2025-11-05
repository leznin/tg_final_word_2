"""
User verification Pydantic schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserVerificationRequest(BaseModel):
    """Schema for single user verification request"""
    telegram_user_id: int = Field(..., description="Telegram user ID to verify")
    chat_id: int = Field(..., description="Chat ID where to check the user")
    auto_update: bool = Field(default=True, description="Automatically update user data if changes detected")


class UserChangeDetail(BaseModel):
    """Schema for tracking a single field change"""
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class UserVerificationResult(BaseModel):
    """Schema for user verification result"""
    telegram_user_id: int
    chat_id: int
    chat_title: Optional[str] = None
    is_updated: bool = Field(description="Whether the user data was updated")
    has_changes: bool = Field(description="Whether any changes were detected")
    changes: Dict[str, UserChangeDetail] = Field(default_factory=dict, description="Dictionary of field changes")
    current_status: Optional[str] = Field(None, description="User status in chat (member, administrator, creator, left, kicked)")
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "chat_id": -1001234567890,
                "chat_title": "My Chat",
                "is_updated": True,
                "has_changes": True,
                "changes": {
                    "first_name": {
                        "old_value": "John",
                        "new_value": "Johnny"
                    },
                    "username": {
                        "old_value": "john_old",
                        "new_value": "john_new"
                    }
                },
                "current_status": "member",
                "checked_at": "2025-11-05T12:00:00",
                "error": None
            }
        }


class BulkVerificationRequest(BaseModel):
    """Schema for bulk user verification request"""
    chat_id: Optional[int] = Field(None, description="Chat ID to filter users. If not provided, checks all active users")
    telegram_user_ids: Optional[List[int]] = Field(None, description="Specific user IDs to check. If not provided, checks all active users in chat(s)")
    auto_update: bool = Field(default=True, description="Automatically update user data if changes detected")
    delay_between_requests: float = Field(default=0.5, description="Delay in seconds between API requests to avoid rate limiting")


class BulkVerificationResponse(BaseModel):
    """Schema for bulk verification response"""
    total_checked: int = Field(description="Total number of users checked")
    total_updated: int = Field(description="Number of users with updated data")
    total_errors: int = Field(description="Number of errors encountered")
    total_with_changes: int = Field(description="Number of users with detected changes")
    results: List[UserVerificationResult] = Field(default_factory=list)
    started_at: datetime
    completed_at: datetime
    duration_seconds: float = Field(description="Total duration of the verification process")


class ActiveUserInfo(BaseModel):
    """Schema for active user information"""
    telegram_user_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_bot: Optional[bool] = None
    active_chats: List[Dict[str, Any]] = Field(default_factory=list, description="List of chats where user is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "telegram_user_id": 123456789,
                "first_name": "John",
                "last_name": "Doe",
                "username": "johndoe",
                "is_bot": False,
                "active_chats": [
                    {
                        "chat_id": 1,
                        "telegram_chat_id": -1001234567890,
                        "title": "My Chat",
                        "chat_type": "supergroup"
                    }
                ]
            }
        }


class ActiveUsersListResponse(BaseModel):
    """Schema for list of active users"""
    users: List[ActiveUserInfo] = Field(default_factory=list)
    total: int = Field(description="Total number of active users")
    skip: int
    limit: int
