import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../utils/api'
import {
  UserSearchRequest,
  UserSearchResponse,
  TelegramUserVerifyRequest,
  TelegramUserVerifyResponse,
  SearchLimitResponse
} from '../types/mini-app'

export const useUserSearch = () => {
  const queryClient = useQueryClient()

  const searchUsersMutation = useMutation({
    mutationFn: async (request: UserSearchRequest): Promise<UserSearchResponse> => {
      const response = await api.post('/mini-app/search-users', request)
      return response.data
    },
    onSuccess: () => {
      // Invalidate search limits to refresh after search
      queryClient.invalidateQueries({ queryKey: ['searchLimits'] })
    }
  })

  const verifyUserMutation = useMutation({
    mutationFn: async (request: TelegramUserVerifyRequest): Promise<TelegramUserVerifyResponse> => {
      const response = await api.post('/mini-app/verify-user', request)
      return response.data
    },
  })

  const useSearchLimits = (telegramUserId?: number) => {
    return useQuery<SearchLimitResponse>({
      queryKey: ['searchLimits', telegramUserId],
      queryFn: async () => {
        if (!telegramUserId) throw new Error('No telegram user id')
        const response = await api.get(`/mini-app/search-limits/${telegramUserId}`)
        return response.data
      },
      enabled: !!telegramUserId,
      refetchInterval: 30000, // Refetch every 30 seconds
    })
  }

  return {
    searchUsers: searchUsersMutation.mutate,
    searchUsersAsync: searchUsersMutation.mutateAsync,
    isSearching: searchUsersMutation.isPending,
    searchError: searchUsersMutation.error,
    searchData: searchUsersMutation.data,

    verifyUser: verifyUserMutation.mutate,
    verifyUserAsync: verifyUserMutation.mutateAsync,
    isVerifying: verifyUserMutation.isPending,
    verifyError: verifyUserMutation.error,
    verifyData: verifyUserMutation.data,

    useSearchLimits,
  }
}
