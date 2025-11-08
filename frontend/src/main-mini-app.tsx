import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import MiniApp from './MiniApp.tsx'
import './index.css'

console.log('='.repeat(60))
console.log('[main-mini-app.tsx] LOADING MINI APP ENTRY POINT')
console.log('[main-mini-app.tsx] Current URL:', window.location.href)
console.log('[main-mini-app.tsx] Current pathname:', window.location.pathname)
console.log('[main-mini-app.tsx] Document URL:', document.URL)
console.log('[main-mini-app.tsx] Telegram WebApp available:', !!window.Telegram?.WebApp)

// CRITICAL: Ensure we're loading mini-app.html, not index.html
if (!window.location.pathname.includes('mini-app.html') && !window.location.pathname.includes('/mini-app/')) {
  console.error('[main-mini-app.tsx] ❌ WRONG ENTRY POINT!')
  console.error('[main-mini-app.tsx] Expected: /mini-app.html')
  console.error('[main-mini-app.tsx] Got:', window.location.pathname)
  
  // Force redirect to mini-app.html
  const newUrl = new URL(window.location.href)
  newUrl.pathname = '/mini-app.html'
  console.log('[main-mini-app.tsx] Redirecting to:', newUrl.toString())
  window.location.href = newUrl.toString()
}

console.log('='.repeat(60))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        if ((error as any)?.response?.status === 401) {
          return false
        }
        return failureCount < 3
      },
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <HashRouter>
        <MiniApp />
      </HashRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
