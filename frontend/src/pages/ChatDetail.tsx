import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, Radio, Settings, Calendar, User, Unlink, Plus, Trash2, Clock, FileText, ExternalLink, Search, ChevronLeft, ChevronRight, ChevronDown, ChevronUp, MessageSquare, MessageCircle, Upload } from 'lucide-react';
import { useChatDetail, useAvailableChannels, useLinkChannel, useUnlinkChannel, useChatModerators, useRemoveModerator, useChatMembers, useChatSubscriptionStatus, useCreateChatSubscription, useDeactivateChatSubscription } from '../hooks/useChats';
import { Loading } from '../components/ui/Loading';
import { Select } from '../components/ui/Select';
import { ChatPostsList } from '../components/chat/ChatPostsList';
import { CreatePostModal } from '../components/modals/CreatePostModal';
import { WelcomeMessageModal } from '../components/modals/WelcomeMessageModal';
import { TelegramMessagePreview } from '../components/chat/TelegramMessagePreview';
import { UserFileUploadModal } from '../components/chat/UserFileUploadModal';

export const ChatDetail: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const { data, isLoading } = useChatDetail(chatId!);
  const [showChannelSelector, setShowChannelSelector] = useState(false);
  const [showSubscriptionForm, setShowSubscriptionForm] = useState(false);
  const [showCreatePostModal, setShowCreatePostModal] = useState(false);
  const [subscriptionForm, setSubscriptionForm] = useState({
    subscription_type: 'month' as 'month' | 'year',
    price_stars: 1,
    currency: 'XTR',
    end_date: ''
  });

  // Chat info tabs state
  const [activeTab, setActiveTab] = useState<'info' | 'moderators' | 'welcome'>('welcome');
  const [showWelcomeMessageModal, setShowWelcomeMessageModal] = useState(false);

  // User file upload state
  const [showUserFileUpload, setShowUserFileUpload] = useState(false);

  // Chat members search and pagination state
  const [memberSearch, setMemberSearch] = useState('');
  const [memberPage, setMemberPage] = useState(1);
  const [memberPageSize] = useState(7);
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
      icon: Users,
      color: 'purple'
    },
    {
      title: 'Участники',
      value: chat.member_count || membersData?.total || 0,
      icon: User,
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

  return (
    <div className="space-y-3 pb-6">
      {/* Компактный заголовок с градиентом и метриками */}
      <div className="bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 rounded-xl shadow-xl p-4 text-white">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            <button
              onClick={() => navigate('/chats')}
              className="p-2 hover:bg-white/20 rounded-lg transition-all flex-shrink-0"
            >
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div className="flex-1 min-w-0">
              <h1 className="text-2xl font-bold truncate mb-2">{chat.chat_title}</h1>
              <div className="flex flex-wrap items-center gap-2 text-sm">
                <span className="px-2.5 py-1 bg-white/20 backdrop-blur-sm rounded-lg font-mono">
                  ID: {chat.chat_id}
                </span>
                <span className={`px-2.5 py-1 rounded-lg font-medium backdrop-blur-sm ${
                  chat.is_active ? 'bg-green-500/80' : 'bg-red-500/80'
                }`}>
                  {chat.is_active ? '● Активен' : '○ Неактивен'}
                </span>
                <span className="px-2.5 py-1 bg-white/20 backdrop-blur-sm rounded-lg">
                  <Calendar className="h-3.5 w-3.5 inline mr-1" />
                  {new Date(chat.added_date).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Компактные метрики внутри заголовка */}
        <div className="grid grid-cols-4 gap-3">
          {statsCards.map((stat, index) => (
            <div key={index} className="bg-white/10 backdrop-blur-md rounded-lg p-3 text-center hover:bg-white/20 transition-all">
              <stat.icon className="h-5 w-5 mx-auto mb-1 opacity-90" />
              <div className="text-xl font-bold">{stat.value}</div>
              <div className="text-[10px] opacity-80 uppercase tracking-wide">{stat.title}</div>
            </div>
          ))}
        </div>

        {/* Статусы в заголовке */}
        <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/20">
          <span className={`text-xs px-2.5 py-1 rounded-lg font-medium backdrop-blur-sm ${
            chat.delete_messages_enabled ? 'bg-red-500/30' : 'bg-white/20'
          }`}>
            🗑️ Удаление: {chat.delete_messages_enabled ? 'Вкл' : 'Откл'}
          </span>
          <span className={`text-xs px-2.5 py-1 rounded-lg font-medium backdrop-blur-sm ${
            (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-500/30' :
            (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-500/30' :
            'bg-white/20'
          }`}>
            🤖 AI: {
              (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Активна' :
              (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'Нет оплаты' :
              'Откл'
            }
          </span>
        </div>
      </div>

      {/* Основная сетка с 3 колонками */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        
        {/* Левая колонка (2 колонки из 3) */}
        <div className="lg:col-span-2 space-y-3">
          
          {/* Объединенный блок с вкладками */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
            {/* Вкладки */}
            <div className="flex border-b border-gray-200 bg-gray-50">
              <button
                onClick={() => setActiveTab('welcome')}
                className={`flex-1 flex items-center justify-center px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === 'welcome'
                    ? 'bg-white text-green-600 border-b-2 border-green-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <MessageCircle className="h-4 w-4 mr-2" />
                Приветствие
              </button>
              <button
                onClick={() => setActiveTab('info')}
                className={`flex-1 flex items-center justify-center px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === 'info'
                    ? 'bg-white text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <FileText className="h-4 w-4 mr-2" />
                Информация
              </button>
              <button
                onClick={() => setActiveTab('moderators')}
                className={`flex-1 flex items-center justify-center px-4 py-3 text-sm font-medium transition-all ${
                  activeTab === 'moderators'
                    ? 'bg-white text-purple-600 border-b-2 border-purple-600'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <Users className="h-4 w-4 mr-2" />
                Модераторы
                {(moderatorsData?.length || moderators.length) > 0 && (
                  <span className="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-0.5 rounded-full">
                    {moderatorsData?.length || moderators.length}
                  </span>
                )}
              </button>
            </div>

            {/* Содержимое вкладок */}
            <div className="p-4">
              {/* Вкладка: Приветствие */}
              {activeTab === 'welcome' && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-bold text-gray-900">Приветственное сообщение</h3>
                    <button
                      onClick={() => setShowWelcomeMessageModal(true)}
                      className="px-3 py-1 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 transition-all flex items-center"
                    >
                      <Settings className="h-3 w-3 mr-1" />
                      Настроить
                    </button>
                  </div>

                  {chat.welcome_message_enabled ? (
                    <div className="space-y-4">
                      {/* Status badge */}
                      <div className="flex items-center justify-center space-x-2 p-2 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-xs text-green-800 font-medium">Приветствие активно</span>
                      </div>

                      {/* Telegram-style preview */}
                      <TelegramMessagePreview
                        text={chat.welcome_message_text}
                        mediaType={chat.welcome_message_media_type as 'photo' | 'video' | null}
                        mediaUrl={chat.welcome_message_media_url}
                        buttons={chat.welcome_message_buttons ? JSON.parse(JSON.stringify(chat.welcome_message_buttons)) : []}
                        lifetimeMinutes={chat.welcome_message_lifetime_minutes}
                      />
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <MessageCircle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                      <p className="text-sm text-gray-500 mb-2">Приветственное сообщение отключено</p>
                      <p className="text-xs text-gray-400 mb-4">
                        Настройте сообщение, которое будет автоматически отправляться новым участникам
                      </p>
                      <button
                        onClick={() => setShowWelcomeMessageModal(true)}
                        className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-all"
                      >
                        Настроить приветствие
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Вкладка: Информация */}
              {activeTab === 'info' && (
                <div className="space-y-3">
                  {/* Описание */}
                  {chat.description && (
                    <div className="p-3 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                      <div className="text-xs font-bold text-blue-900 mb-1">Описание</div>
                      <p className="text-xs text-blue-900">{chat.description}</p>
                    </div>
                  )}

                  {/* Ссылка и дата обновления */}
                  <div className="grid grid-cols-2 gap-2">
                    {chat.invite_link && (
                      <a
                        href={chat.invite_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 p-3 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200 hover:shadow-md transition-all group"
                      >
                        <ExternalLink className="h-4 w-4 text-green-600 flex-shrink-0" />
                        <span className="text-xs font-medium text-green-900 truncate group-hover:underline">
                          Открыть ссылку
                        </span>
                      </a>
                    )}
                    {chat.last_info_update && (
                      <div className="flex items-center space-x-2 p-3 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                        <Calendar className="h-4 w-4 text-purple-600 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="text-[10px] text-purple-700 uppercase font-medium">Обновлено</div>
                          <div className="text-xs font-medium text-purple-900 truncate">
                            {new Date(chat.last_info_update).toLocaleDateString('ru-RU')}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* AI проверка и Подписка */}
                  <div>
                    <h4 className="text-sm font-bold text-gray-900 mb-2">AI & Подписка</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {/* AI статус */}
                      <div className="p-2 bg-gradient-to-br from-green-50 to-emerald-100 rounded-lg border border-green-200">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-green-900">AI проверка</span>
                          <div className={`w-2.5 h-2.5 rounded-full ${
                            (subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-green-500 animate-pulse' :
                            (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? 'bg-yellow-500' :
                            'bg-gray-400'
                          }`} />
                        </div>
                        <p className="text-xs text-green-800 leading-relaxed">
                          {(subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? '✓ Активна и работает' :
                           (!subscriptionStatus?.has_active_subscription && chat.ai_content_check_enabled) ? '⚠ Требуется оплата' :
                           '○ Отключена'}
                        </p>
                      </div>

                      {/* Подписка */}
                      <div className="p-2 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg border border-blue-200">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-bold text-blue-900">Подписка</span>
                          {!chat.active_subscription && (
                            <button
                              onClick={() => setShowSubscriptionForm(!showSubscriptionForm)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Plus className="h-3.5 w-3.5" />
                            </button>
                          )}
                        </div>
                        {chat.active_subscription ? (
                          <div className="space-y-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-blue-800">💎 {chat.active_subscription.price_stars} ⭐</span>
                              <span className="text-blue-700 font-medium">
                                {chat.active_subscription.subscription_type === 'month' ? 'Месяц' : 'Год'}
                              </span>
                            </div>
                            <div className="text-xs text-blue-800">
                              до {new Date(chat.active_subscription.end_date).toLocaleDateString('ru-RU')}
                            </div>
                            <button
                              onClick={() => handleDeactivateSubscription(chat.active_subscription!.id)}
                              className="text-[10px] text-red-600 hover:text-red-800 font-medium"
                            >
                              Деактивировать
                            </button>
                          </div>
                        ) : (
                          <p className="text-xs text-blue-800">○ Не активна</p>
                        )}
                      </div>
                    </div>

                    {/* Форма создания подписки */}
                    {showSubscriptionForm && (
                      <div className="pt-2 border-t border-gray-200 mt-2">
                        <h5 className="text-xs font-bold text-gray-900 mb-1.5">Новая подписка</h5>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                          <Select
                            label="Тип"
                            value={subscriptionForm.subscription_type}
                            onChange={(e) => setSubscriptionForm(prev => ({
                              ...prev,
                              subscription_type: e.target.value as 'month' | 'year'
                            }))}
                            icon={<Calendar className="w-3.5 h-3.5" />}
                          >
                            <option value="month">Месяц</option>
                            <option value="year">Год</option>
                          </Select>
                          <div>
                            <label className="block text-[10px] font-medium text-gray-700 mb-1">Стоимость ⭐</label>
                            <input
                              type="number"
                              min="1"
                              value={subscriptionForm.price_stars}
                              onChange={(e) => setSubscriptionForm(prev => ({
                                ...prev,
                                price_stars: parseInt(e.target.value) || 1
                              }))}
                              className="w-full px-2 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                        </div>
                        <div className="mb-2">
                          <label className="block text-[10px] font-medium text-gray-700 mb-1">Окончание</label>
                          <input
                            type="datetime-local"
                            value={subscriptionForm.end_date}
                            onChange={(e) => setSubscriptionForm(prev => ({
                              ...prev,
                              end_date: e.target.value
                            }))}
                            className="w-full px-2 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setShowSubscriptionForm(false)}
                            className="px-2 py-1 text-xs text-gray-600 hover:text-gray-800"
                          >
                            Отмена
                          </button>
                          <button
                            onClick={handleCreateSubscription}
                            disabled={createSubscriptionMutation.isPending || !subscriptionForm.end_date}
                            className="px-3 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 disabled:opacity-50"
                          >
                            {createSubscriptionMutation.isPending ? 'Создание...' : 'Создать'}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Привязанный канал */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-bold text-gray-900">Привязанный канал</h4>
                      {!chat.linked_channel && (
                        <button
                          onClick={() => setShowChannelSelector(!showChannelSelector)}
                          className="px-2 py-1 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-all flex items-center"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Привязать
                        </button>
                      )}
                    </div>

                    {chat.linked_channel ? (
                      <div className="relative group">
                        <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-2 border border-blue-200 hover:shadow-md transition-all">
                          <div className="flex items-start space-x-2">
                            <div className="w-7 h-7 bg-blue-200 rounded-full flex items-center justify-center flex-shrink-0">
                              <Radio className="w-3.5 h-3.5 text-blue-700" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="text-sm font-medium text-blue-900 truncate">
                                {chat.linked_channel.title || `Канал ${chat.linked_channel.telegram_chat_id}`}
                              </h4>
                              <div className="text-xs text-blue-700 font-mono mt-0.5">
                                ID: {chat.linked_channel.telegram_chat_id}
                              </div>
                              {chat.linked_channel.username && (
                                <a
                                  href={`https://t.me/${chat.linked_channel.username}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs text-blue-600 hover:underline inline-block mt-1"
                                >
                                  @{chat.linked_channel.username}
                                </a>
                              )}
                            </div>
                            <button
                              onClick={handleUnlinkChannel}
                              disabled={unlinkChannelMutation.isPending}
                              className="flex-shrink-0 text-red-500 hover:text-red-700 disabled:opacity-50 p-1 rounded hover:bg-red-50 transition-all"
                              title="Отвязать канал"
                            >
                              <Unlink className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-4 bg-gray-50 rounded-lg">
                        <Radio className="h-6 w-6 text-gray-300 mx-auto mb-1" />
                        <p className="text-xs text-gray-500">Канал не привязан</p>
                      </div>
                    )}

                    {/* Селектор каналов */}
                    {showChannelSelector && availableChannels && availableChannels.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <h5 className="text-xs font-bold text-gray-900 mb-1.5">Выберите канал:</h5>
                        <div className="space-y-1.5 max-h-48 overflow-y-auto">
                          {availableChannels.map((channel) => (
                            <div
                              key={channel.id}
                              className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-2 border border-green-200 hover:shadow-md cursor-pointer transition-all"
                              onClick={() => handleLinkChannel(channel.id)}
                            >
                              <div className="flex items-center space-x-2">
                                <Radio className="h-3.5 w-3.5 text-green-600 flex-shrink-0" />
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs font-medium text-green-900 truncate">
                                    {channel.title || `Канал ${channel.telegram_chat_id}`}
                                  </div>
                                  <div className="text-[10px] text-green-700 font-mono">
                                    ID: {channel.telegram_chat_id}
                                  </div>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                        <button
                          onClick={() => setShowChannelSelector(false)}
                          className="mt-1.5 text-xs text-gray-600 hover:text-gray-800"
                        >
                          Отмена
                        </button>
                      </div>
                    )}

                    {showChannelSelector && (!availableChannels || availableChannels.length === 0) && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <p className="text-xs text-gray-500 text-center py-3">
                          Нет доступных каналов
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Вкладка: Модераторы */}
              {activeTab === 'moderators' && (
                <div>
                  {(moderatorsData || moderators).length > 0 ? (
                    <div className="grid grid-cols-2 gap-2">
                      {(moderatorsData || moderators).map((moderator) => (
                        <div key={moderator.id} className="relative group">
                          <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-2 border border-purple-200 hover:shadow-md transition-all">
                            <div className="flex items-start space-x-2">
                              <div className="w-7 h-7 bg-purple-200 rounded-full flex items-center justify-center flex-shrink-0">
                                <User className="w-3.5 h-3.5 text-purple-700" />
                              </div>
                              <div className="flex-1 min-w-0">
                                <h4 className="text-xs font-medium text-purple-900 truncate">
                                  {'moderator_name' in moderator ? moderator.moderator_name : `${moderator.first_name || ''} ${moderator.last_name || ''}`.trim() || `ID: ${moderator.moderator_user_id}`}
                                </h4>
                                <div className="text-[10px] text-purple-700 font-mono mt-0.5">
                                  {moderator.moderator_user_id}
                                </div>
                                {('moderator_username' in moderator ? moderator.moderator_username : moderator.username) && (
                                  <a
                                    href={`https://t.me/${'moderator_username' in moderator ? moderator.moderator_username : moderator.username}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-[10px] text-purple-600 hover:underline truncate block"
                                  >
                                    @{'moderator_username' in moderator ? moderator.moderator_username : moderator.username}
                                  </a>
                                )}
                              </div>
                              <button
                                onClick={() => handleRemoveModerator(moderator.id)}
                                disabled={removeModeratorMutation.isPending}
                                className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 disabled:opacity-50 p-1 rounded hover:bg-red-50 transition-all"
                              >
                                <Trash2 className="h-3 w-3" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 bg-gray-50 rounded-lg">
                      <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                      <p className="text-xs text-gray-500">Модераторы не назначены</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Правая колонка - Участники (1 колонка из 3) */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-3 sticky top-3">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center">
                <Users className="h-4 w-4 mr-2 text-green-600" />
                <h3 className="text-sm font-bold text-gray-900">Участники</h3>
                <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full font-medium">
                  {membersData?.total || 0}
                </span>
              </div>
              <button
                onClick={() => setShowUserFileUpload(true)}
                className="p-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
                title="Загрузить из файла"
              >
                <Upload className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Search */}
            <div className="mb-3">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3.5 w-3.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Поиск..."
                  value={memberSearch}
                  onChange={(e) => setMemberSearch(e.target.value)}
                  className="w-full pl-7 pr-2 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {membersLoading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600"></div>
              </div>
            ) : membersData && membersData.members && membersData.members.length > 0 ? (
              <>
                <div className="space-y-1.5 max-h-[600px] overflow-y-auto">
                  {membersData.members.map((member) => {
                    const isExpanded = expandedMembers.has(member.id);
                    return (
                      <div key={member.id} className="bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200 hover:shadow transition-all">
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
                              <div className="flex items-center justify-between">
                                <h4 className="text-xs font-medium text-green-900 truncate flex-1">
                                  {member.first_name || ''} {member.last_name || ''} {!member.first_name && !member.last_name && `ID: ${member.telegram_user_id}`}
                                  {member.is_premium && <span className="ml-1">⭐</span>}
                                </h4>
                                {member.history && member.history.length > 0 && (
                                  <button
                                    onClick={() => toggleMemberExpanded(member.id)}
                                    className="p-0.5 hover:bg-green-200 rounded"
                                  >
                                    {isExpanded ? (
                                      <ChevronUp className="w-3 h-3 text-green-700" />
                                    ) : (
                                      <ChevronDown className="w-3 h-3 text-green-700" />
                                    )}
                                  </button>
                                )}
                              </div>
                              <div className="text-[10px] text-green-700 font-mono">
                                {member.telegram_user_id}
                                {member.username && <span className="ml-1">@{member.username}</span>}
                              </div>
                              {member.joined_at && (
                                <div className="text-[10px] text-green-600 mt-0.5">
                                  {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* History */}
                        {isExpanded && member.history && member.history.length > 0 && (
                          <div className="border-t border-green-300 px-2 py-1.5 bg-white/50">
                            <div className="text-[10px] font-bold text-green-900 mb-1">История:</div>
                            <div className="space-y-1 max-h-24 overflow-y-auto">
                              {member.history.map((change) => (
                                <div key={change.id} className="text-[10px] bg-white rounded p-1 border border-green-200">
                                  <div className="flex justify-between mb-0.5">
                                    <span className="font-medium text-green-900">
                                      {change.field_name === 'first_name' ? 'Имя' :
                                       change.field_name === 'last_name' ? 'Фамилия' :
                                       change.field_name === 'username' ? 'Username' : change.field_name}
                                    </span>
                                    <span className="text-green-600">
                                      {new Date(change.changed_at).toLocaleDateString('ru-RU')}
                                    </span>
                                  </div>
                                  <div className="text-green-800">
                                    {change.old_value && change.new_value ? (
                                      <>
                                        <span className="line-through text-red-600">{change.old_value}</span>
                                        {' → '}
                                        <span className="text-green-600 font-medium">{change.new_value}</span>
                                      </>
                                    ) : change.new_value ? (
                                      <span className="text-green-600">+ {change.new_value}</span>
                                    ) : change.old_value ? (
                                      <span className="text-red-600">- {change.old_value}</span>
                                    ) : (
                                      <span className="text-gray-600">Нет данных</span>
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
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">
                        {((memberPage - 1) * memberPageSize) + 1}-{Math.min(memberPage * memberPageSize, membersData.total)} из {membersData.total}
                      </span>
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => setMemberPage(prev => Math.max(1, prev - 1))}
                          disabled={memberPage === 1}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          <ChevronLeft className="h-3.5 w-3.5" />
                        </button>
                        <span className="text-gray-600">
                          {memberPage}/{Math.ceil(membersData.total / memberPageSize)}
                        </span>
                        <button
                          onClick={() => setMemberPage(prev => prev + 1)}
                          disabled={memberPage >= Math.ceil(membersData.total / memberPageSize)}
                          className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
                        >
                          <ChevronRight className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-xs text-gray-500">Участники не найдены</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Посты чата - полная ширина внизу */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2 text-indigo-600" />
            <h2 className="text-lg font-bold text-gray-900">Посты чата</h2>
          </div>
          <button
            onClick={() => setShowCreatePostModal(true)}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all shadow-md"
          >
            <Plus className="h-4 w-4 mr-2" />
            Создать пост
          </button>
        </div>
        <ChatPostsList chatId={chat.id} />
      </div>

      {/* Модальное окно создания поста */}
      {showCreatePostModal && (
        <CreatePostModal
          chatId={chat.id}
          onClose={() => setShowCreatePostModal(false)}
        />
      )}

      {/* Модальное окно настройки приветственного сообщения */}
      {showWelcomeMessageModal && (
        <WelcomeMessageModal
          chat={{
            id: chat.id,
            telegram_chat_id: chat.chat_id,
            chat_type: chat.chat_type as 'group' | 'supergroup' | 'channel',
            title: chat.chat_title,
            added_by_user_id: chat.admin_user_id,
            is_active: chat.is_active,
            added_at: chat.added_date,
            created_at: chat.added_date,
            updated_at: chat.added_date,
            ai_content_check_enabled: chat.ai_content_check_enabled,
            delete_messages_enabled: chat.delete_messages_enabled,
            chat_moderators: [],
            welcome_message_enabled: chat.welcome_message_enabled,
            welcome_message_text: chat.welcome_message_text,
            welcome_message_media_type: chat.welcome_message_media_type,
            welcome_message_media_url: chat.welcome_message_media_url,
            welcome_message_lifetime_minutes: chat.welcome_message_lifetime_minutes,
            welcome_message_buttons: chat.welcome_message_buttons,
          }}
          onClose={() => setShowWelcomeMessageModal(false)}
        />
      )}

      {/* Модальное окно загрузки файла с User ID */}
      {showUserFileUpload && (
        <UserFileUploadModal
          chatId={chat.id}
          onClose={() => setShowUserFileUpload(false)}
          onSuccess={() => {
            // Refresh chat members after successful verification
            window.location.reload();
          }}
        />
      )}
    </div>
  );
};
