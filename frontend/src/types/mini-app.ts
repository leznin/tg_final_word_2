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

// Telegram Web App types
declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name?: string
            last_name?: string
            username?: string
            language_code?: string
            is_premium?: boolean
            is_bot?: boolean
          }
          chat?: any
          query_id?: string
        }
        ready(): void
        close(): void
        expand(): void
        MainButton: {
          text: string
          show(): void
          hide(): void
          onClick(callback: () => void): void
          offClick(callback: () => void): void
        }
        BackButton: {
          show(): void
          hide(): void
          onClick(callback: () => void): void
          offClick(callback: () => void): void
        }
        HapticFeedback: {
          impactOccurred(style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft'): void
          notificationOccurred(type: 'error' | 'success' | 'warning'): void
          selectionChanged(): void
        }
        colorScheme: 'light' | 'dark'
        themeParams: {
          bg_color?: string
          text_color?: string
          hint_color?: string
          link_color?: string
          button_color?: string
          button_text_color?: string
        }
      }
    }
  }
}
