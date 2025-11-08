/**
 * Session storage utility for Telegram Mini App
 * Manages user sessions with 2-hour expiration
 */

const SESSION_KEY = 'miniapp_session'
const SESSION_DURATION = 2 * 60 * 60 * 1000 // 2 hours in milliseconds

export interface MiniAppSession {
  userId: number
  verified: boolean
  token?: string
  expiresAt: number
  createdAt: number
}

/**
 * Save session to localStorage with expiration time
 */
export const saveSession = (userId: number, token?: string): void => {
  const now = Date.now()
  const session: MiniAppSession = {
    userId,
    verified: true,
    token,
    expiresAt: now + SESSION_DURATION,
    createdAt: now
  }
  
  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))
    console.log('[SessionStorage] Session saved:', {
      userId,
      expiresAt: new Date(session.expiresAt).toISOString()
    })
  } catch (error) {
    console.error('[SessionStorage] Error saving session:', error)
  }
}

/**
 * Get current session if it exists and is not expired
 * Returns null if session doesn't exist or is expired
 */
export const getSession = (): MiniAppSession | null => {
  try {
    const sessionData = localStorage.getItem(SESSION_KEY)
    
    if (!sessionData) {
      console.log('[SessionStorage] No session found')
      return null
    }
    
    const session: MiniAppSession = JSON.parse(sessionData)
    const now = Date.now()
    
    // Check if session is expired
    if (now >= session.expiresAt) {
      console.log('[SessionStorage] Session expired')
      clearSession()
      return null
    }
    
    console.log('[SessionStorage] Valid session found:', {
      userId: session.userId,
      expiresAt: new Date(session.expiresAt).toISOString(),
      timeRemaining: Math.round((session.expiresAt - now) / 1000 / 60) + ' minutes'
    })
    
    return session
  } catch (error) {
    console.error('[SessionStorage] Error getting session:', error)
    clearSession()
    return null
  }
}

/**
 * Check if there is a valid session
 */
export const hasValidSession = (): boolean => {
  return getSession() !== null
}

/**
 * Clear the current session
 */
export const clearSession = (): void => {
  try {
    localStorage.removeItem(SESSION_KEY)
    console.log('[SessionStorage] Session cleared')
  } catch (error) {
    console.error('[SessionStorage] Error clearing session:', error)
  }
}

/**
 * Get remaining session time in milliseconds
 */
export const getRemainingTime = (): number => {
  const session = getSession()
  if (!session) return 0
  
  return Math.max(0, session.expiresAt - Date.now())
}

/**
 * Extend session by another 2 hours
 */
export const extendSession = (): boolean => {
  const session = getSession()
  if (!session) return false
  
  const now = Date.now()
  session.expiresAt = now + SESSION_DURATION
  
  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session))
    console.log('[SessionStorage] Session extended:', {
      userId: session.userId,
      newExpiresAt: new Date(session.expiresAt).toISOString()
    })
    return true
  } catch (error) {
    console.error('[SessionStorage] Error extending session:', error)
    return false
  }
}
