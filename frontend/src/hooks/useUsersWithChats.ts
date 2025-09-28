import { useQuery } from '@tanstack/react-query';
import { api } from '../utils/api';
import { UserWithChats } from '../types';

export const useUsersWithChats = () => {
  return useQuery({
    queryKey: ['users-with-chats'],
    queryFn: async (): Promise<UserWithChats[]> => {
      const response = await api.get('/users/with-chats');
      return response.data;
    },
  });
};
