import { useEffect, useState } from 'react'
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import MiniAppUserSearch from './pages/MiniAppUserSearch'
import { hasValidSession } from './utils/sessionStorage'
import './index.css'

function MiniApp() {
  const [isCheckingSession, setIsCheckingSession] = useState(true)
  const [shouldRedirect, setShouldRedirect] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  // Log all location changes
  useEffect(() => {
    console.log('[MiniApp] Location changed:', {
      pathname: location.pathname,
      search: location.search,
      hash: location.hash,
      fullUrl: window.location.href
    })
  }, [location])

  useEffect(() => {
    // Check if this is a page reload (not first open from Telegram)
    const checkSession = () => {
      console.log('[MiniApp] Checking session...')
      console.log('[MiniApp] Current URL:', window.location.href)
      console.log('[MiniApp] Telegram WebApp available:', !!window.Telegram?.WebApp)
      console.log('[MiniApp] Telegram initData:', window.Telegram?.WebApp?.initData ? 'present' : 'empty')
      
      // Check if we have Telegram WebApp available (first open from Telegram)
      const hasTelegramWebApp = window.Telegram?.WebApp?.initData
      
      if (hasTelegramWebApp) {
        // First open from Telegram - allow verification
        console.log('[MiniApp] Telegram WebApp detected, allowing verification')
        setIsCheckingSession(false)
        // Navigate to user-search page
        navigate('/', { replace: true })
        return
      }
      
      // Page reload without Telegram context - check session
      const validSession = hasValidSession()
      
      if (!validSession) {
        console.log('[MiniApp] No valid session on reload, redirecting to Google')
        setShouldRedirect(true)
        // Delay redirect to show message
        setTimeout(() => {
          window.location.href = 'https://www.google.com'
        }, 1000)
        return
      }
      
      console.log('[MiniApp] Valid session found on reload')
      setIsCheckingSession(false)
      // Navigate to user-search page
      navigate('/', { replace: true })
    }

    checkSession()
  }, [])

  // Show redirect message
  if (shouldRedirect) {
    return (
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: 'var(--tg-theme-bg-color, #ffffff)',
        color: 'var(--tg-theme-text-color, #000000)',
        padding: '20px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏱️</div>
        <div style={{ fontSize: '18px', marginBottom: '10px' }}>Сессия истекла</div>
        <div style={{ fontSize: '14px', opacity: 0.7 }}>Перенаправление...</div>
      </div>
    )
  }

  // Show loading while checking session
  if (isCheckingSession) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: 'var(--tg-theme-bg-color, #ffffff)',
        color: 'var(--tg-theme-text-color, #000000)'
      }}>
        <div>Проверка...</div>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/" element={<MiniAppUserSearch />} />
      <Route path="/user-search" element={<MiniAppUserSearch />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default MiniApp
