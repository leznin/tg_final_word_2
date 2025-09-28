import React, { useState, useMemo } from 'react';
import { Search, Users, MessageSquare, Hash, Radio, ArrowUp, ArrowDown } from 'lucide-react';
import { useUsersWithChats } from '../hooks/useUsersWithChats';
import { UserChatsGroup } from '../components/ui/UserChatsGroup';
import { Loading } from '../components/ui/Loading';
import { UserWithChats } from '../types';

interface Filters {
  searchTerm: string;
  showAdminsOnly: boolean;
  showWithChatsOnly: boolean;
  showWithChannelsOnly: boolean;
  sortBy: 'name' | 'chats' | 'channels' | 'created';
  sortOrder: 'asc' | 'desc';
}

export const UsersChats: React.FC = () => {
  const { data, isLoading } = useUsersWithChats();
  const [filters, setFilters] = useState<Filters>({
    searchTerm: '',
    showAdminsOnly: false,
    showWithChatsOnly: false,
    showWithChannelsOnly: false,
    sortBy: 'name',
    sortOrder: 'asc',
  });

  const users = data || [];

  // Фильтрация и сортировка пользователей
  const filteredUsers = useMemo(() => {
    let filtered = users.filter(user => {
      // Поиск по имени, username
      const matchesSearch = filters.searchTerm === '' ||
        user.first_name?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        user.last_name?.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
        user.username?.toLowerCase().includes(filters.searchTerm.toLowerCase());

      // Только администраторы
      const matchesAdmin = !filters.showAdminsOnly || user.is_admin;

      // Только с чатами
      const matchesChats = !filters.showWithChatsOnly || user.chats.length > 0;

      // Только с каналами
      const matchesChannels = !filters.showWithChannelsOnly ||
        user.chats.some(chat => chat.chat_type === 'channel' || chat.linked_channel_info);

      return matchesSearch && matchesAdmin && matchesChats && matchesChannels;
    });

    // Сортировка
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (filters.sortBy) {
        case 'name':
          aValue = `${a.first_name || ''} ${a.last_name || ''}`.trim().toLowerCase();
          bValue = `${b.first_name || ''} ${b.last_name || ''}`.trim().toLowerCase();
          break;
        case 'chats':
          aValue = a.chats.length;
          bValue = b.chats.length;
          break;
        case 'channels':
          aValue = a.chats.filter(chat => chat.chat_type === 'channel' || chat.linked_channel_info).length;
          bValue = b.chats.filter(chat => chat.chat_type === 'channel' || chat.linked_channel_info).length;
          break;
        case 'created':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return filters.sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return filters.sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [users, filters]);

  // Статистика
  const stats = useMemo(() => {
    const totalUsers = users.length;
    const totalChats = users.reduce((sum, user) => sum + user.chats.length, 0);
    const totalChannels = users.reduce((sum, user) =>
      sum + user.chats.filter(chat => chat.chat_type === 'channel').length, 0);
    const totalLinkedChannels = users.reduce((sum, user) =>
      sum + user.chats.filter(chat => chat.linked_channel_info).length, 0);

    return { totalUsers, totalChats, totalChannels, totalLinkedChannels };
  }, [users]);

  const updateFilter = <K extends keyof Filters>(key: K, value: Filters[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      {/* Заголовок и статистика */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Пользователи и их чаты</h1>
          <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <Users className="h-4 w-4" />
              <span>{stats.totalUsers} пользовател{stats.totalUsers !== 1 ? 'ей' : 'ь'}</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageSquare className="h-4 w-4" />
              <span>{stats.totalChats} чат{stats.totalChats !== 1 ? 'ов' : ''}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Radio className="h-4 w-4" />
              <span>{stats.totalChannels} канал{stats.totalChannels !== 1 ? 'ов' : ''}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Hash className="h-4 w-4" />
              <span>{stats.totalLinkedChannels} привяз{stats.totalLinkedChannels !== 1 ? 'ок' : 'ка'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Фильтры и поиск */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Поиск */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Поиск по имени или username..."
                value={filters.searchTerm}
                onChange={(e) => updateFilter('searchTerm', e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
                  </div>
                </div>

          {/* Чекбоксы фильтров */}
          <div className="flex flex-wrap gap-4 items-center">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.showAdminsOnly}
                onChange={(e) => updateFilter('showAdminsOnly', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Только администраторы</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.showWithChatsOnly}
                onChange={(e) => updateFilter('showWithChatsOnly', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Только с чатами</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={filters.showWithChannelsOnly}
                onChange={(e) => updateFilter('showWithChannelsOnly', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Только с каналами</span>
            </label>
          </div>

          {/* Сортировка */}
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-700">Сортировка:</span>
            <select
              value={filters.sortBy}
              onChange={(e) => updateFilter('sortBy', e.target.value as Filters['sortBy'])}
              className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="name">По имени</option>
              <option value="chats">По чатам</option>
              <option value="channels">По каналам</option>
              <option value="created">По дате</option>
            </select>
            <button
              onClick={() => updateFilter('sortOrder', filters.sortOrder === 'asc' ? 'desc' : 'asc')}
              className="p-1 hover:bg-gray-100 rounded"
              title={filters.sortOrder === 'asc' ? 'По возрастанию' : 'По убыванию'}
            >
              {filters.sortOrder === 'asc' ? (
                <ArrowUp className="h-4 w-4 text-gray-600" />
              ) : (
                <ArrowDown className="h-4 w-4 text-gray-600" />
              )}
            </button>
          </div>
            </div>

        {/* Показать активные фильтры */}
        {(filters.searchTerm || filters.showAdminsOnly || filters.showWithChatsOnly || filters.showWithChannelsOnly) && (
          <div className="mt-3 text-xs text-gray-500">
            Найдено: {filteredUsers.length} пользовател{filteredUsers.length !== 1 ? 'ей' : 'ь'}
          </div>
        )}
      </div>

      {/* Список пользователей с их чатами */}
      <div className="space-y-6">
        {filteredUsers.length > 0 ? (
          filteredUsers.map((user) => (
            <UserChatsGroup key={user.id} user={user} />
          ))
        ) : (
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                {users.length === 0 ? 'Нет пользователей' : 'Нет пользователей по фильтру'}
              </h3>
            <p className="mt-1 text-sm text-gray-500">
                {users.length === 0
                  ? 'В системе ещё нет зарегистрированных пользователей.'
                  : 'Попробуйте изменить критерии поиска или фильтры.'
                }
            </p>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};
