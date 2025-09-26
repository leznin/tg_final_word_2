import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { Chat, ChatDetailResponse, LinkChannelRequest, LinkChannelResponse } from '../types';

export const useChats = () => {
  return useQuery({
    queryKey: ['chats'],
    queryFn: async (): Promise<{ chats: Chat[] }> => {
      const response = await api.get('/chats');
      return response.data;
    },
  });
};

export const useChatDetail = (chatId: string) => {
  return useQuery({
    queryKey: ['chat-detail', chatId],
    queryFn: async (): Promise<ChatDetailResponse> => {
      const response = await api.get(`/chats/${chatId}`);
      return response.data;
    },
    enabled: !!chatId,
  });
};

export const useAvailableChannels = (userId: number) => {
  return useQuery({
    queryKey: ['available-channels', userId],
    queryFn: async (): Promise<Chat[]> => {
      const response = await api.get(`/chats/user/${userId}/available-channels`);
      return response.data;
    },
    enabled: !!userId,
  });
};

export const useLinkChannel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ chatId, channelId }: { chatId: number; channelId: number }): Promise<LinkChannelResponse> => {
      const response = await api.post(`/chats/${chatId}/link-channel`, { channel_id: channelId });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
    },
  });
};

export const useUnlinkChannel = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (chatId: number): Promise<LinkChannelResponse> => {
      const response = await api.delete(`/chats/${chatId}/link-channel`);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
    },
  });
};

export const useLinkedChannel = (chatId: number) => {
  return useQuery({
    queryKey: ['linked-channel', chatId],
    queryFn: async (): Promise<Chat> => {
      const response = await api.get(`/chats/${chatId}/linked-channel`);
      return response.data;
    },
    enabled: !!chatId,
  });
};