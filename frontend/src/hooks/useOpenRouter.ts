import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import {
  OpenRouterSettings,
  OpenRouterSettingsCreate,
  OpenRouterSettingsUpdate,
  OpenRouterModel,
  OpenRouterBalance,
  OpenRouterModelsResponse,
  OpenRouterBalanceResponse
} from '../types';

export const useOpenRouterSettings = () => {
  return useQuery({
    queryKey: ['openrouter-settings'],
    queryFn: async (): Promise<OpenRouterSettings | null> => {
      try {
        const response = await api.get('/openrouter/settings');
        return response.data;
      } catch (error: any) {
        // Return null if settings not found (404)
        if (error.response?.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });
};

export const useSaveOpenRouterSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (settings: OpenRouterSettingsCreate): Promise<OpenRouterSettings> => {
      const response = await api.post('/openrouter/settings', settings);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['openrouter-settings'] });
      queryClient.invalidateQueries({ queryKey: ['openrouter-balance'] });
    },
  });
};

export const useUpdateOpenRouterSettings = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (settings: OpenRouterSettingsUpdate): Promise<OpenRouterSettings> => {
      const response = await api.put('/openrouter/settings', settings);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['openrouter-settings'] });
      queryClient.invalidateQueries({ queryKey: ['openrouter-balance'] });
    },
  });
};

export const useOpenRouterModels = () => {
  return useQuery({
    queryKey: ['openrouter-models'],
    queryFn: async (): Promise<OpenRouterModelsResponse> => {
      const response = await api.get('/openrouter/models');
      return response.data;
    },
    enabled: false, // Only fetch when explicitly called
  });
};

export const useOpenRouterBalance = () => {
  return useQuery({
    queryKey: ['openrouter-balance'],
    queryFn: async (): Promise<OpenRouterBalanceResponse> => {
      const response = await api.get('/openrouter/balance');
      return response.data;
    },
    enabled: false, // Only fetch when explicitly called
  });
};
