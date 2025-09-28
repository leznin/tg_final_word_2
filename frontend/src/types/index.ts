export interface Chat {
  id: number;
  telegram_chat_id: number;
  chat_type: 'group' | 'supergroup' | 'channel';
  title?: string;
  username?: string;
  added_by_user_id: number;
  is_active: boolean;
  added_at: string;
  created_at: string;
  updated_at: string;
  linked_channel_id?: number;
  message_edit_timeout_minutes?: number;
  delete_messages_enabled?: boolean;
  linked_channel_info?: LinkedChannelWithAdmin;
  chat_moderators: ChannelModerator[];
}

export interface ChatDetail {
  id: number;
  chat_id: number;
  chat_title: string;
  chat_type: string;
  admin_user_id: number;
  added_date: string;
  is_active: boolean;
  delete_messages_enabled: boolean;
  max_edit_time_minutes: number;
}

export interface Moderator {
  id: number;
  chat_id: number;
  chat_title: string;
  moderator_user_id: number;
  moderator_username?: string;
  moderator_name: string;
  added_by_user_id: number;
  added_date: string;
}

export interface Channel {
  id: number;
  channel_id: number;
  admin_user_id: number;
  created_date: string;
}

export interface LinkedChannel {
  id: number;
  telegram_chat_id: number;
  title?: string;
  username?: string;
}

export interface ChannelModerator {
  id: number;
  moderator_user_id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  added_date?: string;
}

export interface LinkedChannelWithAdmin {
  id: number;
  telegram_chat_id: number;
  title?: string;
  username?: string;
  admin_user_id: number;
  admin_username?: string;
  admin_name?: string;
}

export interface DashboardStats {
  total_chats: number;
  total_channels: number;
  total_moderators: number;
  total_users: number;
}

export interface AuthResponse {
  success: boolean;
  message: string;
}

export interface AuthCheckResponse {
  authenticated: boolean;
}

export interface LinkChannelRequest {
  channel_id: number;
}

export interface LinkChannelResponse {
  message: string;
}

export interface ChatModerator {
  id: number;
  chat_id: number;
  moderator_user_id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
  added_by_user_id: number;
  created_at: string;
  updated_at: string;
}

export interface AddModeratorRequest {
  moderator_user_id: number;
  first_name?: string;
  last_name?: string;
  username?: string;
}

export interface ModeratorResponse {
  message: string;
}

export interface ChatDetailResponse {
  chat: ChatDetail;
  moderators: Moderator[];
  channels: Channel[];
}