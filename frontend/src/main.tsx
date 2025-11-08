import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

console.log('='.repeat(60))
console.log('[main.tsx] LOADING ADMIN PANEL ENTRY POINT')
console.log('[main.tsx] Current URL:', window.location.href)
console.log('[main.tsx] Current pathname:', window.location.pathname)
console.log('='.repeat(60))

// Check if someone is trying to access admin panel from Telegram Mini App
if (window.Telegram?.WebApp) {
  console.error('[main.tsx] ❌ CRITICAL: Admin panel accessed from Telegram Mini App!')
  console.error('[main.tsx] This should NEVER happen. Redirecting to mini-app.html...')
  
  // Redirect to mini-app.html
  const currentUrl = new URL(window.location.href)
  currentUrl.pathname = '/mini-app.html'
  window.location.href = currentUrl.toString()
  
  // Don't render anything
  throw new Error('Admin panel should not be accessed from Telegram Mini App')
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
