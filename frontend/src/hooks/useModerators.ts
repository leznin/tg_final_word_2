import { useQuery } from '@tanstack/react-query';
import { api } from '../utils/api';
import { Moderator } from '../types';

export const useModerators = () => {
  return useQuery({
    queryKey: ['moderators'],
    queryFn: async (): Promise<{ moderators: Moderator[] }> => {
      const response = await api.get('/moderators');
      return response.data;
    },
  });
};