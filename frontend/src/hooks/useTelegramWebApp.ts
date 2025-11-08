import { useEffect, useState } from 'react'
import type { TelegramWebApp } from '../types/telegram-web-app'

export interface TelegramUserData {
  id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  is_bot?: boolean
  photo_url?: string
}

export interface TelegramThemeParams {
  bg_color?: string
  text_color?: string
  hint_color?: string
  link_color?: string
  button_color?: string
  button_text_color?: string
  secondary_bg_color?: string
  header_bg_color?: string
  accent_text_color?: string
  section_bg_color?: string
  section_header_text_color?: string
  subtitle_text_color?: string
  destructive_text_color?: string
}

export interface TelegramThemeData {
  colorScheme: 'light' | 'dark'
  themeParams: TelegramThemeParams
}

export const useTelegramWebApp = () => {
  const [isReady, setIsReady] = useState(false)
  const [user, setUser] = useState<TelegramUserData | null>(null)
  const [initData, setInitData] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [theme, setTheme] = useState<TelegramThemeData>({
    colorScheme: 'light',
    themeParams: {}
  })

  const updateTheme = (webApp: TelegramWebApp) => {
    const newTheme: TelegramThemeData = {
      colorScheme: webApp.colorScheme || 'light',
      themeParams: webApp.themeParams || {}
    }
    setTheme(newTheme)
  }

  const fetchUserPhoto = async (userId: number): Promise<string | null> => {
    try {
      const response = await fetch(`/api/mini-app/user-photo/${userId}`)
      
      if (response.ok) {
        // The endpoint returns a redirect, so we get the final URL
        return response.url
      }
      return null
    } catch (error) {
      console.error('Error fetching user photo:', error)
      return null
    }
  }

  useEffect(() => {
    const initializeTelegramWebApp = () => {
      try {
        console.log('[TelegramWebApp] Starting initialization...')
        console.log('[TelegramWebApp] window.Telegram:', window.Telegram)
        
        // Check if Telegram Web App is available
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
          const webApp: TelegramWebApp = window.Telegram.WebApp
          console.log('[TelegramWebApp] WebApp found:', webApp)
          console.log('[TelegramWebApp] initData:', webApp.initData)
          console.log('[TelegramWebApp] initDataUnsafe:', webApp.initDataUnsafe)

          // Initialize the Web App
          webApp.ready()
          console.log('[TelegramWebApp] Called ready()')

          // Expand the Web App to full height
          webApp.expand()
          console.log('[TelegramWebApp] Called expand()')

          // Store initData for backend verification
          setInitData(webApp.initData)
          console.log('[TelegramWebApp] Set initData:', webApp.initData ? 'present' : 'empty')

          // Get user data
          if (webApp.initDataUnsafe?.user) {
            const userData = webApp.initDataUnsafe.user
            setUser(userData)
            console.log('[TelegramWebApp] User found:', userData)
            
            // Fetch user photo from backend
            if (userData.id) {
              fetchUserPhoto(userData.id).then(photoUrl => {
                if (photoUrl) {
                  setUser(prev => prev ? { ...prev, photo_url: photoUrl } : prev)
                }
              })
            }
          } else {
            console.error('[TelegramWebApp] No user in initDataUnsafe')
            setError('Пользовательские данные недоступны')
          }

          // Initialize theme
          updateTheme(webApp)

          // Listen for theme changes
          if (webApp.onEvent) {
            webApp.onEvent('themeChanged', () => updateTheme(webApp))
          }

          setIsReady(true)
          console.log('[TelegramWebApp] Initialization complete!')
        } else {
          console.error('[TelegramWebApp] Telegram Web App not available')
          console.error('[TelegramWebApp] window:', typeof window)
          console.error('[TelegramWebApp] window.Telegram:', window.Telegram)
          setError('Telegram Web App не инициализирован')
        }
      } catch (err) {
        console.error('Ошибка инициализации Telegram Web App:', err)
        setError('Ошибка инициализации Telegram Web App')
      }
    }

    // Initialize after a short delay to ensure DOM is ready
    const timer = setTimeout(initializeTelegramWebApp, 100)

    return () => clearTimeout(timer)
  }, [])

  const closeWebApp = () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.close()
    }
  }

  const showMainButton = (text: string, onClick: () => void) => {
    if (window.Telegram?.WebApp) {
      const { MainButton } = window.Telegram.WebApp
      MainButton.text = text
      MainButton.show()
      MainButton.onClick(onClick)
    }
  }

  const hideMainButton = () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.MainButton.hide()
    }
  }

  const showBackButton = (onClick: () => void) => {
    if (window.Telegram?.WebApp) {
      const { BackButton } = window.Telegram.WebApp
      BackButton.show()
      BackButton.onClick(onClick)
    }
  }

  const hideBackButton = () => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.BackButton.hide()
    }
  }

  const hapticFeedback = {
    impact: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.impactOccurred(style)
      }
    },
    notification: (type: 'error' | 'success' | 'warning') => {
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.notificationOccurred(type)
      }
    },
    selection: () => {
      if (window.Telegram?.WebApp?.HapticFeedback) {
        window.Telegram.WebApp.HapticFeedback.selectionChanged()
      }
    }
  }

  const openInvoice = (url: string, callback?: (status: string) => void) => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.openInvoice(url, callback)
    }
  }

  return {
    isReady,
    user,
    initData,
    error,
    theme,
    closeWebApp,
    showMainButton,
    hideMainButton,
    showBackButton,
    hideBackButton,
    hapticFeedback,
    openInvoice,
    webApp: window.Telegram?.WebApp
  }
}
