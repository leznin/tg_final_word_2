import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../utils/api'
import {
  UserSearchRequest,
  UserSearchResponse,
  TelegramUserVerifyRequest,
  TelegramUserVerifyResponse
} from '../types/mini-app'

export const useUserSearch = () => {
  const queryClient = useQueryClient()

  const searchUsersMutation = useMutation({
    mutationFn: async (request: UserSearchRequest): Promise<UserSearchResponse> => {
      const response = await api.post('/mini-app/search-users', request)
      return response.data
    },
  })

  const verifyUserMutation = useMutation({
    mutationFn: async (request: TelegramUserVerifyRequest): Promise<TelegramUserVerifyResponse> => {
      const response = await api.post('/mini-app/verify-user', request)
      return response.data
    },
  })

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
  }
}
