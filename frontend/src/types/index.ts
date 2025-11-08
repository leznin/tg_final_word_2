export interface ChatSubscription {
  id: number;
  subscription_type: 'month' | 'year';
  price_stars: number;
  currency: string;
  start_date: string;
  end_date: string;
  is_active: boolean;
  telegram_payment_charge_id?: string;
  created_at: string;
}

export interface ChatSubscriptionCreate {
  chat_id: number;
  subscription_type: 'month' | 'year';
  price_stars: number;
  currency: string;
  start_date: Date;
  end_date: Date;
  is_active?: boolean;
  telegram_payment_charge_id?: string;
}

export interface WelcomeMessageButton {
  text: string;
  url?: string;
  callback_data?: string;
}

export interface WelcomeMessageSettings {
  enabled: boolean;
  text?: string;
  media_type?: 'photo' | 'video' | null;
  media_url?: string;
  lifetime_minutes?: number;
  buttons?: WelcomeMessageButton[][];
}

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
  ai_content_check_enabled: boolean;
  delete_messages_enabled: boolean;
  linked_channel_info?: LinkedChannelWithAdmin;
  chat_moderators: ChannelModerator[];
  member_count?: number;
  description?: string;
  invite_link?: string;
  bot_permissions?: BotPermissions;
  last_info_update?: string;
  active_subscription?: ChatSubscription;
  welcome_message_enabled?: boolean;
  welcome_message_text?: string;
  welcome_message_media_type?: string;
  welcome_message_media_url?: string;
  welcome_message_lifetime_minutes?: number;
  welcome_message_buttons?: any;
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
  ai_content_check_enabled: boolean;
  notify_on_user_changes: boolean;
  max_edit_time_minutes: number;
  member_count?: number;
  description?: string;
  invite_link?: string;
  bot_permissions?: BotPermissions;
  last_info_update?: string;
  linked_channel?: LinkedChannelWithAdmin | null;
  active_subscription?: ChatSubscription;
  welcome_message_enabled?: boolean;
  welcome_message_text?: string;
  welcome_message_media_type?: string;
  welcome_message_media_url?: string;
  welcome_message_lifetime_minutes?: number;
  welcome_message_buttons?: any;
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
  first_name?: string;
  last_name?: string;
  username?: string;
  added_by_username?: string;
  added_by_first_name?: string;
  added_by_last_name?: string;
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
  user?: AdminUserInfo;
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager'
}

export interface AdminUserInfo {
  user_id: number;
  email: string;
  role: UserRole;
}

