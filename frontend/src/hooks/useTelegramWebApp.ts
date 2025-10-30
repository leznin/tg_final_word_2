import { useEffect, useState } from 'react'

export interface TelegramUserData {
  id: number
  first_name?: string
  last_name?: string
  username?: string
  language_code?: string
  is_premium?: boolean
  is_bot?: boolean
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

  const updateTheme = (webApp: any) => {
    const newTheme: TelegramThemeData = {
      colorScheme: webApp.colorScheme || 'light',
      themeParams: webApp.themeParams || {}
    }
    setTheme(newTheme)
  }

  useEffect(() => {
    const initializeTelegramWebApp = () => {
      try {
        // Check if Telegram Web App is available
        if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
          const webApp = window.Telegram.WebApp

          // Initialize the Web App
          webApp.ready()

          // Expand the Web App to full height
          webApp.expand()

          // Store initData for backend verification
          setInitData(webApp.initData)

          // Get user data
          if (webApp.initDataUnsafe?.user) {
            setUser(webApp.initDataUnsafe.user)
          } else {
            setError('Пользовательские данные недоступны')
          }

          // Initialize theme
          updateTheme(webApp)

          // Listen for theme changes
          if (webApp.onEvent) {
            webApp.onEvent('themeChanged', () => updateTheme(webApp))
          }

          setIsReady(true)
        } else {
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
    webApp: window.Telegram?.WebApp
  }
}
