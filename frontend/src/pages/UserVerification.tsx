import React, { useState, useEffect } from 'react';
import { Search, Users, CheckCircle, XCircle, AlertTriangle, RefreshCw, Clock, Calendar, Settings } from 'lucide-react';
import { Loading } from '../components/ui/Loading';

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
  
  // Results state
  const [results, setResults] = useState<UserVerificationResult[]>([]);
  const [stats, setStats] = useState<BulkVerificationResponse | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'changes' | 'errors'>('all');
  
  // Schedule state
  const [schedules, setSchedules] = useState<VerificationSchedule[]>([]);
  const [loadingSchedules, setLoadingSchedules] = useState(false);
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
    }
  };
  
  const loadSchedules = async () => {
    setLoadingSchedules(true);
    try {
      const response = await fetch('/api/v1/admin/verification-schedule/schedules');
      if (!response.ok) throw new Error('Failed to load schedules');
      const data = await response.json();
      setSchedules(data);
    } catch (error) {
      console.error('Error loading schedules:', error);
    } finally {
      setLoadingSchedules(false);
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

  if (loadingChats) {
    return <Loading />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Проверка пользователей</h1>
        <p className="mt-2 text-sm text-gray-600">
          Автоматическая проверка информации о пользователях через Telegram API
        </p>
      </div>

      {/* Single User Verification */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Search className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">Проверить одного пользователя</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Выберите чат
            </label>
            <select
              value={singleChatId}
              onChange={(e) => setSingleChatId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Выберите чат...</option>
              {chats.map(chat => (
                <option key={chat.id} value={chat.id}>
                  {chat.title} ({chat.chat_type})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telegram User ID
            </label>
            <input
              type="number"
              value={telegramUserId}
              onChange={(e) => setTelegramUserId(e.target.value)}
              placeholder="Введите Telegram user ID"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="single-auto-update"
              checked={singleAutoUpdate}
              onChange={(e) => setSingleAutoUpdate(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="single-auto-update" className="text-sm text-gray-700">
              Автоматически обновлять данные при обнаружении изменений
            </label>
          </div>
          
          <button
            onClick={verifySingleUser}
            disabled={verifySingleLoading || !singleChatId || !telegramUserId}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {verifySingleLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Проверка...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                Проверить пользователя
              </>
            )}
          </button>
        </div>
      </div>

      {/* Bulk Verification */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <Users className="w-5 h-5 text-green-600" />
          <h2 className="text-lg font-semibold text-gray-900">Проверить активных пользователей</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Фильтр по чату (опционально)
            </label>
            <select
              value={bulkChatId}
              onChange={(e) => setBulkChatId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              <option value="">Все активные пользователи</option>
              {chats.map(chat => (
                <option key={chat.id} value={chat.id}>
                  {chat.title} ({chat.chat_type})
                </option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="bulk-auto-update"
              checked={bulkAutoUpdate}
              onChange={(e) => setBulkAutoUpdate(e.target.checked)}
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <label htmlFor="bulk-auto-update" className="text-sm text-gray-700">
              Автоматически обновлять данные при обнаружении изменений
            </label>
          </div>
          
          <button
            onClick={verifyActiveUsers}
            disabled={verifyBulkLoading}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
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

      {/* Scheduled Verification */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-purple-600" />
            <h2 className="text-lg font-semibold text-gray-900">Автоматическая проверка по расписанию</h2>
          </div>
          <button
            onClick={() => {
              setShowScheduleForm(true);
              setEditingScheduleId(null);
              setScheduleForm({
                enabled: true,
                schedule_time: '02:00',
                interval_hours: 24,
                auto_update: true,
                chat_id: ''
              });
            }}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Settings className="w-4 h-4" />
            Добавить расписание
          </button>
        </div>

        {showScheduleForm && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-md font-semibold text-gray-900 mb-4">
              {editingScheduleId ? 'Редактировать расписание' : 'Новое расписание'}
            </h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Время запуска
                  </label>
                  <input
                    type="time"
                    value={scheduleForm.schedule_time}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, schedule_time: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Интервал (часов)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="168"
                    value={scheduleForm.interval_hours}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, interval_hours: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Фильтр по чату (опционально)
                </label>
                <select
                  value={scheduleForm.chat_id}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, chat_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Все чаты</option>
                  {chats.map(chat => (
                    <option key={chat.id} value={chat.id}>
                      {chat.title} ({chat.chat_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="schedule-enabled"
                    checked={scheduleForm.enabled}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, enabled: e.target.checked })}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <label htmlFor="schedule-enabled" className="text-sm text-gray-700">
                    Включено
                  </label>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="schedule-auto-update"
                    checked={scheduleForm.auto_update}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, auto_update: e.target.checked })}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                  <label htmlFor="schedule-auto-update" className="text-sm text-gray-700">
                    Автообновление данных
                  </label>
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={saveSchedule}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                >
                  <CheckCircle className="w-4 h-4" />
                  Сохранить
                </button>
                <button
                  onClick={() => {
                    setShowScheduleForm(false);
                    setEditingScheduleId(null);
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                >
                  <XCircle className="w-4 h-4" />
                  Отмена
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-3">
          {schedules.length === 0 ? (
            <p className="text-gray-500 text-center py-4">Нет настроенных расписаний</p>
          ) : (
            schedules.map(schedule => (
              <div key={schedule.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${schedule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {schedule.enabled ? 'Активно' : 'Выключено'}
                      </span>
                      <span className="text-sm text-gray-600">
                        <Calendar className="w-4 h-4 inline mr-1" />
                        {schedule.schedule_time} каждые {schedule.interval_hours}ч
                      </span>
                      {schedule.chat_title && (
                        <span className="text-sm text-gray-600">
                          📱 {schedule.chat_title}
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 space-y-1">
                      {schedule.last_run_at && (
                        <div>Последний запуск: {new Date(schedule.last_run_at).toLocaleString('ru-RU')}</div>
                      )}
                      {schedule.next_run_at && (
                        <div>Следующий запуск: {new Date(schedule.next_run_at).toLocaleString('ru-RU')}</div>
                      )}
                      <div>Автообновление: {schedule.auto_update ? 'Да' : 'Нет'}</div>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => toggleSchedule(schedule.id)}
                      className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                        schedule.enabled 
                          ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' 
                          : 'bg-green-100 text-green-800 hover:bg-green-200'
                      }`}
                    >
                      {schedule.enabled ? 'Выключить' : 'Включить'}
                    </button>
                    <button
                      onClick={() => editSchedule(schedule)}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-sm font-medium hover:bg-blue-200 transition-colors"
                    >
                      Изменить
                    </button>
                    <button
                      onClick={() => deleteSchedule(schedule.id)}
                      className="px-3 py-1 bg-red-100 text-red-800 rounded text-sm font-medium hover:bg-red-200 transition-colors"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-600 mb-1">Проверено</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_checked}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-600 mb-1">С изменениями</div>
            <div className="text-2xl font-bold text-orange-600">{stats.total_with_changes}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-600 mb-1">Обновлено</div>
            <div className="text-2xl font-bold text-green-600">{stats.total_updated}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-600 mb-1">Ошибки</div>
            <div className="text-2xl font-bold text-red-600">{stats.total_errors}</div>
          </div>
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="text-sm text-gray-600 mb-1">Длительность</div>
            <div className="text-2xl font-bold text-blue-600">{stats.duration_seconds.toFixed(1)}с</div>
          </div>
        </div>
      )}

      {/* Filter Buttons */}
      {results.length > 0 && (
        <div className="flex gap-2">
          <button
            onClick={() => setFilterType('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Все результаты
          </button>
          <button
            onClick={() => setFilterType('changes')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'changes'
                ? 'bg-orange-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            С изменениями
          </button>
          <button
            onClick={() => setFilterType('errors')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filterType === 'errors'
                ? 'bg-red-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Только ошибки
          </button>
        </div>
      )}

      {/* Results Table */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Чат
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Изменения
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Статус в чате
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Время проверки
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {getFilteredResults().map((result, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {result.telegram_user_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.chat_title || result.chat_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {result.error ? (
                        <span className="inline-flex items-center gap-1 text-red-600 font-semibold">
                          <XCircle className="w-4 h-4" />
                          Ошибка
                        </span>
                      ) : result.is_updated ? (
                        <span className="inline-flex items-center gap-1 text-green-600 font-semibold">
                          <CheckCircle className="w-4 h-4" />
                          Обновлено
                        </span>
                      ) : result.has_changes ? (
                        <span className="inline-flex items-center gap-1 text-orange-600 font-semibold">
                          <AlertTriangle className="w-4 h-4" />
                          Есть изменения
                        </span>
                      ) : (
                        <span className="text-gray-500">Без изменений</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {result.error ? (
                        <div className="text-red-600">{result.error}</div>
                      ) : Object.keys(result.changes).length > 0 ? (
                        <div className="space-y-1">
                          {Object.entries(result.changes).map(([field, change]) => (
                            <div key={field} className="bg-yellow-50 px-2 py-1 rounded text-xs">
                              <strong>{field}:</strong> "{change.old_value || 'null'}" → "{change.new_value || 'null'}"
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {result.current_status || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(result.checked_at).toLocaleString('ru-RU')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