export interface AdminUser {
  id: number;
  username?: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AdminUserCreate {
  username?: string;
  email: string;
  password: string;
  role: UserRole;
  is_active?: boolean;
}

export interface AdminUserUpdate {
  username?: string;
  email?: string;
  password?: string;
  role?: UserRole;
  is_active?: boolean;
}

export interface ManagerChatAccess {
  id: number;
  admin_user_id: number;
  chat_id: number;
  created_at: string;
  updated_at: string;
}

export interface ManagerChatInfo {
  chat_id: number;
  telegram_chat_id: number;
  chat_title?: string;
  chat_type: string;
}

export interface ManagerChatAccessBulk {
  admin_user_id: number;
  chat_ids: number[];
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

export interface User {
  id: number;
  telegram_id?: number;
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  language_code?: string;
  is_premium: boolean;
  is_bot: boolean;
  can_send_messages: boolean;
  blocked_at?: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export interface BotPermissions {
  can_send_messages: boolean;
  can_send_audios: boolean;
  can_send_documents: boolean;
  can_send_photos: boolean;
  can_send_videos: boolean;
  can_send_video_notes: boolean;
  can_send_voice_notes: boolean;
  can_send_polls: boolean;
  can_send_other_messages: boolean;
  can_add_web_page_previews: boolean;
  can_change_info: boolean;
  can_invite_users: boolean;
  can_pin_messages: boolean;
  can_manage_topics: boolean;
  can_delete_messages: boolean;
  can_manage_video_chats: boolean;
  can_restrict_members: boolean;
  can_promote_members: boolean;
  can_post_messages?: boolean;
  can_edit_messages?: boolean;
  is_anonymous: boolean;
  custom_title?: string;
}

export interface ChatAdministrator {
  user: {
    id: number;
    is_bot: boolean;
    first_name?: string;
    last_name?: string;
    username?: string;
    language_code?: string;
  };
  status: string;
  can_be_edited?: boolean;
  is_anonymous?: boolean;
  can_manage_chat?: boolean;
  can_delete_messages?: boolean;
  can_manage_video_chats?: boolean;
  can_restrict_members?: boolean;
  can_promote_members?: boolean;
  can_change_info?: boolean;
  can_invite_users?: boolean;
  can_post_messages?: boolean;
  can_edit_messages?: boolean;
  can_pin_messages?: boolean;
  can_manage_topics?: boolean;
  custom_title?: string;
}

export interface ChatInfoResponse {
  telegram_chat_id: number;
  chat_type: string;
  title?: string;
  username?: string;
  description?: string;
  invite_link?: string;
  member_count?: number;
  bot_permissions?: BotPermissions;
  administrators: ChatAdministrator[];
  permissions?: any;
  slow_mode_delay?: number;
  bio?: string;
  has_private_forwards?: boolean;
  has_protected_content?: boolean;
  sticker_set_name?: string;
  can_set_sticker_set?: boolean;
  linked_chat_id?: number;
  location?: any;
  join_to_send_messages?: boolean;
  join_by_request?: boolean;
  has_hidden_members?: boolean;
  has_aggressive_anti_spam_enabled?: boolean;
  emoji_status_custom_emoji_id?: string;
  emoji_status_expiration_date?: number;
  available_reactions?: string[];
  accent_color_id?: number;
  background_custom_emoji_id?: string;
  profile_accent_color_id?: number;
  profile_background_custom_emoji_id?: string;
  has_visible_history?: boolean;
  unrestrict_boost_count?: number;
  custom_emoji_sticker_set_name?: string;
  business_intro?: any;
  business_location?: any;
  business_opening_hours?: any;
  personal_chat?: any;
  birthdate?: any;
}

export interface BulkChatInfoResponse {
  chats_info: ChatInfoResponse[];
  total_chats: number;
  successful_requests: number;
  failed_requests: number;
  errors: Array<{
    chat_id?: number;
    error: string;
  }>;
}

export interface UserWithChats extends User {
  chats: Chat[];
}

export interface TelegramUserHistory {
  id: number;
  telegram_user_id: number;
  field_name: string;
  old_value?: string;
  new_value?: string;
  changed_at: string;
}

export interface ChatMemberWithHistory {
  id: number;
  chat_id: number;
  telegram_user_id: number;
  is_bot: boolean;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  added_to_attachment_menu?: boolean;
  can_join_groups?: boolean;
  can_read_all_group_messages?: boolean;
  supports_inline_queries?: boolean;
  can_connect_to_business?: boolean;
  has_main_web_app?: boolean;
  joined_at?: string;
  created_at: string;
  updated_at: string;
  user_groups: Array<{
    title: string;
    telegram_chat_id: number;
    chat_type: string;
  }>;
  history: TelegramUserHistory[];
}

export interface ChatMembersResponse {
  members: ChatMemberWithHistory[];
  total: number;
}

export interface OpenRouterModel {
  id: string;
  name: string;
  description?: string;
  pricing?: Record<string, any>;
  context_length?: number;
  supports_function_calling?: boolean;
  supports_vision?: boolean;
}

export interface OpenRouterBalance {
  credits: number;
  total_credits: number;
  total_usage: number;
  currency: string;
}

export interface OpenRouterSettings {
  id: number;
  api_key: string;
  selected_model?: string;
  balance?: number;
  prompt?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OpenRouterSettingsCreate {
  api_key: string;
  selected_model?: string;
  prompt?: string;
  is_active?: boolean;
}

export interface OpenRouterSettingsUpdate {
  api_key?: string;
  selected_model?: string;
  balance?: number;
  prompt?: string;
  is_active?: boolean;
}

export interface OpenRouterModelsResponse {
  models: OpenRouterModel[];
}

export interface OpenRouterBalanceResponse {
  balance: OpenRouterBalance;
  last_updated: string;
}

export interface InlineKeyboardButton {
  text: string;
  url?: string;
  callback_data?: string;
}

export interface InlineKeyboardRow {
  buttons: InlineKeyboardButton[];
}

export interface InlineKeyboardMarkup {
  inline_keyboard: InlineKeyboardRow[];
}

export interface MediaFile {
  type: string; // 'photo', 'video', 'document'
  url: string; // URL to the file or file_id
  filename?: string;
  caption?: string;
}

export interface BroadcastMessageRequest {
  message: string;
  original_message?: string;
  media?: MediaFile;
  reply_markup?: InlineKeyboardMarkup;
}

export interface BroadcastResult {
  total_users: number;
  sent_successfully: number;
  blocked_users: number;
  failed_sends: number;
  duration_seconds: number;
  started_at: string;
  completed_at: string;
}

export interface BroadcastStatus {
  is_running: boolean;
  current_progress: number;
  total_users: number;
  sent_successfully: number;
  blocked_users: number;
  failed_sends: number;
  estimated_time_remaining?: number;
  started_at?: string;
}

export interface BroadcastUsersCount {
  count: number;
  description: string;
}

// Chat Posts
export interface MediaUpload {
  type: string; // 'photo', 'video', 'document'
  url?: string;
  file_id?: string;
  filename?: string;
}

export interface ChatPostCreate {
  chat_id: number;
  content_text?: string;
  media?: MediaUpload;
  scheduled_send_at?: string;  // ISO datetime string
  send_immediately?: boolean;
  pin_message?: boolean;
  pin_duration_minutes?: number;
  delete_after_minutes?: number;
  reply_markup?: InlineKeyboardMarkup;
}

export interface ChatPostUpdate {
  content_text?: string;
  scheduled_send_at?: string;  // ISO datetime string (for unsent posts)
  pin_message?: boolean;
  pin_duration_minutes?: number;
  delete_after_minutes?: number;
  reply_markup?: InlineKeyboardMarkup;
}

export interface ChatPost {
  id: number;
  chat_id: number;
  telegram_message_id?: number;
  scheduled_send_at?: string;
  is_sent: boolean;
  sent_at?: string;
  content_text?: string;
  media_type?: string;
  media_file_id?: string;
  media_url?: string;
  media_filename?: string;
  is_pinned: boolean;
  pin_duration_minutes?: number;
  scheduled_unpin_at?: string;
  delete_after_minutes?: number;
  scheduled_delete_at?: string;
  reply_markup?: InlineKeyboardMarkup | string;  // Can be object or JSON string
  created_by_user_id: number;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChatPostListResponse {
  posts: ChatPost[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PinPostRequest {
  pin_duration_minutes?: number;
}

export interface MediaUploadResponse {
  url: string;
  filename: string;
  content_type: string;
  size: number;
}