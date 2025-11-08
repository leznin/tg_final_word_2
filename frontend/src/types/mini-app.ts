export interface TelegramUser {
  id: number
  telegram_user_id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  is_bot: boolean
  account_creation_date?: string
  created_at: string
  updated_at: string
}

export interface TelegramUserVerifyRequest {
  init_data: string  // Telegram Web App initData for verification
}

export interface TelegramUserVerifyResponse {
  verified: boolean
  telegram_user_id: number
  message: string
  session_token?: string  // Session token for maintaining user session
  user_data?: {
    id: number
    username?: string
    first_name?: string
    last_name?: string
  }
}

export interface UserSearchRequest {
  query: string
  limit?: number
  offset?: number
  telegram_user_id: number  // User performing the search
}

export interface UserHistoryEntry {
  id: number
  field_name: string
  old_value?: string | null
  new_value?: string | null
  changed_at: string
}

export interface UserSearchResult {
  telegram_user_id: number | string  // Can be number or masked string
  real_telegram_user_id?: number | null  // Real ID for masked accounts
  username?: string | null
  first_name?: string | null
  last_name?: string | null
  language_code?: string | null
  is_premium: boolean
  is_bot: boolean
  account_creation_date?: string | null
  created_at: string
  updated_at: string
  history: UserHistoryEntry[]
}

export interface UserSearchResponse {
  results: UserSearchResult[]
  total: number
  limit: number
  offset: number
}

export interface SearchLimitResponse {
  total_searches_today: number
  max_searches_per_day: number
  remaining_searches: number
  reset_time: string  // ISO date string
}
