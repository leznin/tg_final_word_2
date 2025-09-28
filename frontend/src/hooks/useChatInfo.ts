import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { ChatInfoResponse, BulkChatInfoResponse } from '../types';

export const useGetChatInfo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (telegramChatId: number): Promise<ChatInfoResponse> => {
      const response = await api.get(`/chat-info/chat/${telegramChatId}`);
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate and refetch chats data to show updated information
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
    },
  });
};

export const useGetAllChatsInfo = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (): Promise<BulkChatInfoResponse> => {
      const response = await api.post('/chat-info/chats/bulk-info');
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate and refetch chats data to show updated information
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });

      // Log detailed results for debugging
      console.log('Bulk chat info results:', data);
      if (data.errors && data.errors.length > 0) {
        console.warn('Chat info errors:', data.errors);
      }
    },
  });
};
