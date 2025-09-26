import { useQuery } from '@tanstack/react-query';
import { api } from '../utils/api';
import { DashboardStats } from '../types';

export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async (): Promise<DashboardStats> => {
      const response = await api.get('/dashboard/stats');
      return response.data;
    },
  });
};