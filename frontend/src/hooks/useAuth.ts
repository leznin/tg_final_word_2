import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { getFingerprint } from '../utils/fingerprint';
import { AuthResponse, AuthCheckResponse } from '../types';

export const useAuth = () => {
  const queryClient = useQueryClient();

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['auth'],
    queryFn: async (): Promise<AuthCheckResponse> => {
      const response = await api.get('/auth/check');
      return response.data;
    },
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }): Promise<AuthResponse> => {
      // Get fingerprint before login attempt
      const fingerprint = await getFingerprint();

      const formData = new FormData();
      formData.append('email', credentials.email);
      formData.append('password', credentials.password);
      formData.append('fingerprint', fingerprint);

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    retry: false,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] });
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async (): Promise<AuthResponse> => {
      const response = await api.post('/auth/logout');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] });
    },
  });

  return {
    isAuthenticated: authStatus?.authenticated ?? false,
    user: authStatus?.user,
    isLoading,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    loginError: loginMutation.error,
    loginLoading: loginMutation.isPending,
  };
};