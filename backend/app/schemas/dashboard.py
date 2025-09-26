"""
Dashboard Pydantic schemas
"""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Schema for dashboard statistics response"""
    total_chats: int
    total_channels: int
    total_moderators: int
    total_users: int
