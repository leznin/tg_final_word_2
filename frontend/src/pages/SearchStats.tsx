import React, { useEffect, useState } from 'react'
import { api } from '../utils/api'

interface SearchStatsEntry {
  user_id: number
  telegram_user_id: number
  username?: string
  first_name?: string
  last_name?: string
  total_searches: number
  last_search_at: string
  searches_today: number
}

interface SearchStatsResponse {
  total_users: number
  total_searches_all_time: number
  total_searches_today: number
  stats: SearchStatsEntry[]
}

interface SearchBoostPrice {
  id: number
  boost_amount: number
  price_stars: number
  currency: string
  is_active: boolean
  created_at: string
  updated_at: string
}

const SearchStats: React.FC = () => {
  const [stats, setStats] = useState<SearchStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [boostPrice, setBoostPrice] = useState<SearchBoostPrice | null>(null)
  const [editingPrice, setEditingPrice] = useState(false)
  const [newPrice, setNewPrice] = useState<number>(50)
  const [savingPrice, setSavingPrice] = useState(false)

  useEffect(() => {
    fetchStats()
    fetchBoostPrice()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      const response = await api.get<SearchStatsResponse>('/admin/search-stats')
      setStats(response.data)
      setError(null)
    } catch (err: any) {
      console.error('Failed to fetch search stats:', err)
      setError(err?.response?.data?.detail || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  const fetchBoostPrice = async () => {
    try {
      const response = await api.get<SearchBoostPrice>('/admin/search-boost/price')
      setBoostPrice(response.data)
      setNewPrice(response.data.price_stars)
    } catch (err: any) {
      console.error('Failed to fetch boost price:', err)
      // Price might not be configured yet, that's okay
      // If it's a real error (not 404), we should still show something
      if (err?.response?.status !== 404) {
        console.error('Unexpected error fetching boost price:', err)
      }
    }
  }

  const handleSavePrice = async () => {
    if (newPrice < 1) {
      alert('Price must be at least 1 star')
      return
    }

    try {
      setSavingPrice(true)
      await api.put('/admin/search-boost/price', { price_stars: newPrice })
      await fetchBoostPrice()
      setEditingPrice(false)
      alert('Price updated successfully!')
    } catch (err: any) {
      console.error('Failed to update price:', err)
      alert(err?.response?.data?.detail || 'Failed to update price')
    } finally {
      setSavingPrice(false)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getUserName = (entry: SearchStatsEntry) => {
    if (entry.first_name || entry.last_name) {
      return `${entry.first_name || ''} ${entry.last_name || ''}`.trim()
    }
    return entry.username ? `@${entry.username}` : `User ${entry.telegram_user_id}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="p-6">
        <div className="text-gray-500">No data available</div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Search Usage Statistics</h1>
        <button
          onClick={fetchStats}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Total Users</div>
          <div className="text-4xl font-bold mt-2">{stats.total_users}</div>
          <div className="text-xs mt-1 opacity-75">who performed searches</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">All Time Searches</div>
          <div className="text-4xl font-bold mt-2">{stats.total_searches_all_time}</div>
          <div className="text-xs mt-1 opacity-75">total search operations</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="text-sm font-medium opacity-90">Today's Searches</div>
          <div className="text-4xl font-bold mt-2">{stats.total_searches_today}</div>
          <div className="text-xs mt-1 opacity-75">in the last 24 hours</div>
        </div>
      </div>

      {/* Boost Price Configuration */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Search Boost Price Settings</h2>
          {!editingPrice && (
            <button
              onClick={() => setEditingPrice(true)}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Edit Price
            </button>
          )}
        </div>
        
        {boostPrice ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Boost Amount</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">{boostPrice.boost_amount} searches</div>
              </div>
              
              <div className="bg-yellow-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Current Price</div>
                <div className="text-2xl font-bold text-yellow-600 mt-1">{boostPrice.price_stars} ⭐</div>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4">
                <div className="text-sm text-gray-600">Status</div>
                <div className={`text-sm font-semibold mt-2 ${boostPrice.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {boostPrice.is_active ? '✓ Active' : '✗ Inactive'}
                </div>
              </div>
            </div>

            {editingPrice && (
              <div className="border-t pt-4 mt-4">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Price (Telegram Stars)
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={newPrice}
                      onChange={(e) => setNewPrice(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleSavePrice}
                      disabled={savingPrice}
                      className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {savingPrice ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      onClick={() => {
                        setEditingPrice(false)
                        setNewPrice(boostPrice.price_stars)
                      }}
                      className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="text-xs text-gray-500 bg-blue-50 rounded-lg p-3">
              ℹ️ Users can purchase up to 2 boosts per day (24 hours). Each boost provides {boostPrice.boost_amount} additional searches.
            </div>
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            <p>Boost price not configured yet.</p>
            <button
              onClick={() => setEditingPrice(true)}
              className="mt-4 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Configure Price
            </button>
          </div>
        )}
      </div>

      {/* User Stats Table */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-xl font-semibold text-gray-900">User Activity</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Telegram ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Searches
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Today
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Search
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {stats.stats.map((entry) => (
                <tr key={entry.user_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                        {getUserName(entry).charAt(0).toUpperCase()}
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {getUserName(entry)}
                        </div>
                        {entry.username && (
                          <div className="text-sm text-gray-500">
                            @{entry.username}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{entry.telegram_user_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-semibold text-gray-900">{entry.total_searches}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      entry.searches_today >= 8
                        ? 'bg-red-100 text-red-800'
                        : entry.searches_today >= 5
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                    }`}>
                      {entry.searches_today}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(entry.last_search_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {stats.stats.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No search activity yet
          </div>
        )}
      </div>
    </div>
  )
}

export default SearchStats
