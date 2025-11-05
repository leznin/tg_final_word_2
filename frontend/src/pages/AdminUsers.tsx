import React, { useState } from 'react';
import { Users, Plus, Trash2, Shield, UserCog, Settings } from 'lucide-react';
import { useAdminUsers, useDeleteAdminUser } from '../hooks/useAdminUsers';
import { useCurrentUser } from '../hooks/useAdminUsers';
import { DataTable } from '../components/ui/DataTable';
import { Loading } from '../components/ui/Loading';
import { AdminUser, UserRole } from '../types';
import { CreateManagerModal } from '../components/modals/CreateManagerModal';
import { ManageChatAccessModal } from '../components/modals/ManageChatAccessModal';

export const AdminUsers: React.FC = () => {
  const { data: adminUsers, isLoading } = useAdminUsers();
  const { data: currentUser } = useCurrentUser();
  const deleteAdmin = useDeleteAdminUser();
  
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isAccessModalOpen, setIsAccessModalOpen] = useState(false);
  const [selectedManager, setSelectedManager] = useState<AdminUser | null>(null);

  if (isLoading) return <Loading />;

  const users = adminUsers || [];

  const handleDelete = async (user: AdminUser) => {
    if (window.confirm(`Удалить пользователя ${user.email}?`)) {
      try {
        await deleteAdmin.mutateAsync(user.id);
      } catch (error: any) {
        alert(error.response?.data?.detail || 'Ошибка при удалении');
      }
    }
  };

  const handleManageAccess = (user: AdminUser) => {
    setSelectedManager(user);
    setIsAccessModalOpen(true);
  };

  const columns = [
    {
      key: 'id',
      label: 'ID',
      sortable: true,
      render: (value: number) => (
        <div className="text-xs text-gray-500 font-mono">{value}</div>
      ),
    },
    {
      key: 'email',
      label: 'Email',
      sortable: true,
      render: (value: string) => (
        <div className="font-medium">{value}</div>
      ),
    },
    {
      key: 'username',
      label: 'Имя пользователя',
      sortable: true,
      render: (value: string) => (
        <div className="text-gray-600">{value || '—'}</div>
      ),
    },
    {
      key: 'role',
      label: 'Роль',
      sortable: true,
      render: (value: UserRole) => (
        <div className="flex items-center space-x-2">
          {value === UserRole.ADMIN ? (
            <>
              <Shield className="w-4 h-4 text-red-500" />
              <span className="px-2 py-1 text-xs font-semibold text-red-700 bg-red-100 rounded-full">
                Администратор
              </span>
            </>
          ) : (
            <>
              <UserCog className="w-4 h-4 text-blue-500" />
              <span className="px-2 py-1 text-xs font-semibold text-blue-700 bg-blue-100 rounded-full">
                Менеджер
              </span>
            </>
          )}
        </div>
      ),
    },
    {
      key: 'is_active',
      label: 'Статус',
      sortable: true,
      render: (value: boolean) => (
        <span
          className={`px-2 py-1 text-xs font-semibold rounded-full ${
            value
              ? 'text-green-700 bg-green-100'
              : 'text-red-700 bg-red-100'
          }`}
        >
          {value ? 'Активен' : 'Неактивен'}
        </span>
      ),
    },
    {
      key: 'created_at',
      label: 'Создан',
      sortable: true,
      render: (value: string) => (
        <div className="text-sm text-gray-500">
          {new Date(value).toLocaleDateString('ru-RU')}
        </div>
      ),
    },
    {
      key: 'actions',
      label: 'Действия',
      render: (_: any, user: AdminUser) => (
        <div className="flex space-x-2">
          {user.role === UserRole.MANAGER && (
            <button
              onClick={() => handleManageAccess(user)}
              className="p-1 text-blue-600 hover:text-blue-800 transition-colors"
              title="Управление доступом к чатам"
            >
              <Settings className="w-4 h-4" />
            </button>
          )}
          {currentUser?.id !== user.id && (
            <button
              onClick={() => handleDelete(user)}
              className="p-1 text-red-600 hover:text-red-800 transition-colors"
              title="Удалить"
              disabled={deleteAdmin.isPending}
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900">
            Управление пользователями
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Администраторы и менеджеры системы
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Создать пользователя</span>
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-2 text-gray-700">
            <Users className="w-5 h-5" />
            <h2 className="text-lg font-semibold">
              Пользователи ({users.length})
            </h2>
          </div>
        </div>

        <DataTable
          data={users}
          columns={columns}
        />
      </div>

      {isCreateModalOpen && (
        <CreateManagerModal
          onClose={() => setIsCreateModalOpen(false)}
        />
      )}

      {isAccessModalOpen && selectedManager && (
        <ManageChatAccessModal
          manager={selectedManager}
          onClose={() => {
            setIsAccessModalOpen(false);
            setSelectedManager(null);
          }}
        />
      )}
    </div>
  );
};
