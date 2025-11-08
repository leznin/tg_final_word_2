import React, { useState, useEffect } from 'react'
import { useTelegramWebApp } from '../hooks/useTelegramWebApp'
import { useUserSearch } from '../hooks/useUserSearch'
import { UserSearchResult } from '../types/mini-app'
import { Loading } from '../components/ui/Loading'
import { UserAvatar } from '../components/UserAvatar'
import { createThemeStyles } from '../utils/themeUtils'
import { saveSession, getSession, hasValidSession } from '../utils/sessionStorage'

const MiniAppUserSearch: React.FC = () => {
  const { isReady, user, initData, error: telegramError, hapticFeedback, theme } = useTelegramWebApp()
  const { verifyUserAsync, searchUsersAsync, isSearching } = useUserSearch()

  // Create theme styles
  const themeStyles = createThemeStyles(theme)

  const [searchQuery, setSearchQuery] = useState('')
  const [isVerified, setIsVerified] = useState(false)
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([])
  const [searchError, setSearchError] = useState<string | null>(null)
  const [isPasting, setIsPasting] = useState(false)

  const inputRef = React.useRef<HTMLInputElement>(null)

  // Check for existing session on mount
  useEffect(() => {
    console.log('[MiniAppUserSearch] Component mounted, checking for existing session')
    const existingSession = getSession()
    
    if (existingSession && existingSession.verified) {
      console.log('[MiniAppUserSearch] Found existing valid session, skipping verification')
      setIsVerified(true)
      return
    }
    
    console.log('[MiniAppUserSearch] No valid session found, will verify with Telegram')
  }, [])

  // Verify user on component mount if not already verified
  useEffect(() => {
    console.log('[MiniAppUserSearch] useEffect triggered')
    console.log('[MiniAppUserSearch] isReady:', isReady)
    console.log('[MiniAppUserSearch] initData:', initData ? 'present' : 'empty')
    console.log('[MiniAppUserSearch] isVerified:', isVerified)
    console.log('[MiniAppUserSearch] user:', user)
    
    if (isReady && initData && !isVerified && !hasValidSession()) {
      console.log('[MiniAppUserSearch] Calling verifyUser()')
      verifyUser()
    }
  }, [isReady, initData, isVerified])

  const verifyUser = async () => {
    console.log('[MiniAppUserSearch] verifyUser() called')
    if (!initData) {
      console.error('[MiniAppUserSearch] No initData available for verification')
      return
    }

    try {
      console.log('[MiniAppUserSearch] Sending verification request...')
      const verifyRequest = {
        init_data: initData
      }

      const response = await verifyUserAsync(verifyRequest)
      console.log('[MiniAppUserSearch] Verification response:', response)
      
      if (response.verified) {
        setIsVerified(true)
        
        // Save session to localStorage
        if (user?.id) {
          saveSession(user.id, response.session_token)
          console.log('[MiniAppUserSearch] Session saved for user:', user.id)
        }
        
        hapticFeedback.notification('success')
        console.log('[MiniAppUserSearch] Verification successful!')
      } else {
        console.error('[MiniAppUserSearch] User verification failed:', response.message)
        hapticFeedback.notification('error')
      }
    } catch (error) {
      console.error('[MiniAppUserSearch] Verification error:', error)
      hapticFeedback.notification('error')
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      setSearchError('Enter at least 2 characters to search')
      hapticFeedback.notification('error')
      return
    }

    setSearchError(null)
    hapticFeedback.selection()

    try {
      const response = await searchUsersAsync({
        query: searchQuery.trim(),
        limit: 20,
        offset: 0
      })

      setSearchResults(response.results)
      hapticFeedback.notification('success')
    } catch (error) {
      console.error('Search error:', error)
      setSearchError('Search error. Please try again.')
      setSearchResults([])
      hapticFeedback.notification('error')
    }
  }

  const handlePaste = async () => {
    setIsPasting(true)
    try {
      const text = await navigator.clipboard.readText()
      if (text.trim()) {
        setSearchQuery(text.trim())
        hapticFeedback.selection()

        // Focus on the input field after pasting
        setTimeout(() => {
          if (inputRef.current) {
            inputRef.current.focus()
            // Set cursor to the end of text
            inputRef.current.setSelectionRange(text.trim().length, text.trim().length)
          }
        }, 100)
      } else {
        hapticFeedback.notification('error')
      }
    } catch (error) {
      console.error('Paste error:', error)
      hapticFeedback.notification('error')
    } finally {
      setIsPasting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getFieldNameDisplay = (fieldName: string) => {
    const fieldNames: Record<string, string> = {
      'first_name': 'First Name',
      'last_name': 'Last Name',
      'username': 'Username'
    }
    return fieldNames[fieldName] || fieldName
  }

  const isMaskedAccount = (user: UserSearchResult) => {
    // Check if name or lastname contains asterisks (masked account)
    const hasAsterisks = (str: string | null | undefined) => str && str.includes('*')
    return hasAsterisks(user.first_name) || hasAsterisks(user.last_name)
  }

  const handleSimilarAccountClick = async (result: UserSearchResult) => {
    // Get real ID from masked account
    const realId = result.real_telegram_user_id || result.telegram_user_id
    if (!realId) return

    // Set search query to ID
    setSearchQuery(String(realId))
    hapticFeedback.selection()

    // Perform search
    try {
      const response = await searchUsersAsync({
        query: String(realId),
        limit: 20,
        offset: 0
      })

      setSearchResults(response.results)
      hapticFeedback.notification('success')
    } catch (error) {
      console.error('Search error:', error)
      setSearchError('Search error. Please try again.')
      setSearchResults([])
      hapticFeedback.notification('error')
    }
  }

  if (!isReady) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={themeStyles.container}>
        <div className="text-center">
          <Loading />
          <p className="mt-4" style={themeStyles.textSecondary}>Initializing...</p>
        </div>
      </div>
    )
  }

  if (telegramError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={themeStyles.container}>
        <div className="rounded-xl shadow-2xl p-6 max-w-md w-full text-center" style={themeStyles.card}>
          <div className="text-5xl mb-4" style={themeStyles.textError}>⚠️</div>
          <h2 className="text-xl font-semibold mb-2" style={themeStyles.textPrimary}>Error</h2>
          <p style={themeStyles.textSecondary}>{telegramError}</p>
          <p className="text-sm mt-4" style={themeStyles.textHint}>
            This app only works in Telegram
          </p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={themeStyles.container}>
        <div className="rounded-xl shadow-2xl p-6 max-w-md w-full text-center" style={themeStyles.card}>
          <div className="text-5xl mb-4" style={themeStyles.textWarning}>👤</div>
          <h2 className="text-xl font-semibold mb-2" style={themeStyles.textPrimary}>User not found</h2>
          <p style={themeStyles.textSecondary}>
            Failed to get user data from Telegram
          </p>
        </div>
      </div>
    )
  }

  if (!isVerified) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={themeStyles.container}>
        <div className="text-center">
          <Loading />
          <p className="mt-4" style={themeStyles.textSecondary}>Verifying user...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={themeStyles.container}>
      {/* Header */}
      <div className="backdrop-blur-sm shadow-lg" style={themeStyles.header}>
        <div className="px-4 py-4">
          <div className="flex items-center space-x-3">
            <UserAvatar 
              firstName={user.first_name}
              lastName={user.last_name}
              username={user.username}
              size="md"
              photoUrl={user.photo_url}
            />
            <div className="flex-1 min-w-0">
              <h1 className="text-lg font-bold truncate" style={themeStyles.textPrimary}>
                {user.first_name || user.username || 'User'}
                {user.last_name && ` ${user.last_name}`}
              </h1>
              {user.username && (
                <p className="text-sm truncate" style={themeStyles.textSecondary}>
                  @{user.username}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Search Form */}
      <div className="p-4">
        <form onSubmit={handleSearch} className="space-y-6">
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Enter ID or @username"
              className="w-full px-4 py-4 pr-20 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-300 adaptive-input"
              style={{
                ...themeStyles.input,
                '--placeholder-color': themeStyles.inputPlaceholder.color
              } as React.CSSProperties}
              disabled={isSearching}
            />
            <div className="absolute inset-y-0 right-0 flex items-center pr-4">
              <button
                type="button"
                onClick={handlePaste}
                className={`group relative p-2 rounded-full transition-all duration-300 transform hover:scale-110 active:scale-95 ${
                  isPasting
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 shadow-lg shadow-blue-500/25 animate-pulse'
                    : 'bg-gradient-to-r from-gray-700 to-gray-600 hover:from-purple-600 hover:to-blue-600 shadow-lg hover:shadow-purple-500/25 text-white'
                } ${isSearching || isPasting ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:rotate-12'}`}
                title={isPasting ? "Pasting..." : "Paste from clipboard"}
                disabled={isSearching || isPasting}
              >
                <div className="relative">
                  <svg
                    className={`w-4 h-4 transition-transform duration-300 ${
                      isPasting ? 'animate-spin' : 'group-hover:rotate-12'
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                    />
                  </svg>
                  {!isPasting && (
                    <div className="absolute -top-1 -right-1 w-2 h-2 bg-gradient-to-r from-pink-400 to-purple-500 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300 animate-ping"></div>
                  )}
                </div>
              </button>
            </div>
          </div>

          {searchError && (
            <div className="rounded-xl p-4" style={themeStyles.error}>
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <p className="text-sm">{searchError}</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="w-full font-semibold py-4 px-4 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none disabled:shadow-none"
            style={themeStyles.buttonPrimary}
          >
            <div className="flex items-center justify-center space-x-3">
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white flex-shrink-0"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Find Users</span>
                </>
              )}
            </div>
          </button>
        </form>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-8">
            <div className="flex items-center space-x-3 mb-8">
              <div className="h-8 w-1 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full flex-shrink-0"></div>
              <h2 className="text-lg font-bold" style={themeStyles.textPrimary}>
                Users Found: <span style={themeStyles.textAccent}>{searchResults.length}</span>
              </h2>
            </div>
            <div className="space-y-3">
              {searchResults.map((result) => (
                <div
                  key={result.telegram_user_id}
                  className="rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300"
                  style={themeStyles.card}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      {/* Имя и фамилия */}
                      {(result.first_name || result.last_name) && (
                        <h3 className="font-semibold text-lg truncate" style={themeStyles.textPrimary}>
                          {[result.first_name, result.last_name].filter(Boolean).join(' ')}
                        </h3>
                      )}
                      
                      {/* Username */}
                      {result.username && (
                        <p className="text-sm mt-1" style={themeStyles.textSecondary}>
                          @{result.username}
                        </p>
                      )}
                      
                      {/* ID */}
                      {result.telegram_user_id && (
                        <p className="text-sm mt-2" style={themeStyles.textSecondary}>
                          ID: <span style={themeStyles.textAccent}>{result.telegram_user_id}</span>
                        </p>
                      )}
                      {result.language_code && (
                        <p className="text-xs mt-1" style={themeStyles.textHint}>
                          Language: <span style={themeStyles.textAccent}>{result.language_code.toUpperCase()}</span>
                        </p>
                      )}
                      {result.account_creation_date && (
                        <p className="text-xs mt-1" style={themeStyles.textHint}>
                          Account Created: <span style={themeStyles.textAccent}>{formatDate(result.account_creation_date)}</span>
                        </p>
                      )}

                      {/* History Section */}
                      {result.history && result.history.length > 0 && (
                        <div className="mt-4 pt-4 border-t" style={{ borderColor: themeStyles.textHint.color }}>
                          <h4 className="text-sm font-semibold mb-3 flex items-center gap-2" style={themeStyles.textPrimary}>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Change History ({result.history.length})
                          </h4>
                          <div className="space-y-2 max-h-60 overflow-y-auto">
                            {result.history.map((historyEntry) => (
                              <div
                                key={historyEntry.id}
                                className="text-xs p-3 rounded-lg"
                                style={{ 
                                  backgroundColor: theme.colorScheme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.03)'
                                }}
                              >
                                <div className="flex items-start justify-between gap-2 mb-1">
                                  <span className="font-semibold" style={themeStyles.textAccent}>
                                    {getFieldNameDisplay(historyEntry.field_name)}
                                  </span>
                                  <span style={themeStyles.textHint}>
                                    {formatDate(historyEntry.changed_at)}
                                  </span>
                                </div>
                                <div className="flex items-center gap-2" style={themeStyles.textSecondary}>
                                  <span className="truncate">
                                    {historyEntry.old_value || '(empty)'}
                                  </span>
                                  <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                  </svg>
                                  <span className="truncate font-semibold">
                                    {historyEntry.new_value || '(empty)'}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {isMaskedAccount(result) && (
                        <button
                          onClick={() => handleSimilarAccountClick(result)}
                          className="bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs px-3 py-1 rounded-full font-medium shadow-lg whitespace-nowrap cursor-pointer hover:from-orange-600 hover:to-red-600 transition-all duration-200 transform hover:scale-105 active:scale-95"
                        >
                          🔄 Similar
                        </button>
                      )}
                      {result.is_premium && (
                        <span className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs px-3 py-1 rounded-full font-medium shadow-lg whitespace-nowrap">
                          ⭐ Premium
                        </span>
                      )}
                      {result.is_bot && (
                        <span className="bg-gradient-to-r from-gray-600 to-gray-500 text-white text-xs px-3 py-1 rounded-full font-medium shadow-lg whitespace-nowrap">
                          🤖 Bot
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {searchQuery && searchResults.length === 0 && !isSearching && (
          <div className="mt-8 text-center py-16">
            <div className="rounded-2xl p-8 max-w-md mx-auto" style={themeStyles.card}>
              <div className="text-6xl mb-4" style={themeStyles.textHint}>🔍</div>
              <h3 className="text-xl font-semibold mb-3" style={themeStyles.textPrimary}>No Users Found</h3>
              <p className="leading-relaxed" style={themeStyles.textSecondary}>
                Enter a username or user ID in the search field and click the search button
              </p>
              <div className="mt-4 text-sm" style={themeStyles.textHint}>
                💡 Example: @username or 123456789
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MiniAppUserSearch
