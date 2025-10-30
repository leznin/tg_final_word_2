import React, { useState, useEffect } from 'react'
import { useTelegramWebApp } from '../hooks/useTelegramWebApp'
import { useUserSearch } from '../hooks/useUserSearch'
import { UserSearchResult } from '../types/mini-app'
import { Loading } from '../components/ui/Loading'

const MiniAppUserSearch: React.FC = () => {
  const { isReady, user, initData, error: telegramError, hapticFeedback } = useTelegramWebApp()
  const { verifyUserAsync, searchUsersAsync, isSearching, searchData, verifyData } = useUserSearch()

  const [searchQuery, setSearchQuery] = useState('')
  const [isVerified, setIsVerified] = useState(false)
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([])
  const [searchError, setSearchError] = useState<string | null>(null)
  const [isPasting, setIsPasting] = useState(false)

  const inputRef = React.useRef<HTMLInputElement>(null)

  // Verify user on component mount
  useEffect(() => {
    if (isReady && initData && !isVerified) {
      verifyUser()
    }
  }, [isReady, initData, isVerified])

  const verifyUser = async () => {
    if (!initData) {
      console.error('No initData available for verification')
      return
    }

    try {
      const verifyRequest = {
        init_data: initData
      }

      const response = await verifyUserAsync(verifyRequest)
      if (response.verified) {
        setIsVerified(true)
        hapticFeedback.notification('success')
      } else {
        console.error('User verification failed:', response.message)
        hapticFeedback.notification('error')
      }
    } catch (error) {
      console.error('Verification error:', error)
      hapticFeedback.notification('error')
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!searchQuery.trim() || searchQuery.trim().length < 2) {
      setSearchError('Введите минимум 2 символа для поиска')
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
      setSearchError('Ошибка поиска. Попробуйте еще раз.')
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

        // Фокусируемся на поле ввода после вставки
        setTimeout(() => {
          if (inputRef.current) {
            inputRef.current.focus()
            // Устанавливаем курсор в конец текста
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

  const getUserDisplayName = (user: UserSearchResult) => {
    if (user.username) {
      return `@${user.username}`
    }
    const nameParts = [user.first_name, user.last_name].filter(Boolean)
    return nameParts.length > 0 ? nameParts.join(' ') : 'Без имени'
  }

  if (!isReady) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loading />
          <p className="mt-4 text-gray-300">Инициализация...</p>
        </div>
      </div>
    )
  }

  if (telegramError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl shadow-2xl p-6 max-w-md w-full text-center">
          <div className="text-red-400 text-5xl mb-4">⚠️</div>
          <h2 className="text-xl font-semibold text-white mb-2">Ошибка</h2>
          <p className="text-gray-300">{telegramError}</p>
          <p className="text-sm text-gray-400 mt-4">
            Это приложение работает только в Telegram
          </p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl shadow-2xl p-6 max-w-md w-full text-center">
          <div className="text-yellow-400 text-5xl mb-4">👤</div>
          <h2 className="text-xl font-semibold text-white mb-2">Пользователь не найден</h2>
          <p className="text-gray-300">
            Не удалось получить данные пользователя из Telegram
          </p>
        </div>
      </div>
    )
  }

  if (!isVerified) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loading />
          <p className="mt-4 text-gray-300">Проверка пользователя...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 shadow-lg">
        <div className="px-4 py-4">
          <h1 className="text-xl font-bold text-white bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Поиск пользователей
          </h1>
          <p className="text-sm text-gray-300 mt-2">
            Привет, {user.first_name || user.username || 'Пользователь'}! 👋
          </p>
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
              placeholder="Введите имя пользователя или @username"
              className="w-full px-4 py-4 pr-20 bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-300 hover:bg-gray-800/70"
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
                title={isPasting ? "Вставка..." : "Вставить из буфера обмена"}
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
            <div className="bg-red-900/30 backdrop-blur-sm border border-red-700/50 rounded-xl p-4">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-red-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <p className="text-red-300 text-sm">{searchError}</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-600 text-white font-semibold py-4 px-4 rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-[1.02] disabled:transform-none disabled:shadow-none"
          >
            <div className="flex items-center justify-center space-x-3">
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white flex-shrink-0"></div>
                  <span>Поиск...</span>
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <span>Найти пользователей</span>
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
              <h2 className="text-lg font-bold text-white">
                Найдено пользователей: <span className="text-blue-400">{searchResults.length}</span>
              </h2>
            </div>
            <div className="space-y-3">
              {searchResults.map((result) => (
                <div
                  key={result.id}
                  className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 hover:bg-gray-800/70"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-white text-lg truncate">
                        {getUserDisplayName(result)}
                      </h3>
                      {result.telegram_id && (
                        <p className="text-sm text-gray-400 mt-2">
                          ID: <span className="text-blue-400">{result.telegram_id}</span>
                        </p>
                      )}
                      {result.language_code && (
                        <p className="text-xs text-gray-500 mt-1">
                          Язык: <span className="text-purple-400">{result.language_code.toUpperCase()}</span>
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
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

        {searchData && searchResults.length === 0 && !isSearching && (
          <div className="mt-8 text-center py-16">
            <div className="bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-2xl p-8 max-w-md mx-auto">
              <div className="text-gray-400 text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-white mb-3">Пользователи не найдены</h3>
              <p className="text-gray-400 leading-relaxed">
                Попробуйте изменить запрос или проверить правильность написания
              </p>
              <div className="mt-4 text-sm text-gray-500">
                💡 Совет: используйте @username для точного поиска
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default MiniAppUserSearch
