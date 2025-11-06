import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Radio, Settings, Calendar, User, Unlink, Plus, Trash2, Clock, FileText, ExternalLink, Search, ChevronLeft, ChevronRight, ChevronDown, ChevronUp, History, Shield, CreditCard, MessagesSquare } from 'lucide-react';
import { useChatDetail, useAvailableChannels, useLinkChannel, useUnlinkChannel, useChatModerators, useRemoveModerator, useChatMembers, useChatSubscriptionStatus, useCreateChatSubscription, useDeactivateChatSubscription } from '../hooks/useChats';
import { Loading } from '../components/ui/Loading';
import { Select } from '../components/ui/Select';
import { ChatPostsList } from '../components/chat/ChatPostsList';
import { CreatePostModal } from '../components/modals/CreatePostModal';

type TabType = 'overview' | 'management' | 'members' | 'posts';

export const ChatDetail: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { data, isLoading } = useChatDetail(chatId!);
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [showChannelSelector, setShowChannelSelector] = useState(false);
  const [showSubscriptionForm, setShowSubscriptionForm] = useState(false);
  const [showCreatePostModal, setShowCreatePostModal] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['info']));
  const [subscriptionForm, setSubscriptionForm] = useState({
    subscription_type: 'month' as 'month' | 'year',
    price_stars: 1,
    currency: 'XTR',
    end_date: ''
  });

  // Chat members search and pagination state
  const [memberSearch, setMemberSearch] = useState('');
  const [memberPage, setMemberPage] = useState(1);
  const [memberPageSize] = useState(30);
  const [expandedMembers, setExpandedMembers] = useState<Set<number>>(new Set());

  // Reset page when search changes
  useEffect(() => {
    setMemberPage(1);
  }, [memberSearch]);

  const toggleMemberExpanded = (memberId: number) => {
    setExpandedMembers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(memberId)) {
        newSet.delete(memberId);
      } else {
        newSet.add(memberId);
      }
      return newSet;
    });
  };

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  // Hooks for channel linking
  const { data: availableChannels } = useAvailableChannels(data?.chat.admin_user_id || 0);
  const linkChannelMutation = useLinkChannel();
  const unlinkChannelMutation = useUnlinkChannel();

  // Hooks for moderators
  const { data: moderatorsData } = useChatModerators(chatId!);
  const removeModeratorMutation = useRemoveModerator();

  // Hooks for chat members
  const { data: membersData, isLoading: membersLoading } = useChatMembers(chatId!, memberSearch, memberPage, memberPageSize);

  // Hook for chat subscription status
  const { data: subscriptionStatus } = useChatSubscriptionStatus(chatId!);

  // Hooks for subscription management
  const createSubscriptionMutation = useCreateChatSubscription();
  const deactivateSubscriptionMutation = useDeactivateChatSubscription();

  if (isLoading) return <Loading />;
  if (!data) return <div>Чат не найден</div>;

  const { chat, moderators, channels } = data;

  const handleLinkChannel = async (channelId: number) => {
    try {
      await linkChannelMutation.mutateAsync({ chatId: chat.id, channelId });
      setShowChannelSelector(false);
    } catch (error) {
      console.error('Failed to link channel:', error);
    }
  };

  const handleUnlinkChannel = async () => {
    try {
      await unlinkChannelMutation.mutateAsync(chat.id);
    } catch (error) {
      console.error('Failed to unlink channel:', error);
    }
  };

  const handleRemoveModerator = async (moderatorId: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этого модератора?')) {
      try {
        await removeModeratorMutation.mutateAsync(moderatorId);
      } catch (error) {
        console.error('Failed to remove moderator:', error);
        alert('Не удалось удалить модератора');
      }
    }
  };

  const handleCreateSubscription = async () => {
    try {
      const subscriptionData = {
        chat_id: chat.id,
        subscription_type: subscriptionForm.subscription_type,
        price_stars: subscriptionForm.price_stars,
        currency: subscriptionForm.currency,
        start_date: new Date(),
        end_date: new Date(subscriptionForm.end_date),
        is_active: true
      };

      await createSubscriptionMutation.mutateAsync(subscriptionData);
      setShowSubscriptionForm(false);
      setSubscriptionForm({
        subscription_type: 'month',
        price_stars: 1,
        currency: 'XTR',
        end_date: ''
      });
      alert('Подписка успешно создана!');
    } catch (error) {
      console.error('Failed to create subscription:', error);
      alert('Не удалось создать подписку');
    }
  };

  const handleDeactivateSubscription = async (subscriptionId: number) => {
    if (window.confirm('Вы уверены, что хотите деактивировать эту подписку?')) {
      try {
        await deactivateSubscriptionMutation.mutateAsync(subscriptionId);
        alert('Подписка успешно деактивирована!');
      } catch (error) {
        console.error('Failed to deactivate subscription:', error);
        alert('Не удалось деактивировать подписку');
      }
    }
  };

  const statsCards = [
    {
      title: 'Модераторы',
      value: moderatorsData?.length || moderators.length,
      icon: Shield,
      color: 'purple'
    },
    {
      title: 'Участники',
      value: chat.member_count || membersData?.total || 0,
      icon: Users,
      color: 'green'
    },
    {
      title: 'Каналы',
      value: channels.length,
      icon: Radio,
      color: 'blue'
    },
    {
      title: 'Время ред.',
      value: `${chat.max_edit_time_minutes}м`,
      icon: Clock,
      color: 'orange'
    }
  ];

  const tabs = [
    { id: 'overview' as TabType, label: 'Обзор', icon: FileText },
    { id: 'management' as TabType, label: 'Управление', icon: Settings },
    { id: 'members' as TabType, label: 'Участники', icon: Users },
    { id: 'posts' as TabType, label: 'Посты', icon: MessagesSquare }
  ];

  return (
    <div className="space-y-4">
      {/* Заголовок */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate('/chats')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-all"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">{chat.chat_title}</h1>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-sm text-gray-600 font-mono">ID: {chat.chat_id}</span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  chat.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  {chat.is_active ? 'Активен' : 'Неактивен'}
                </span>
                <span className="text-sm text-gray-500">
                  <Calendar className="h-3.5 w-3.5 inline mr-1" />
                  {new Date(chat.added_date).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Объединённый блок: Метрики + Информация о чате */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
        {/* Метрики */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {statsCards.map((stat, index) => (
            <div key={index} className="bg-gradient-to-r from-white to-gray-50 rounded-lg p-3 border border-gray-100 hover:shadow-md transition-all">
              <div className="flex items-center space-x-2">
                <div className={`p-2 rounded-lg bg-${stat.color}-100`}>
                  <stat.icon className={`h-4 w-4 text-${stat.color}-600`} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-gray-600">{stat.title}</p>
                  <p className="text-lg font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Информация о чате в том же блоке */}
        {(chat.description || chat.invite_link || chat.last_info_update) && (
          <div className="border-t border-gray-100 pt-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {chat.description && (
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200">
                  <div className="flex items-start space-x-2">
                    <FileText className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-blue-900 mb-1">Описание</h4>
                      <p className="text-xs text-blue-800 line-clamp-2">{chat.description}</p>
                    </div>
                  </div>
                </div>
              )}

              {chat.invite_link && (
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 border border-green-200">
                  <div className="flex items-start space-x-2">
                    <ExternalLink className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-green-900 mb-1">Ссылка</h4>
                      <a
                        href={chat.invite_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-green-700 hover:text-green-900 hover:underline block truncate"
                        title={chat.invite_link}
                      >
                        {chat.invite_link}
                      </a>
                    </div>
                  </div>
                </div>
              )}

              {chat.last_info_update && (
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200">
                  <div className="flex items-start space-x-2">
                    <Calendar className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-semibold text-purple-900 mb-1">Обновлено</h4>
                      <p className="text-xs text-purple-800">
                        {new Date(chat.last_info_update).toLocaleDateString('ru-RU', {
                          day: 'numeric',
                          month: 'short',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Статусы */}
        <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-100">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            chat.delete_messages_enabled ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
          }`}>
            Удаление сообщений: {chat.delete_messages_enabled ? 'Включено' : 'Отключено'}
          </span>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-100 text-green-800' :
            (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            AI проверка: {
              (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Активна' :
              (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата' :
              'Отключена'
            }
          </span>
        </div>
      </div>

      {/* Объединённый блок: AI проверка + Управление подпиской */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-blue-500 bg-opacity-20">
            <Settings className="h-5 w-5 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">AI проверка и подписка</h3>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* AI проверка контента */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-green-50 to-green-100">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-900">Статус AI проверки</h4>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-200 text-green-900' :
                (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-200 text-yellow-900' :
                'bg-gray-200 text-gray-900'
              }`}>
                {(subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Активна' :
                 (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата' :
                 'Отключена'}
              </span>
            </div>

            <div className="flex items-center space-x-2 mb-2">
              <div className={`w-3 h-3 rounded-full ${
                (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-500' :
                (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-500' :
                'bg-gray-400'
              }`} />
              <span className="text-sm font-medium text-gray-900">
                {chat.ai_content_check_enabled ? 'Включена' : 'Отключена'}
              </span>
            </div>

            <p className="text-sm text-gray-700">
              {(subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Подписка активна, проверка сообщений работает' :
               (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Требуется оплата подписки для работы AI проверки' :
               'Функция отключена администратором'}
            </p>
          </div>

          {/* Управление подпиской */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-blue-50 to-blue-100">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-900">Управление подпиской</h4>
              {!chat.active_subscription && (
                <button
                  onClick={() => setShowSubscriptionForm(!showSubscriptionForm)}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-all"
                >
                  <Plus className="h-4 w-4 inline mr-1" />
                  Создать
                </button>
              )}
            </div>

            {chat.active_subscription ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="text-sm font-medium text-gray-900">Подписка активна</span>
                  </div>
                  <button
                    onClick={() => handleDeactivateSubscription(chat.active_subscription!.id)}
                    disabled={deactivateSubscriptionMutation.isPending}
                    className="px-2 py-1 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-all disabled:opacity-50"
                  >
                    Деактивировать
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-white rounded-lg p-2 border border-blue-200">
                    <div className="text-gray-600 text-xs">Стоимость</div>
                    <div className="font-medium text-gray-900">{chat.active_subscription.price_stars} ⭐</div>
                  </div>
                  <div className="bg-white rounded-lg p-2 border border-blue-200">
                    <div className="text-gray-600 text-xs">Тип</div>
                    <div className="font-medium text-gray-900">
                      {chat.active_subscription.subscription_type === 'month' ? 'Месяц' : 'Год'}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-2 border border-blue-200">
                    <div className="text-gray-600 text-xs">Начало</div>
                    <div className="font-medium text-gray-900 text-sm">
                      {new Date(chat.active_subscription.start_date).toLocaleDateString('ru-RU')}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-2 border border-blue-200">
                    <div className="text-gray-600 text-xs">Окончание</div>
                    <div className={`font-medium text-sm ${new Date(chat.active_subscription.end_date) < new Date() ? 'text-red-600' : 'text-green-600'}`}>
                      {new Date(chat.active_subscription.end_date).toLocaleDateString('ru-RU')}
                      {new Date(chat.active_subscription.end_date) < new Date() && (
                        <span className="block text-red-500 text-xs">(истекла)</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                  <span className="text-sm font-medium text-gray-900">Нет активной подписки</span>
                </div>
                <p className="text-sm text-gray-700">Чат не имеет платной подписки на AI проверку</p>
              </div>
            )}

            {/* Форма создания подписки */}
            {showSubscriptionForm && (
              <div className="mt-4 pt-4 border-t border-blue-200">
                <h5 className="text-sm font-medium text-gray-900 mb-3">Создать подписку</h5>
                <div className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <Select
                      label="Тип"
                      value={subscriptionForm.subscription_type}
                      onChange={(e) => setSubscriptionForm(prev => ({
                        ...prev,
                        subscription_type: e.target.value as 'month' | 'year'
                      }))}
                      icon={<Calendar className="w-4 h-4" />}
                    >
                      <option value="month">Месяц</option>
                      <option value="year">Год</option>
                    </Select>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">Стоимость (⭐)</label>
                      <input
                        type="number"
                        min="1"
                        value={subscriptionForm.price_stars}
                        onChange={(e) => setSubscriptionForm(prev => ({
                          ...prev,
                          price_stars: parseInt(e.target.value) || 1
                        }))}
                        className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 mb-1">Дата окончания</label>
                    <input
                      type="datetime-local"
                      value={subscriptionForm.end_date}
                      onChange={(e) => setSubscriptionForm(prev => ({
                        ...prev,
                        end_date: e.target.value
                      }))}
                      className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                  <button
                    onClick={() => setShowSubscriptionForm(false)}
                    className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Отмена
                  </button>
                  <button
                    onClick={handleCreateSubscription}
                    disabled={createSubscriptionMutation.isPending || !subscriptionForm.end_date}
                    className="px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createSubscriptionMutation.isPending ? 'Создание...' : 'Создать'}
                  </button>
                </div>
              </div>
            </div>
          )}
          </div>
        </div>
      </div>

      {/* Объединённый блок: Модераторы + Привязанный канал */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Модераторы и Привязанный канал */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
          <div className="flex items-center space-x-2 mb-4">
            <div className="p-2 rounded-lg bg-purple-100">
              <Users className="h-5 w-5 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Модераторы и каналы</h3>
          </div>

          {/* Модераторы */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-700">Модераторы</h4>
              <span className="text-xs text-gray-500 bg-purple-50 px-2 py-1 rounded-full font-medium">
                {moderatorsData?.length || moderators.length}
              </span>
            </div>

            {(moderatorsData || moderators).length > 0 ? (
              <div className="grid grid-cols-1 gap-2">
                {(moderatorsData || moderators).map((moderator) => (
                  <div key={moderator.id} className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-3 border border-purple-200 hover:shadow-md transition-all">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 flex-1 min-w-0">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-purple-200 rounded-full flex items-center justify-center">
                            <User className="w-4 h-4 text-purple-700" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-sm font-medium text-purple-900 truncate">
                            {'moderator_name' in moderator ? moderator.moderator_name : `${moderator.first_name || ''} ${moderator.last_name || ''}`.trim() || `Пользователь ${moderator.moderator_user_id}`}
                          </h4>
                          <div className="flex items-center space-x-2 mt-0.5">
                            <span className="text-xs text-purple-700 font-mono">
                              ID: {moderator.moderator_user_id}
                            </span>
                            {('moderator_username' in moderator ? moderator.moderator_username : moderator.username) && (
                              <a
                                href={`https://t.me/${'moderator_username' in moderator ? moderator.moderator_username : moderator.username}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-purple-600 hover:text-purple-800 hover:underline truncate"
                              >
                                @{'moderator_username' in moderator ? moderator.moderator_username : moderator.username}
                              </a>
                            )}
                          </div>
                        </div>
                      </div>
                      <button
                        onClick={() => handleRemoveModerator(moderator.id)}
                        disabled={removeModeratorMutation.isPending}
                        className="text-red-500 hover:text-red-700 disabled:opacity-50 p-1.5 rounded hover:bg-red-50 transition-all ml-2"
                        title="Удалить модератора"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-4 bg-gray-50 rounded-lg">
                <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Модераторы не назначены</p>
              </div>
            )}
          </div>

          {/* Разделитель */}
          <div className="border-t border-gray-200 my-4"></div>

          {/* Привязанный канал */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-semibold text-gray-700">Привязанный канал</h4>
              {!chat.linked_channel && (
                <button
                  onClick={() => setShowChannelSelector(!showChannelSelector)}
                  className="px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-all"
                >
                  <Plus className="h-4 w-4 inline mr-1" />
                  Привязать
                </button>
              )}
            </div>

            {chat.linked_channel ? (
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-3 border border-blue-200 hover:shadow-md transition-all">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-200 rounded-full flex items-center justify-center">
                        <Radio className="w-4 h-4 text-blue-700" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-blue-900 truncate">
                        {chat.linked_channel.title || `Канал ${chat.linked_channel.telegram_chat_id}`}
                      </h4>
                      <div className="flex items-center space-x-2 mt-0.5">
                        <span className="text-xs text-blue-700 font-mono">
                          ID: {chat.linked_channel.telegram_chat_id}
                        </span>
                        {chat.linked_channel.username && (
                          <a
                            href={`https://t.me/${chat.linked_channel.username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            @{chat.linked_channel.username}
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={handleUnlinkChannel}
                    disabled={unlinkChannelMutation.isPending}
                    className="text-red-500 hover:text-red-700 disabled:opacity-50 p-1.5 rounded hover:bg-red-50 transition-all ml-2"
                    title="Отвязать канал"
                  >
                    <Unlink className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 bg-gray-50 rounded-lg">
                <Radio className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">Канал не привязан</p>
              </div>
            )}

            {/* Селектор каналов */}
            {showChannelSelector && availableChannels && availableChannels.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <h5 className="text-sm font-medium text-gray-900 mb-2">Выберите канал для привязки:</h5>
                <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto">
                  {availableChannels.map((channel) => (
                    <div
                      key={channel.id}
                      className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-2 border border-green-200 hover:shadow-md hover:from-green-100 hover:to-green-200 cursor-pointer transition-all"
                      onClick={() => handleLinkChannel(channel.id)}
                    >
                      <div className="flex items-center space-x-2">
                        <Radio className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-green-900 truncate">
                            {channel.title || `Канал ${channel.telegram_chat_id}`}
                          </div>
                          <div className="text-xs text-green-700 font-mono">
                            ID: {channel.telegram_chat_id}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-2">
                  <button
                    onClick={() => setShowChannelSelector(false)}
                    className="px-2 py-0.5 text-xs text-gray-600 hover:text-gray-800"
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}

            {showChannelSelector && (!availableChannels || availableChannels.length === 0) && (
              <div className="mt-3 pt-3 border-t border-gray-100">
                <p className="text-xs text-gray-500 text-center py-3">
                  Нет доступных каналов. Добавьте бота как администратора в канал.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Правая колонка - Участники */}
        <div className="space-y-3">
          <div className="bg-white rounded-lg shadow border border-gray-100 p-3 hover:shadow-md transition-all">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 rounded bg-green-100">
                  <Users className="h-3.5 w-3.5 text-green-600" />
                </div>
                <h3 className="text-sm font-semibold text-gray-900">Участники</h3>
                <span className="text-xs text-gray-500 bg-green-50 px-1.5 py-0.5 rounded-full">
                  {membersData?.total || 0}
                </span>
              </div>
            </div>

            {/* Search field */}
            <div className="mb-3">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск по имени, username или ID..."
                  value={memberSearch}
                  onChange={(e) => setMemberSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {membersLoading ? (
              <div className="flex justify-center py-4">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-green-600"></div>
              </div>
            ) : membersData && membersData.members && membersData.members.length > 0 ? (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 max-h-80 overflow-y-auto">
                  {membersData.members.map((member) => {
                    const isExpanded = expandedMembers.has(member.id);
                    return (
                      <div key={member.id} className="bg-gradient-to-r from-green-50 to-green-100 rounded border border-green-200 hover:shadow hover:from-green-100 hover:to-green-200 transition-all">
                        <div className="p-2">
                          <div className="flex items-start space-x-1.5">
                            <div className="flex-shrink-0">
                              {member.is_bot ? (
                                <div className="w-5 h-5 bg-red-200 rounded-full flex items-center justify-center">
                                  <Settings className="w-2.5 h-2.5 text-red-700" />
                                </div>
                              ) : (
                                <div className="w-5 h-5 bg-green-200 rounded-full flex items-center justify-center">
                                  <User className="w-2.5 h-2.5 text-green-700" />
                                </div>
                              )}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between mb-0.5">
                                <div className="flex items-center space-x-1 flex-1 min-w-0">
                                  <h4 className="text-xs font-medium text-green-900 truncate">
                                    {member.first_name || ''} {member.last_name || ''} {!member.first_name && !member.last_name && `ID: ${member.telegram_user_id}`}
                                  </h4>
                                  {member.is_bot && (
                                    <span className="inline-flex items-center px-1 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                      Бот
                                    </span>
                                  )}
                                  {member.is_premium && (
                                    <span className="text-xs">⭐</span>
                                  )}
                                </div>
                                {member.history && member.history.length > 0 && (
                                  <button
                                    onClick={() => toggleMemberExpanded(member.id)}
                                    className="flex-shrink-0 p-0.5 hover:bg-green-200 rounded transition-colors"
                                  >
                                    {isExpanded ? (
                                      <ChevronUp className="w-3 h-3 text-green-700" />
                                    ) : (
                                      <ChevronDown className="w-3 h-3 text-green-700" />
                                    )}
                                  </button>
                                )}
                              </div>
                              <div className="text-xs text-green-700 mb-0.5">
                                <span className="font-mono">ID: {member.telegram_user_id}</span>
                                {member.username && <span className="ml-1">@{member.username}</span>}
                              </div>
                              {member.joined_at && (
                                <div className="text-xs text-green-600">
                                  {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                                </div>
                              )}
                              {member.history && member.history.length > 0 && (
                                <div className="text-xs text-green-600 mt-0.5">
                                  <History className="w-2.5 h-2.5 inline mr-0.5" />
                                  {member.history.length} изм.
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Expanded history section */}
                        {isExpanded && member.history && member.history.length > 0 && (
                          <div className="border-t border-green-300 bg-green-25 px-2 py-1.5">
                            <div className="text-xs font-medium text-green-900 mb-1">История:</div>
                            <div className="space-y-1 max-h-24 overflow-y-auto">
                              {member.history.map((change) => (
                                <div key={change.id} className="text-xs bg-white rounded p-1.5 border border-green-200">
                                  <div className="flex justify-between items-start mb-0.5">
                                    <span className="font-medium text-green-900 capitalize">
                                      {change.field_name === 'first_name' ? 'Имя' :
                                       change.field_name === 'last_name' ? 'Фамилия' :
                                       change.field_name === 'username' ? 'Username' : change.field_name}
                                    </span>
                                    <span className="text-green-600 text-xs">
                                      {new Date(change.changed_at).toLocaleDateString('ru-RU')}
                                    </span>
                                  </div>
                                  <div className="text-green-800">
                                    {change.old_value && change.new_value ? (
                                      <span>
                                        <span className="line-through text-red-600">{change.old_value}</span>
                                        {' → '}
                                        <span className="text-green-600 font-medium">{change.new_value}</span>
                                      </span>
                                    ) : change.new_value ? (
                                      <span className="text-green-600 font-medium">Установлено: {change.new_value}</span>
                                    ) : change.old_value ? (
                                      <span className="text-red-600">Удалено: {change.old_value}</span>
                                    ) : (
                                      <span className="text-gray-600">Изменение без данных</span>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Pagination */}
                {membersData.total > memberPageSize && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-gray-500">
                        {((memberPage - 1) * memberPageSize) + 1}-{Math.min(memberPage * memberPageSize, membersData.total)} из {membersData.total}
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <button
                          onClick={() => setMemberPage(prev => Math.max(1, prev - 1))}
                          disabled={memberPage === 1}
                          className="p-0.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronLeft className="h-3.5 w-3.5" />
                        </button>
                        <span className="text-xs text-gray-600">
                          {memberPage} / {Math.ceil(membersData.total / memberPageSize)}
                        </span>
                        <button
                          onClick={() => setMemberPage(prev => prev + 1)}
                          disabled={memberPage >= Math.ceil(membersData.total / memberPageSize)}
                          className="p-0.5 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <ChevronRight className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-4 bg-gray-50 rounded">
                <Users className="h-6 w-6 text-gray-300 mx-auto mb-1" />
                <p className="text-xs text-gray-500 mb-0.5">Участники не найдены</p>
                <p className="text-xs text-gray-400">
                  Информация может быть недоступна
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Посты чата */}
      <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-gray-900">Посты чата</h2>
          <button
            onClick={() => setShowCreatePostModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>Создать пост</span>
          </button>
        </div>

        <ChatPostsList chatId={chat.id} />
      </div>

      {/* Create Post Modal */}
      {showCreatePostModal && (
        <CreatePostModal
          chatId={chat.id}
          onClose={() => setShowCreatePostModal(false)}
          onSuccess={() => {
            setShowCreatePostModal(false);
          }}
        />
      )}
    </div>
  );
};