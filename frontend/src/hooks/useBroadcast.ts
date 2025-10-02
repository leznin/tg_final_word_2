import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { BroadcastMessageRequest, BroadcastResult, BroadcastStatus, BroadcastUsersCount } from '../types';

export const useBroadcastUsersCount = () => {
  return useQuery({
    queryKey: ['broadcast-users-count'],
    queryFn: async (): Promise<BroadcastUsersCount> => {
      const response = await api.get('/broadcast/users/count');
      return response.data;
    },
  });
};

export const useBroadcastStatus = () => {
  return useQuery({
    queryKey: ['broadcast-status'],
    queryFn: async (): Promise<BroadcastStatus> => {
      const response = await api.get('/broadcast/status');
      return response.data;
    },
    refetchInterval: (data) => {
      // Refetch every 2 seconds if broadcast is running
      return data?.is_running ? 2000 : false;
    },
  });
};

export const useBroadcast = () => {
  const queryClient = useQueryClient();

  const sendBroadcastMutation = useMutation({
    mutationFn: async (request: BroadcastMessageRequest): Promise<BroadcastResult> => {
      const response = await api.post('/broadcast/send', request);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate status query to start polling
      queryClient.invalidateQueries({ queryKey: ['broadcast-status'] });
    },
  });

  return {
    sendBroadcast: sendBroadcastMutation.mutateAsync,
    isSending: sendBroadcastMutation.isPending,
    error: sendBroadcastMutation.error,
    result: sendBroadcastMutation.data,
  };
};

export const useMediaUpload = () => {
  const uploadMediaMutation = useMutation({
    mutationFn: async (file: File): Promise<{ url: string; filename: string; content_type: string; size: number }> => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/broadcast/upload-media', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  });

  return {
    uploadMedia: uploadMediaMutation.mutateAsync,
    isUploading: uploadMediaMutation.isPending,
    error: uploadMediaMutation.error,
  };
};
