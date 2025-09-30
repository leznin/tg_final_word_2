import { useQuery } from '@tanstack/react-query';

const API_BASE_URL = '/api';

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
      const response = await fetch(`${API_BASE_URL}/subscription-prices/`);
      if (!response.ok) {
        throw new Error('Failed to fetch subscription prices');
      }
      return response.json();
    },
  });
};

export const useCreateSubscriptionPrice = () => {
  return useQuery({
    queryKey: ['create-subscription-price'],
    queryFn: async (data: Omit<SubscriptionPrice, 'id' | 'created_at' | 'updated_at'>): Promise<SubscriptionPrice> => {
      const response = await fetch(`${API_BASE_URL}/subscription-prices/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error('Failed to create subscription price');
      }
      return response.json();
    },
    enabled: false,
  });
};

export const useUpdateSubscriptionPrice = () => {
  return useQuery({
    queryKey: ['update-subscription-price'],
    queryFn: async ({ id, data }: { id: number; data: Partial<SubscriptionPrice> }): Promise<SubscriptionPrice> => {
      const response = await fetch(`${API_BASE_URL}/subscription-prices/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error('Failed to update subscription price');
      }
      return response.json();
    },
    enabled: false,
  });
};

export const useDeleteSubscriptionPrice = () => {
  return useQuery({
    queryKey: ['delete-subscription-price'],
    queryFn: async (id: number): Promise<void> => {
      const response = await fetch(`${API_BASE_URL}/subscription-prices/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete subscription price');
      }
    },
    enabled: false,
  });
};

