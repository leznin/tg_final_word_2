import React, { useState, useEffect } from 'react';
import { Search, Users, CheckCircle, XCircle, AlertTriangle, RefreshCw, Clock, Calendar, Settings, MessageSquare } from 'lucide-react';
import { Loading } from '../components/ui/Loading';
import { Select } from '../components/ui/Select';
import { ProgressBar } from '../components/ui/ProgressBar';

interface Chat {
  id: number;
  telegram_chat_id: number;
  title: string;
  chat_type: string;
  is_active: boolean;
}

interface UserChangeDetail {
  old_value: string | null;
  new_value: string | null;
}

interface UserVerificationResult {
  telegram_user_id: number;
  chat_id: number;
  chat_title: string | null;
  is_updated: boolean;
  has_changes: boolean;
  changes: Record<string, UserChangeDetail>;
  current_status: string | null;
  checked_at: string;
  error: string | null;
}

interface BulkVerificationResponse {
  total_checked: number;
  total_updated: number;
  total_errors: number;
  total_with_changes: number;
  results: UserVerificationResult[];
  started_at: string;
  completed_at: string;
  duration_seconds: number;
}

interface VerificationSchedule {
  id: number;
  enabled: boolean;
  schedule_time: string;
  interval_hours: number;
  auto_update: boolean;
  chat_id: number | null;
  created_at: string;
  updated_at: string;
  last_run_at: string | null;
  next_run_at: string | null;
  chat_title: string | null;
}

