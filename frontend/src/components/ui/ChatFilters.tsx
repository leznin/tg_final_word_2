import React from 'react';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';

export interface ChatFilters {
  chatType: 'all' | 'group' | 'supergroup' | 'channel';
  hasLinkedChannel: 'all' | 'with_channel' | 'without_channel';
  hasModerators: 'all' | 'with_moderators' | 'without_moderators';
  deleteMessages: 'all' | 'enabled' | 'disabled';
  botPermissions: 'all' | 'admin' | 'limited' | 'none';
  dateFrom: string;
  dateTo: string;
}

interface ChatFiltersProps {
  filters: ChatFilters;
  onFiltersChange: (filters: ChatFilters) => void;
  isExpanded: boolean;
  onToggleExpanded: () => void;
}

export const ChatFilters: React.FC<ChatFiltersProps> = ({
  filters,
  onFiltersChange,
  isExpanded,
  onToggleExpanded
}) => {
  const updateFilter = <K extends keyof ChatFilters>(key: K, value: ChatFilters[K]) => {
    onFiltersChange({
      ...filters,
      [key]: value
    });
  };

  const resetFilters = () => {
    onFiltersChange({
      chatType: 'all',
      hasLinkedChannel: 'all',
      hasModerators: 'all',
      deleteMessages: 'all',
      botPermissions: 'all',
      dateFrom: '',
      dateTo: ''
    });
  };

  const hasActiveFilters = () => {
    return filters.chatType !== 'all' ||
           filters.hasLinkedChannel !== 'all' ||
           filters.hasModerators !== 'all' ||
           filters.deleteMessages !== 'all' ||
           filters.botPermissions !== 'all' ||
           filters.dateFrom !== '' ||
           filters.dateTo !== '';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div
        className="px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={onToggleExpanded}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Filter className="h-5 w-5 text-gray-500" />
            <h3 className="text-lg font-medium text-gray-900">Фильтры</h3>
            {hasActiveFilters() && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                Активны
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {hasActiveFilters() && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  resetFilters();
                }}
                className="text-sm text-gray-500 hover:text-gray-700 flex items-center space-x-1"
              >
                <X className="h-4 w-4" />
                <span>Сбросить</span>
              </button>
            )}
            {isExpanded ? (
              <ChevronUp className="h-5 w-5 text-gray-400" />
            ) : (
              <ChevronDown className="h-5 w-5 text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-6 pb-6 border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Chat Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Тип чата
              </label>
              <select
                value={filters.chatType}
                onChange={(e) => updateFilter('chatType', e.target.value as ChatFilters['chatType'])}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все типы</option>
                <option value="group">Группа</option>
                <option value="supergroup">Супергруппа</option>
                <option value="channel">Канал</option>
              </select>
            </div>

            {/* Linked Channel Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Привязанный канал
              </label>
              <select
                value={filters.hasLinkedChannel}
                onChange={(e) => updateFilter('hasLinkedChannel', e.target.value as ChatFilters['hasLinkedChannel'])}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все чаты</option>
                <option value="with_channel">Только с каналом</option>
                <option value="without_channel">Без канала</option>
              </select>
            </div>

            {/* Moderators Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Модераторы
              </label>
              <select
                value={filters.hasModerators}
                onChange={(e) => updateFilter('hasModerators', e.target.value as ChatFilters['hasModerators'])}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все чаты</option>
                <option value="with_moderators">С модераторами</option>
                <option value="without_moderators">Без модераторов</option>
              </select>
            </div>

            {/* Delete Messages Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Удаление сообщений
              </label>
              <select
                value={filters.deleteMessages}
                onChange={(e) => updateFilter('deleteMessages', e.target.value as ChatFilters['deleteMessages'])}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все</option>
                <option value="enabled">Включено</option>
                <option value="disabled">Отключено</option>
              </select>
            </div>

            {/* Bot Permissions Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Права бота
              </label>
              <select
                value={filters.botPermissions}
                onChange={(e) => updateFilter('botPermissions', e.target.value as ChatFilters['botPermissions'])}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">Все</option>
                <option value="admin">Администратор</option>
                <option value="limited">Ограниченные</option>
                <option value="none">Нет прав</option>
              </select>
            </div>

            {/* Date Range Filters */}
            <div className="md:col-span-2 lg:col-span-3">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Дата добавления
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">От</label>
                  <input
                    type="date"
                    value={filters.dateFrom}
                    onChange={(e) => updateFilter('dateFrom', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">До</label>
                  <input
                    type="date"
                    value={filters.dateTo}
                    onChange={(e) => updateFilter('dateTo', e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
