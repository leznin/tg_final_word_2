import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../utils/api';
import { AdminUser, AdminUserCreate, AdminUserUpdate } from '../types';

// Get all admin users
export const useAdminUsers = () => {
  return useQuery({
    queryKey: ['adminUsers'],
    queryFn: async () => {
      const response = await api.get<AdminUser[]>('/admin-users');
      return response.data;
    },
  });
};

// Get current user
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await api.get<AdminUser>('/admin-users/me');
      return response.data;
    },
  });
};

// Get single admin user
export const useAdminUser = (id: number) => {
  return useQuery({
    queryKey: ['adminUser', id],
    queryFn: async () => {
      const response = await api.get<AdminUser>(`/admin-users/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
};

// Create admin user
export const useCreateAdminUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: AdminUserCreate) => {
      const response = await api.post<AdminUser>('/admin-users', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
    },
  });
};

// Update admin user
export const useUpdateAdminUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: AdminUserUpdate }) => {
      const response = await api.put<AdminUser>(`/admin-users/${id}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      queryClient.invalidateQueries({ queryKey: ['adminUser', variables.id] });
    },
  });
};

// Delete admin user
export const useDeleteAdminUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/admin-users/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
    },
  });
};

// Reset admin user password
export const useResetAdminPassword = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post<{ 
        message: string; 
        new_password: string;
        email: string;
      }>(`/admin-users/${id}/reset-password`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['adminUsers'] });
      queryClient.invalidateQueries({ queryKey: ['adminUser', id] });
    },
  });
};
