import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import {
  ChatPost,
  ChatPostCreate,
  ChatPostUpdate,
  ChatPostListResponse,
  PinPostRequest,
  MediaUploadResponse
} from '../types';

export const useChatPosts = (chatId: number, page: number = 1, pageSize: number = 20) => {
  return useQuery({
    queryKey: ['chat-posts', chatId, page, pageSize],
    queryFn: async (): Promise<ChatPostListResponse> => {
      const response = await api.get(`/chat-posts/chat/${chatId}`, {
        params: { page, page_size: pageSize }
      });
      return response.data;
    },
    enabled: !!chatId,
  });
};

export const useChatPost = (postId: number) => {
  return useQuery({
    queryKey: ['chat-post', postId],
    queryFn: async (): Promise<ChatPost> => {
      const response = await api.get(`/chat-posts/${postId}`);
      return response.data;
    },
    enabled: !!postId,
  });
};

export const useCreateChatPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postData: ChatPostCreate): Promise<ChatPost> => {
      const response = await api.post('/chat-posts/', postData);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['chat-posts', variables.chat_id] });
    },
  });
};

export const useUpdateChatPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, postData }: { postId: number; postData: ChatPostUpdate }): Promise<ChatPost> => {
      const response = await api.put(`/chat-posts/${postId}`, postData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chat-posts', data.chat_id] });
      queryClient.invalidateQueries({ queryKey: ['chat-post', data.id] });
    },
  });
};

export const useDeleteChatPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: number): Promise<void> => {
      await api.delete(`/chat-posts/${postId}`);
    },
    onSuccess: (_, postId) => {
      queryClient.invalidateQueries({ queryKey: ['chat-posts'] });
      queryClient.invalidateQueries({ queryKey: ['chat-post', postId] });
    },
  });
};

export const usePinChatPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ postId, pinRequest }: { postId: number; pinRequest: PinPostRequest }): Promise<ChatPost> => {
      const response = await api.post(`/chat-posts/${postId}/pin`, pinRequest);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chat-posts', data.chat_id] });
      queryClient.invalidateQueries({ queryKey: ['chat-post', data.id] });
    },
  });
};

export const useUnpinChatPost = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (postId: number): Promise<ChatPost> => {
      const response = await api.post(`/chat-posts/${postId}/unpin`);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['chat-posts', data.chat_id] });
      queryClient.invalidateQueries({ queryKey: ['chat-post', data.id] });
    },
  });
};

export const useUploadChatMedia = () => {
  return useMutation({
    mutationFn: async (file: File): Promise<MediaUploadResponse> => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/chat-posts/upload-media', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  });
};
