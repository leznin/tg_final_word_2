import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { ManagerChatInfo, ManagerChatAccessBulk } from '../types';

// Get manager's chats
export const useManagerChats = (managerId: number) => {
  return useQuery({
    queryKey: ['managerChats', managerId],
    queryFn: async () => {
      const response = await api.get<ManagerChatInfo[]>(`/manager-access/${managerId}/chats`);
      return response.data;
    },
    enabled: !!managerId,
  });
};

// Assign chats to manager (bulk)
export const useAssignChatsToManager = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: ManagerChatAccessBulk) => {
      const response = await api.post('/manager-access/bulk', data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['managerChats', variables.admin_user_id] });
      queryClient.invalidateQueries({ queryKey: ['chats'] });
    },
  });
};

// Remove chat access
export const useRemoveChatAccess = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ managerId, chatId }: { managerId: number; chatId: number }) => {
      await api.delete(`/manager-access/${managerId}/chats/${chatId}`);
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['managerChats', variables.managerId] });
    },
  });
};

// Get chat managers
export const useChatManagers = (chatId: number) => {
  return useQuery({
    queryKey: ['chatManagers', chatId],
    queryFn: async () => {
      const response = await api.get<{ chat_id: number; manager_ids: number[] }>(
        `/manager-access/chat/${chatId}/managers`
      );
      return response.data;
    },
    enabled: !!chatId,
  });
};
