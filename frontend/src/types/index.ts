export interface Chat {
  id: number;
  chat_id: number;
  chat_title: string;
  chat_type: 'group' | 'supergroup' | 'channel';
  admin_user_id: number;
  added_date: string;
  delete_messages_enabled: boolean;
  max_edit_time_minutes: number;
  channel_count: number;
  linked_channel_id?: number;
  linked_channel?: LinkedChannel;
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

export interface ChatDetailResponse {
  chat: ChatDetail;
  moderators: Moderator[];
  channels: Channel[];
}