import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Calendar, Settings, Hash, Radio, User, Users, Info, RefreshCw, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { useChats } from '../hooks/useChats';
import { useGetAllChatsInfo } from '../hooks/useChatInfo';
import { ChatCard } from '../components/ui/ChatCard';
import { ChatFilters } from '../components/ui/ChatFilters';
import { Loading } from '../components/ui/Loading';
import { Chat } from '../types';

export const Chats: React.FC = () => {
  const navigate = useNavigate();
  const { data, isLoading } = useChats();
  const getAllChatsInfo = useGetAllChatsInfo();

  const [filters, setFilters] = useState<ChatFilters>({
    chatType: 'all',
    hasLinkedChannel: 'all',
    hasModerators: 'all',
    deleteMessages: 'all',
    botPermissions: 'all',
    dateFrom: '',
    dateTo: ''
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [isFiltersExpanded, setIsFiltersExpanded] = useState(false);

  const itemsPerPage = 12;

  const chats = data?.chats || [];

  // Фильтрация и поиск
  const filteredChats = useMemo(() => {
    return chats.filter(chat => {
      // Поиск по названию и ID
      const matchesSearch = searchTerm === '' ||
        String(chat.telegram_chat_id).includes(searchTerm.toLowerCase()) ||
        (chat.title && chat.title.toLowerCase().includes(searchTerm.toLowerCase()));

      // Фильтр по типу чата
      const matchesType = filters.chatType === 'all' || chat.chat_type === filters.chatType;

      // Фильтр по привязанному каналу
      const matchesLinkedChannel =
        filters.hasLinkedChannel === 'all' ||
        (filters.hasLinkedChannel === 'with_channel' && chat.linked_channel_info) ||
        (filters.hasLinkedChannel === 'without_channel' && !chat.linked_channel_info);

      // Фильтр по модераторам
      const matchesModerators =
        filters.hasModerators === 'all' ||
        (filters.hasModerators === 'with_moderators' && chat.chat_moderators && chat.chat_moderators.length > 0) ||
        (filters.hasModerators === 'without_moderators' && (!chat.chat_moderators || chat.chat_moderators.length === 0));

      // Фильтр по удалению сообщений
      const matchesDeleteMessages =
        filters.deleteMessages === 'all' ||
        (filters.deleteMessages === 'enabled' && chat.delete_messages_enabled) ||
        (filters.deleteMessages === 'disabled' && !chat.delete_messages_enabled);

      // Фильтр по правам бота
      const matchesBotPermissions = (() => {
        if (filters.botPermissions === 'all') return true;
        if (!chat.last_info_update) return filters.botPermissions === 'none';
        if (!chat.bot_permissions) return filters.botPermissions === 'none';

        const hasAdminRights = chat.bot_permissions.can_delete_messages ||
                              chat.bot_permissions.can_restrict_members ||
                              chat.bot_permissions.can_promote_members;

        if (filters.botPermissions === 'admin') return hasAdminRights;
        if (filters.botPermissions === 'limited') return !hasAdminRights;
        if (filters.botPermissions === 'none') return false;

        return true;
      })();

      // Фильтр по дате
      const chatDate = new Date(chat.added_at);
      const matchesDateFrom = !filters.dateFrom || chatDate >= new Date(filters.dateFrom);
      const matchesDateTo = !filters.dateTo || chatDate <= new Date(filters.dateTo + 'T23:59:59');

      return matchesSearch && matchesType && matchesLinkedChannel && matchesModerators &&
             matchesDeleteMessages && matchesBotPermissions && matchesDateFrom && matchesDateTo;
    });
  }, [chats, searchTerm, filters]);

  // Пагинация
  const totalPages = Math.ceil(filteredChats.length / itemsPerPage);
  const paginatedChats = filteredChats.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleGetChatInfo = async () => {
    try {
      const result = await getAllChatsInfo.mutateAsync();

      // Show results notification
      if (result.successful_requests > 0) {
        alert(`✅ Информация успешно получена для ${result.successful_requests} из ${result.total_chats} чатов${result.failed_requests > 0 ? `\n❌ Ошибки в ${result.failed_requests} чатах` : ''}`);
      } else {
        alert('❌ Не удалось получить информацию ни для одного чата');
      }

      if (result.errors && result.errors.length > 0) {
        console.warn('Chat info errors:', result.errors);
      }
    } catch (error) {
      console.error('Failed to get chat information:', error);
      alert('❌ Произошла ошибка при получении информации о чатах');
    }
  };

  const resetFilters = () => {
    setFilters({
      chatType: 'all',
      hasLinkedChannel: 'all',
      hasModerators: 'all',
      deleteMessages: 'all',
      botPermissions: 'all',
      dateFrom: '',
      dateTo: ''
    });
    setSearchTerm('');
    setCurrentPage(1);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Управление чатами</h1>
          <p className="mt-2 text-sm text-gray-600">
            Всего чатов: {chats.length} | Показано: {filteredChats.length}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={handleGetChatInfo}
            disabled={getAllChatsInfo.isPending}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {getAllChatsInfo.isPending ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Info className="h-4 w-4 mr-2" />
            )}
            {getAllChatsInfo.isPending ? 'Получение информации...' : 'Получить информацию о чатах'}
          </button>
        </div>
      </div>

      {/* Фильтры */}
      <ChatFilters
        filters={filters}
        onFiltersChange={setFilters}
        isExpanded={isFiltersExpanded}
        onToggleExpanded={() => setIsFiltersExpanded(!isFiltersExpanded)}
      />

      {/* Поиск */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Поиск по названию или ID чата..."
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1); // Сброс пагинации при поиске
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Сетка карточек */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {paginatedChats.map((chat) => (
          <ChatCard
            key={chat.id}
            chat={chat}
            onClick={() => navigate(`/chats/${chat.telegram_chat_id}`)}
          />
        ))}
      </div>

      {/* Пагинация */}
      {totalPages > 1 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Показано {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredChats.length)} из {filteredChats.length}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-sm text-gray-700">
                {currentPage} из {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="p-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Пустое состояние */}
      {filteredChats.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm p-12">
          <div className="text-center">
            <MessageSquare className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              {chats.length === 0 ? 'Нет чатов' : 'Чаты не найдены'}
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              {chats.length === 0
                ? 'В системе ещё нет добавленных чатов.'
                : 'Попробуйте изменить фильтры или поисковый запрос.'
              }
            </p>
            {filteredChats.length !== chats.length && (
              <button
                onClick={resetFilters}
                className="mt-4 text-sm text-blue-600 hover:text-blue-500"
              >
                Сбросить все фильтры
              </button>
            )}
          </div>
        </div>
      )}

      {/* Статистика */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Статистика по чатам</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {filteredChats.length}
            </div>
            <div className="text-sm text-blue-800">Показанных чатов</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {filteredChats.filter(c => c.chat_type === 'group').length}
            </div>
            <div className="text-sm text-green-800">Групп</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {filteredChats.filter(c => c.chat_type === 'supergroup').length}
            </div>
            <div className="text-sm text-purple-800">Супергрупп</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {filteredChats.filter(c => c.linked_channel_info).length}
            </div>
            <div className="text-sm text-orange-800">С привязанными каналами</div>
          </div>
        </div>
      </div>
    </div>
  );
};