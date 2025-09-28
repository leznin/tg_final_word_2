"""
Chat information schemas from Telegram API
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatPermissions(BaseModel):
    """Telegram Chat Permissions schema"""
    can_send_messages: Optional[bool] = None
    can_send_audios: Optional[bool] = None
    can_send_documents: Optional[bool] = None
    can_send_photos: Optional[bool] = None
    can_send_videos: Optional[bool] = None
    can_send_video_notes: Optional[bool] = None
    can_send_voice_notes: Optional[bool] = None
    can_send_polls: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_manage_topics: Optional[bool] = None


class ChatAdministrator(BaseModel):
    """Telegram Chat Administrator schema"""
    user: Dict[str, Any]  # Telegram User object
    status: str  # "administrator" or "creator"
    can_be_edited: Optional[bool] = None
    is_anonymous: Optional[bool] = None
    can_manage_chat: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_manage_video_chats: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_manage_topics: Optional[bool] = None
    custom_title: Optional[str] = None


class BotPermissions(BaseModel):
    """Bot permissions in a chat"""
    can_send_messages: bool = False
    can_send_audios: bool = False
    can_send_documents: bool = False
    can_send_photos: bool = False
    can_send_videos: bool = False
    can_send_video_notes: bool = False
    can_send_voice_notes: bool = False
    can_send_polls: bool = False
    can_send_other_messages: bool = False
    can_add_web_page_previews: bool = False
    can_change_info: bool = False
    can_invite_users: bool = False
    can_pin_messages: bool = False
    can_manage_topics: bool = False
    can_delete_messages: bool = False
    can_manage_video_chats: bool = False
    can_restrict_members: bool = False
    can_promote_members: bool = False
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    is_anonymous: bool = False
    custom_title: Optional[str] = None


class ChatInfoResponse(BaseModel):
    """Response schema for chat information from Telegram API"""
    telegram_chat_id: int
    chat_type: str
    title: Optional[str] = None
    username: Optional[str] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    member_count: Optional[int] = None
    bot_permissions: Optional[BotPermissions] = None
    administrators: List[ChatAdministrator] = []
    permissions: Optional[ChatPermissions] = None
    slow_mode_delay: Optional[int] = None
    bio: Optional[str] = None
    has_private_forwards: Optional[bool] = None
    has_protected_content: Optional[bool] = None
    sticker_set_name: Optional[str] = None
    can_set_sticker_set: Optional[bool] = None
    linked_chat_id: Optional[int] = None
    location: Optional[Dict[str, Any]] = None
    join_to_send_messages: Optional[bool] = None
    join_by_request: Optional[bool] = None
    has_hidden_members: Optional[bool] = None
    has_aggressive_anti_spam_enabled: Optional[bool] = None
    emoji_status_custom_emoji_id: Optional[str] = None
    emoji_status_expiration_date: Optional[int] = None
    available_reactions: Optional[List[str]] = None
    accent_color_id: Optional[int] = None
    background_custom_emoji_id: Optional[str] = None
    profile_accent_color_id: Optional[int] = None
    profile_background_custom_emoji_id: Optional[str] = None
    has_visible_history: Optional[bool] = None
    unrestrict_boost_count: Optional[int] = None
    custom_emoji_sticker_set_name: Optional[str] = None
    business_intro: Optional[Dict[str, Any]] = None
    business_location: Optional[Dict[str, Any]] = None
    business_opening_hours: Optional[Dict[str, Any]] = None
    personal_chat: Optional[Dict[str, Any]] = None
    birthdate: Optional[Dict[str, Any]] = None


class ChatInfoUpdateRequest(BaseModel):
    """Request schema for updating chat information in database"""
    telegram_chat_id: int
    member_count: Optional[int] = None
    bot_permissions: Optional[BotPermissions] = None
    last_info_update: datetime


class BulkChatInfoResponse(BaseModel):
    """Response schema for bulk chat information request"""
    chats_info: List[ChatInfoResponse]
    total_chats: int
    successful_requests: int
    failed_requests: int
    errors: List[Dict[str, Any]] = []