export const UserVerification: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'bulk' | 'schedule'>('single');
  const [chats, setChats] = useState<Chat[]>([]);
  const [loadingChats, setLoadingChats] = useState(true);
  
  // Single user verification state
  const [singleChatId, setSingleChatId] = useState<string>('');
  const [telegramUserId, setTelegramUserId] = useState<string>('');
  const [singleAutoUpdate, setSingleAutoUpdate] = useState(true);
  const [verifySingleLoading, setVerifySingleLoading] = useState(false);
  
  // Bulk verification state
  const [bulkChatId, setBulkChatId] = useState<string>('');
  const [bulkAutoUpdate, setBulkAutoUpdate] = useState(true);
  const [verifyBulkLoading, setVerifyBulkLoading] = useState(false);
  
  // Progress tracking state
  const [verificationProgress, setVerificationProgress] = useState<any>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  
  // Results state
  const [results, setResults] = useState<UserVerificationResult[]>([]);
  const [stats, setStats] = useState<BulkVerificationResponse | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'changes' | 'errors'>('all');
  
  // Schedule state
  const [schedules, setSchedules] = useState<VerificationSchedule[]>([]);
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [scheduleForm, setScheduleForm] = useState({
    enabled: true,
    schedule_time: '02:00',
    interval_hours: 24,
    auto_update: true,
    chat_id: ''
  });
  const [editingScheduleId, setEditingScheduleId] = useState<number | null>(null);
  
  // Load chats on mount
  useEffect(() => {
    loadChats();
    loadSchedules();
  }, []);
  
  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);
  
  const startProgressPolling = () => {
    // Clear any existing interval
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    
    // Start polling for progress every 500ms
    const interval = setInterval(async () => {
      try {
        const response = await fetch('/api/v1/admin/user-verification/status');
        const data = await response.json();
        setVerificationProgress(data);
        
        // Stop polling if verification is complete
        if (!data.is_running) {
          clearInterval(interval);
          setPollingInterval(null);
        }
      } catch (error) {
        console.error('Error fetching verification status:', error);
      }
    }, 500);
    
    setPollingInterval(interval);
  };
  
  const stopProgressPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
    setVerificationProgress(null);
  };
  
  const loadChats = async () => {
    try {
      const response = await fetch('/api/v1/admin/user-verification/chats');
      const data = await response.json();
      setChats(data.chats);
    } catch (error) {
      console.error('Error loading chats:', error);
      alert('Не удалось загрузить список чатов');
    } finally {
      setLoadingChats(false);
    }
  };
  
  const verifySingleUser = async () => {
    if (!singleChatId || !telegramUserId) {
      alert('Пожалуйста, выберите чат и введите ID пользователя');
      return;
    }
    
    setVerifySingleLoading(true);
    try {
      const response = await fetch('/api/v1/admin/user-verification/verify-user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          telegram_user_id: parseInt(telegramUserId),
          chat_id: parseInt(singleChatId),
          auto_update: singleAutoUpdate
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка проверки');
      }
      
      const result = await response.json();
      setResults([result]);
      setStats({
        total_checked: 1,
        total_with_changes: result.has_changes ? 1 : 0,
        total_updated: result.is_updated ? 1 : 0,
        total_errors: result.error ? 1 : 0,
        results: [result],
        started_at: result.checked_at,
        completed_at: result.checked_at,
        duration_seconds: 0
      });
    } catch (error: any) {
      console.error('Error verifying user:', error);
      alert('Ошибка проверки: ' + error.message);
    } finally {
      setVerifySingleLoading(false);
    }
  };
  
  const verifyActiveUsers = async () => {
    setVerifyBulkLoading(true);
    setVerificationProgress({ is_running: true, current_progress: 0, total_users: 0 });
    startProgressPolling();
    
    try {
      const response = await fetch('/api/v1/admin/user-verification/verify-active-users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: bulkChatId ? parseInt(bulkChatId) : null,
          auto_update: bulkAutoUpdate,
          delay_between_requests: 0.5
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка проверки');
      }
      
      const result = await response.json();
      setResults(result.results);
      setStats(result);
    } catch (error: any) {
      console.error('Error verifying users:', error);
      alert('Ошибка проверки: ' + error.message);
    } finally {
      setVerifyBulkLoading(false);
      stopProgressPolling();
    }
  };
  
  const loadSchedules = async () => {
    try {
      const response = await fetch('/api/v1/admin/verification-schedule/schedules');
      if (!response.ok) throw new Error('Failed to load schedules');
      const data = await response.json();
      setSchedules(data);
    } catch (error) {
      console.error('Error loading schedules:', error);
    }
  };

  const saveSchedule = async () => {
    try {
      const payload = {
        ...scheduleForm,
        schedule_time: scheduleForm.schedule_time + ':00',
        chat_id: scheduleForm.chat_id ? parseInt(scheduleForm.chat_id) : null
      };

      const url = editingScheduleId 
        ? `/api/v1/admin/verification-schedule/schedules/${editingScheduleId}`
        : '/api/v1/admin/verification-schedule/schedules';
      
      const response = await fetch(url, {
        method: editingScheduleId ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка сохранения');
      }

      await loadSchedules();
      setShowScheduleForm(false);
      setEditingScheduleId(null);
      setScheduleForm({
        enabled: true,
        schedule_time: '02:00',
        interval_hours: 24,
        auto_update: true,
        chat_id: ''
      });
    } catch (error: any) {
      console.error('Error saving schedule:', error);
      alert('Ошибка сохранения: ' + error.message);
    }
  };

  const deleteSchedule = async (scheduleId: number) => {
    if (!confirm('Вы уверены, что хотите удалить это расписание?')) return;
    
    try {
      const response = await fetch(`/api/v1/admin/verification-schedule/schedules/${scheduleId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete schedule');
      await loadSchedules();
    } catch (error) {
      console.error('Error deleting schedule:', error);
      alert('Ошибка удаления расписания');
    }
  };

  const toggleSchedule = async (scheduleId: number) => {
    try {
      const response = await fetch(`/api/v1/admin/verification-schedule/schedules/${scheduleId}/toggle`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to toggle schedule');
      await loadSchedules();
    } catch (error) {
      console.error('Error toggling schedule:', error);
      alert('Ошибка переключения расписания');
    }
  };

  const editSchedule = (schedule: VerificationSchedule) => {
    setEditingScheduleId(schedule.id);
    setScheduleForm({
      enabled: schedule.enabled,
      schedule_time: schedule.schedule_time.substring(0, 5),
      interval_hours: schedule.interval_hours,
      auto_update: schedule.auto_update,
      chat_id: schedule.chat_id ? schedule.chat_id.toString() : ''
    });
    setShowScheduleForm(true);
  };
  
  const getFilteredResults = () => {
    if (filterType === 'all') return results;
    if (filterType === 'changes') return results.filter(r => r.has_changes);
    if (filterType === 'errors') return results.filter(r => r.error);
    return results;
  };
  
  const formatTimeUntil = (dateString: string): string => {
    const now = new Date();
    const target = new Date(dateString);
    const diffMs = target.getTime() - now.getTime();
    
    if (diffMs < 0) return 'прошло';
    
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays > 0) {
      const hours = diffHours % 24;
      return `через ${diffDays}д ${hours}ч`;
    } else if (diffHours > 0) {
      const minutes = diffMinutes % 60;
      return `через ${diffHours}ч ${minutes}м`;
    } else {
      return `через ${diffMinutes}м`;
    }
  };

  if (loadingChats) {
    return <Loading />;
  }

  return (
    <div className="max-w-7xl mx-auto space-y-4">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Проверка пользователей</h1>
            <p className="mt-1 text-blue-100 text-sm">
              Автоматическая проверка и обновление данных через Telegram API
            </p>
          </div>
          <Users className="w-12 h-12 opacity-80" />
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-sm p-1 flex gap-1">
        <button
          onClick={() => setActiveTab('single')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'single'
              ? 'bg-blue-600 text-white shadow-md'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Search className="w-5 h-5" />
          <span>Один пользователь</span>
        </button>
        <button
          onClick={() => setActiveTab('bulk')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'bulk'
              ? 'bg-green-600 text-white shadow-md'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Users className="w-5 h-5" />
          <span>Массовая проверка</span>
        </button>
        <button
          onClick={() => setActiveTab('schedule')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
            activeTab === 'schedule'
              ? 'bg-purple-600 text-white shadow-md'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Clock className="w-5 h-5" />
          <span>Расписание</span>
        </button>
      </div>

      {/* Single User Tab */}
      {activeTab === 'single' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <Select
              label="Чат"
              value={singleChatId}
              onChange={(e) => setSingleChatId(e.target.value)}
              icon={<MessageSquare className="w-5 h-5" />}
              variant="primary"
            >
              <option value="">Выберите чат...</option>
              {chats.map(chat => (
                <option key={chat.id} value={chat.id}>
                  {chat.title}
                </option>
              ))}
            </Select>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Telegram User ID
              </label>
              <input
                type="number"
                value={telegramUserId}
                onChange={(e) => setTelegramUserId(e.target.value)}
                placeholder="Введите User ID"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={singleAutoUpdate}
                onChange={(e) => setSingleAutoUpdate(e.target.checked)}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">Автообновление при изменениях</span>
            </label>
            
            <button
              onClick={verifySingleUser}
              disabled={verifySingleLoading || !singleChatId || !telegramUserId}
              className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
            >
              {verifySingleLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Проверка...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Проверить
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Bulk Verification Tab */}
      {activeTab === 'bulk' && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="mb-6">
            <Select
              label="Фильтр по чату (опционально)"
              value={bulkChatId}
              onChange={(e) => setBulkChatId(e.target.value)}
              icon={<Users className="w-5 h-5" />}
              variant="success"
            >
              <option value="">Все активные пользователи</option>
              {chats.map(chat => (
                <option key={chat.id} value={chat.id}>
                  {chat.title}
                </option>
              ))}
            </Select>
          </div>
          
          {/* Progress Bar */}
          {verificationProgress && verificationProgress.is_running && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <ProgressBar
                progress={verificationProgress.progress_percentage || 0}
                total={verificationProgress.total_users}
                current={verificationProgress.current_progress}
                label="Проверка пользователей"
                showPercentage={true}
                showCount={true}
                estimatedTimeRemaining={verificationProgress.estimated_time_remaining}
                size="md"
                variant="default"
              />
              <div className="mt-3 grid grid-cols-4 gap-2 text-xs text-gray-600">
                <div className="flex items-center gap-1">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span>Обновлено: {verificationProgress.updated_users || 0}</span>
                </div>
                <div className="flex items-center gap-1">
                  <AlertTriangle className="w-4 h-4 text-yellow-500" />
                  <span>Изменений: {verificationProgress.users_with_changes || 0}</span>
                </div>
                <div className="flex items-center gap-1">
                  <XCircle className="w-4 h-4 text-red-500" />
                  <span>Ошибок: {verificationProgress.users_with_errors || 0}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4 text-blue-500" />
                  <span>Проверено: {verificationProgress.checked_users || 0}</span>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={bulkAutoUpdate}
                onChange={(e) => setBulkAutoUpdate(e.target.checked)}
                className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
              />
              <span className="text-sm text-gray-700">Автообновление при изменениях</span>
            </label>
            
            <button
              onClick={verifyActiveUsers}
              disabled={verifyBulkLoading}
              className="flex items-center gap-2 px-6 py-2.5 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
            >
              {verifyBulkLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Проверка...
                </>
              ) : (
                <>
                  <Users className="w-4 h-4" />
                  Начать проверку
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Schedule Tab */}
      {activeTab === 'schedule' && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Расписания проверок</h3>
              <button
                onClick={() => {
                  setShowScheduleForm(!showScheduleForm);
                  if (!showScheduleForm) {
                    setEditingScheduleId(null);
                    setScheduleForm({
                      enabled: true,
                      schedule_time: '02:00',
                      interval_hours: 24,
                      auto_update: true,
                      chat_id: ''
                    });
                  }
                }}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all shadow-md hover:shadow-lg"
              >
                <Settings className="w-4 h-4" />
                {showScheduleForm ? 'Отмена' : 'Добавить расписание'}
              </button>
            </div>

            {showScheduleForm && (
              <div className="mb-6 p-5 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
                <h4 className="text-md font-semibold text-gray-900 mb-4">
                  {editingScheduleId ? 'Редактировать расписание' : 'Новое расписание'}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Время запуска
                    </label>
                    <input
                      type="time"
                      value={scheduleForm.schedule_time}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, schedule_time: e.target.value })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Интервал (часов)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="168"
                      value={scheduleForm.interval_hours}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, interval_hours: parseInt(e.target.value) })}
                      className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div className="mb-4">
                  <Select
                    label="Фильтр по чату"
                    value={scheduleForm.chat_id}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, chat_id: e.target.value })}
                    icon={<MessageSquare className="w-5 h-5" />}
                    variant="default"
                  >
                    <option value="">Все чаты</option>
                    {chats.map(chat => (
                      <option key={chat.id} value={chat.id}>
                        {chat.title}
                      </option>
                    ))}
                  </Select>
                </div>

                <div className="flex items-center gap-6 mb-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={scheduleForm.enabled}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, enabled: e.target.checked })}
                      className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-700 font-medium">Включено</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={scheduleForm.auto_update}
                      onChange={(e) => setScheduleForm({ ...scheduleForm, auto_update: e.target.checked })}
                      className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                    <span className="text-sm text-gray-700 font-medium">Автообновление</span>
                  </label>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={saveSchedule}
                    className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all shadow-md hover:shadow-lg"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Сохранить
                  </button>
                  <button
                    onClick={() => {
                      setShowScheduleForm(false);
                      setEditingScheduleId(null);
                    }}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all"
                  >
                    <XCircle className="w-4 h-4" />
                    Отмена
                  </button>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {schedules.length === 0 ? (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 mx-auto text-gray-300 mb-3" />
                  <p className="text-gray-500">Нет настроенных расписаний</p>
                  <p className="text-sm text-gray-400 mt-1">Создайте первое расписание автоматической проверки</p>
                </div>
              ) : (
                schedules.map(schedule => (
                  <div key={schedule.id} className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${schedule.enabled ? 'bg-green-500 text-white' : 'bg-gray-400 text-white'}`}>
                            {schedule.enabled ? '● Активно' : '○ Выключено'}
                          </span>
                          <span className="flex items-center gap-1 text-sm font-medium text-gray-700">
                            <Clock className="w-4 h-4" />
                            {schedule.schedule_time} / {schedule.interval_hours}ч
                          </span>
                          {schedule.chat_title && (
                            <span className="text-sm text-gray-600 bg-white px-2 py-1 rounded">
                              📱 {schedule.chat_title}
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 space-y-1 ml-1">
                          {schedule.last_run_at && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3 text-gray-400" />
                              <span className="text-gray-600">Последний запуск:</span>
                              <span className="font-medium">{new Date(schedule.last_run_at).toLocaleString('ru-RU')}</span>
                            </div>
                          )}
                          {schedule.next_run_at && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3 text-blue-500" />
                              <span className="text-gray-600">Следующий запуск:</span>
                              <span className="font-medium text-blue-600">{new Date(schedule.next_run_at).toLocaleString('ru-RU')}</span>
                              <span className="text-gray-400">
                                ({formatTimeUntil(schedule.next_run_at)})
                              </span>
                            </div>
                          )}
                          {!schedule.last_run_at && (
                            <div className="flex items-center gap-1 text-gray-400">
                              <AlertTriangle className="w-3 h-3" />
                              <span>Ещё не запускалось</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => toggleSchedule(schedule.id)}
                          className={`p-2 rounded-lg text-sm font-medium transition-all ${
                            schedule.enabled 
                              ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200' 
                              : 'bg-green-100 text-green-700 hover:bg-green-200'
                          }`}
                          title={schedule.enabled ? 'Выключить' : 'Включить'}
                        >
                          {schedule.enabled ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                        </button>
                        <button
                          onClick={() => editSchedule(schedule)}
                          className="p-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all"
                          title="Изменить"
                        >
                          <Settings className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deleteSchedule(schedule.id)}
                          className="p-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all"
                          title="Удалить"
                        >
                          <XCircle className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
            <div className="text-xs text-gray-600 mb-1 font-medium">Проверено</div>
            <div className="text-2xl font-bold text-blue-600">{stats.total_checked}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-orange-500">
            <div className="text-xs text-gray-600 mb-1 font-medium">С изменениями</div>
            <div className="text-2xl font-bold text-orange-600">{stats.total_with_changes}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
            <div className="text-xs text-gray-600 mb-1 font-medium">Обновлено</div>
            <div className="text-2xl font-bold text-green-600">{stats.total_updated}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-red-500">
            <div className="text-xs text-gray-600 mb-1 font-medium">Ошибки</div>
            <div className="text-2xl font-bold text-red-600">{stats.total_errors}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-purple-500">
            <div className="text-xs text-gray-600 mb-1 font-medium">Время</div>
            <div className="text-2xl font-bold text-purple-600">{stats.duration_seconds.toFixed(1)}с</div>
          </div>
        </div>
      )}

      {/* Filter Buttons */}
      {results.length > 0 && (
        <div className="flex gap-2 bg-white rounded-lg shadow-sm p-2">
          <button
            onClick={() => setFilterType('all')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
              filterType === 'all'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Все ({results.length})
          </button>
          <button
            onClick={() => setFilterType('changes')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
              filterType === 'changes'
                ? 'bg-orange-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Изменения ({results.filter(r => r.has_changes).length})
          </button>
          <button
            onClick={() => setFilterType('errors')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
              filterType === 'errors'
                ? 'bg-red-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Ошибки ({results.filter(r => r.error).length})
          </button>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    User ID
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Чат
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Изменения
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                    Время
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getFilteredResults().map((result, index) => (
                  <tr key={index} className="hover:bg-blue-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm font-semibold text-gray-900">{result.telegram_user_id}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-600">{result.chat_title || result.chat_id}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {result.error ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-red-100 text-red-700">
                          <XCircle className="w-3 h-3" />
                          Ошибка
                        </span>
                      ) : result.is_updated ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-green-100 text-green-700">
                          <CheckCircle className="w-3 h-3" />
                          Обновлено
                        </span>
                      ) : result.has_changes ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-700">
                          <AlertTriangle className="w-3 h-3" />
                          Изменения
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                          <CheckCircle className="w-3 h-3" />
                          OK
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {result.error ? (
                        <div className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">{result.error}</div>
                      ) : Object.keys(result.changes).length > 0 ? (
                        <div className="space-y-1">
                          {Object.entries(result.changes).map(([field, change]) => (
                            <div key={field} className="bg-orange-50 px-2 py-1 rounded text-xs border-l-2 border-orange-400">
                              <span className="font-semibold text-orange-800">{field}:</span>
                              <div className="text-gray-600 mt-0.5">
                                <span className="line-through text-red-600">{change.old_value || 'null'}</span>
                                {' → '}
                                <span className="text-green-600 font-medium">{change.new_value || 'null'}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">Нет изменений</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-xs text-gray-500">
                      {new Date(result.checked_at).toLocaleString('ru-RU', { 
                        day: '2-digit', 
                        month: '2-digit', 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {getFilteredResults().length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-500">Нет результатов для выбранного фильтра</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
