import { TelegramThemeData, TelegramThemeParams } from '../hooks/useTelegramWebApp'

export const getThemeColors = (theme: TelegramThemeData): Record<string, string> => {
  const { colorScheme, themeParams } = theme

  // Default colors for light theme
  const defaultLightColors = {
    background: '#ffffff',
    surface: '#f8f9fa',
    surfaceSecondary: '#e9ecef',
    textPrimary: '#212529',
    textSecondary: '#6c757d',
    textHint: '#adb5bd',
    textAccent: '#007bff',
    border: '#dee2e6',
    error: '#dc3545',
    success: '#28a745',
    warning: '#ffc107',
    buttonPrimary: '#007bff',
    buttonPrimaryText: '#ffffff',
    buttonSecondary: '#6c757d',
    headerBg: '#ffffff',
    sectionBg: '#f8f9fa',
    destructive: '#dc3545'
  }

  // Default colors for dark theme
  const defaultDarkColors = {
    background: '#000000',
    surface: '#1a1a1a',
    surfaceSecondary: '#2a2a2a',
    textPrimary: '#ffffff',
    textSecondary: '#b0b0b0',
    textHint: '#808080',
    textAccent: '#4dabf7',
    border: '#404040',
    error: '#ff6b6b',
    success: '#51cf66',
    warning: '#ffd43b',
    buttonPrimary: '#4dabf7',
    buttonPrimaryText: '#ffffff',
    buttonSecondary: '#6c757d',
    headerBg: '#1a1a1a',
    sectionBg: '#2a2a2a',
    destructive: '#ff6b6b'
  }

  // Get base colors based on color scheme
  const baseColors = colorScheme === 'dark' ? defaultDarkColors : defaultLightColors

  // Override with Telegram theme params if available
  const colors = { ...baseColors }

  if (themeParams.bg_color) colors.background = themeParams.bg_color
  if (themeParams.secondary_bg_color) colors.surface = themeParams.secondary_bg_color
  if (themeParams.header_bg_color) colors.headerBg = themeParams.header_bg_color
  if (themeParams.section_bg_color) colors.sectionBg = themeParams.section_bg_color

  if (themeParams.text_color) colors.textPrimary = themeParams.text_color
  if (themeParams.hint_color) colors.textHint = themeParams.hint_color
  if (themeParams.link_color) colors.textAccent = themeParams.link_color
  if (themeParams.accent_text_color) colors.textAccent = themeParams.accent_text_color

  if (themeParams.button_color) colors.buttonPrimary = themeParams.button_color
  if (themeParams.button_text_color) colors.buttonPrimaryText = themeParams.button_text_color

  if (themeParams.destructive_text_color) colors.destructive = themeParams.destructive_text_color

  return colors
}

export const createThemeStyles = (theme: TelegramThemeData): Record<string, React.CSSProperties> => {
  const colors = getThemeColors(theme)

  return {
    // Main container
    container: {
      background: `linear-gradient(135deg, ${colors.background} 0%, ${colors.surface} 100%)`,
      color: colors.textPrimary,
      minHeight: '100vh'
    },

    // Header
    header: {
      background: `${colors.headerBg}80`,
      backdropFilter: 'blur(10px)',
      borderBottom: `1px solid ${colors.border}`,
      color: colors.textPrimary
    },

    // Input field
    input: {
      background: `${colors.surface}80`,
      backdropFilter: 'blur(10px)',
      border: `1px solid ${colors.border}`,
      color: colors.textPrimary
    },
    inputFocus: {
      borderColor: colors.textAccent,
      boxShadow: `0 0 0 2px ${colors.textAccent}20`
    },
    inputPlaceholder: {
      color: colors.textHint
    },

    // Buttons
    buttonPrimary: {
      background: `linear-gradient(135deg, ${colors.buttonPrimary} 0%, ${colors.textAccent} 100%)`,
      color: colors.buttonPrimaryText,
      border: `1px solid ${colors.buttonPrimary}`
    },
    buttonSecondary: {
      background: `${colors.surfaceSecondary}`,
      color: colors.textPrimary,
      border: `1px solid ${colors.border}`
    },

    // Cards
    card: {
      background: `${colors.surface}80`,
      backdropFilter: 'blur(10px)',
      border: `1px solid ${colors.border}`,
      color: colors.textPrimary
    },

    // Text colors
    textPrimary: { color: colors.textPrimary },
    textSecondary: { color: colors.textSecondary },
    textHint: { color: colors.textHint },
    textAccent: { color: colors.textAccent },
    textError: { color: colors.error },
    textSuccess: { color: colors.success },

    // Status colors
    error: { background: `${colors.error}20`, borderColor: colors.error, color: colors.error },
    success: { background: `${colors.success}20`, borderColor: colors.success, color: colors.success },
    warning: { background: `${colors.warning}20`, borderColor: colors.warning, color: colors.warning }
  }
}
