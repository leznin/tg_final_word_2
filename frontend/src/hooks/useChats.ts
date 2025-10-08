import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { Chat, ChatDetailResponse, LinkChannelResponse, ChatModerator, AddModeratorRequest, ModeratorResponse, ChatSubscription, ChatSubscriptionCreate } from '../types';

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

export const useChatModerators = (chatId: string) => {
  return useQuery({
    queryKey: ['chat-moderators', chatId],
    queryFn: async (): Promise<ChatModerator[]> => {
      const response = await api.get(`/moderators/chat/${chatId}`);
      return response.data;
    },
    enabled: !!chatId,
  });
};

export const useAddModerator = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ chatId, moderatorData }: { chatId: number; moderatorData: AddModeratorRequest }): Promise<ChatModerator> => {
      const response = await api.post(`/moderators`, {
        chat_id: chatId,
        ...moderatorData
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['chat-moderators'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
    },
  });
};

export const useRemoveModerator = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (moderatorId: number): Promise<ModeratorResponse> => {
      const response = await api.delete(`/moderators/${moderatorId}`);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate relevant queries
      queryClient.invalidateQueries({ queryKey: ['chat-moderators'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
    },
  });
};

export interface ChatMember {
  id: number;
  chat_id: number;
  telegram_user_id: number;
  is_bot?: boolean;
  first_name?: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  added_to_attachment_menu?: boolean;
  can_join_groups?: boolean;
  can_read_all_group_messages?: boolean;
  supports_inline_queries?: boolean;
  can_connect_to_business?: boolean;
  has_main_web_app?: boolean;
  joined_at?: string;
  created_at?: string;
  updated_at?: string;
  user_groups: Array<{
    title: string;
    telegram_chat_id: number;
    chat_type: string;
  }>;
}

export const useChatMembers = (chatId: string, search: string = '', page: number = 1, pageSize: number = 30) => {
  const skip = (page - 1) * pageSize;

  return useQuery({
    queryKey: ['chat-members', chatId, search, page, pageSize],
    queryFn: async (): Promise<{ members: ChatMember[]; total: number }> => {
      const response = await api.get(`/chat-members/chat/${chatId}`, {
        params: { skip, limit: pageSize, search: search || undefined }
      });
      return response.data;
    },
    enabled: !!chatId,
  });
};

export const useChatSubscriptionStatus = (chatId: string) => {
  return useQuery({
    queryKey: ['chat-subscription-status', chatId],
    queryFn: async () => {
      const response = await api.get(`/chat-subscriptions/chat/${chatId}/active`);
      return response.data;
    },
    enabled: !!chatId,
  });
};

export const useCreateChatSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (subscriptionData: ChatSubscriptionCreate): Promise<ChatSubscription> => {
      const response = await api.post('/chat-subscriptions/', subscriptionData);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
      queryClient.invalidateQueries({ queryKey: ['chat-subscription-status'] });
    },
  });
};

export const useDeactivateChatSubscription = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (subscriptionId: number): Promise<void> => {
      await api.delete(`/chat-subscriptions/${subscriptionId}`);
    },
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: ['chats'] });
      queryClient.invalidateQueries({ queryKey: ['chat-detail'] });
      queryClient.invalidateQueries({ queryKey: ['chat-subscription-status'] });
    },
  });
};