import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';

export interface SubscriptionPrice {
  id: number;
  subscription_type: string;
  price_stars: number;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export const useSubscriptionPrices = () => {
  return useQuery({
    queryKey: ['subscription-prices'],
    queryFn: async (): Promise<SubscriptionPrice[]> => {
      const response = await api.get('/subscription-prices/');
      return response.data;
    },
  });
};

export const useCreateSubscriptionPrice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: Omit<SubscriptionPrice, 'id' | 'created_at' | 'updated_at'>): Promise<SubscriptionPrice> => {
      const response = await api.post('/subscription-prices/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription-prices'] });
    },
  });
};

export const useUpdateSubscriptionPrice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: Partial<SubscriptionPrice> }): Promise<SubscriptionPrice> => {
      const response = await api.put(`/subscription-prices/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription-prices'] });
    },
  });
};

export const useDeleteSubscriptionPrice = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number): Promise<void> => {
      await api.delete(`/subscription-prices/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscription-prices'] });
    },
  });
};



