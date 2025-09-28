import React, { useState, useEffect } from 'react';
import { Key, Bot, DollarSign, FileText, Save, RefreshCw, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';
import { useOpenRouterSettings, useSaveOpenRouterSettings, useUpdateOpenRouterSettings, useOpenRouterModels, useOpenRouterBalance } from '../hooks/useOpenRouter';
import { Loading } from '../components/ui/Loading';
import { ModelSelector } from '../components/ModelSelector';
import { OpenRouterModel, OpenRouterSettingsCreate, OpenRouterSettingsUpdate } from '../types';

export const OpenRouter: React.FC = () => {
  const [apiKey, setApiKey] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [prompt, setPrompt] = useState('');
  const [isActive, setIsActive] = useState(true);
  const [showApiKey, setShowApiKey] = useState(false);

  const { data: settings, isLoading: settingsLoading, error: settingsError } = useOpenRouterSettings();
  const { data: models, isLoading: modelsLoading, refetch: refetchModels } = useOpenRouterModels();
  const { data: balance, isLoading: balanceLoading, refetch: refetchBalance } = useOpenRouterBalance();

  const saveMutation = useSaveOpenRouterSettings();
  const updateMutation = useUpdateOpenRouterSettings();

  const isLoading = settingsLoading || modelsLoading || balanceLoading;
  const isSaving = saveMutation.isPending || updateMutation.isPending;

  // Load existing settings
  useEffect(() => {
    if (settings) {
      setApiKey(settings.api_key);
      setSelectedModel(settings.selected_model || '');
      setPrompt(settings.prompt || '');
      setIsActive(settings.is_active);
      // Load models and balance when settings exist
      refetchModels();
      refetchBalance();
    } else {
      // Reset to defaults when no settings
      setApiKey('');
      setSelectedModel('');
      setPrompt('');
      setIsActive(true);
    }
  }, [settings, refetchModels, refetchBalance]);

  const handleSave = async () => {
    if (!apiKey.trim()) {
      alert('API ключ обязателен');
      return;
    }

    const settingsData: OpenRouterSettingsCreate = {
      api_key: apiKey.trim(),
      selected_model: selectedModel || undefined,
      prompt: prompt.trim() || undefined,
      is_active: isActive,
    };

    try {
      if (settings) {
        await updateMutation.mutateAsync(settingsData as OpenRouterSettingsUpdate);
      } else {
        await saveMutation.mutateAsync(settingsData);
      }
      // Refresh models and balance after successful save
      await refetchModels();
      await refetchBalance();
    } catch (error: any) {
      alert(`Ошибка сохранения: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleRefreshBalance = () => {
    refetchBalance();
  };

  const formatBalance = (credits: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 4,
      maximumFractionDigits: 4,
    }).format(credits);
  };

  if (isLoading) return <Loading />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                OpenRouter
              </h1>
              <p className="mt-2 text-slate-600">
                Настройка интеграции с OpenRouter API для работы с нейросетевыми моделями
              </p>
            </div>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <Save className="h-5 w-5" />
              <span>{isSaving ? 'Сохранение...' : 'Сохранить'}</span>
            </button>
          </div>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - API & Model */}
          <div className="lg:col-span-2 space-y-6">
            {/* API Key Card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Key className="h-5 w-5 text-blue-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900">API Конфигурация</h2>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    OpenRouter API Key
                  </label>
                  <div className="relative">
                    <input
                      type={showApiKey ? "text" : "password"}
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="w-full px-4 py-3 pr-12 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      placeholder="sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    />
                    <button
                      type="button"
                      onClick={() => setShowApiKey(!showApiKey)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      {showApiKey ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                    </button>
                  </div>
                  <p className="text-xs text-slate-500 mt-2">
                    Получить ключ:{' '}
                    <a
                      href="https://openrouter.ai/keys"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 underline"
                    >
                      openrouter.ai/keys
                    </a>
                  </p>
                </div>

                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="isActive"
                    checked={isActive}
                    onChange={(e) => setIsActive(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                  />
                  <label htmlFor="isActive" className="text-sm font-medium text-slate-700">
                    Активна интеграция
                  </label>
                </div>
              </div>
            </div>

            {/* Model Selection Card */}
            {settings && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Bot className="h-5 w-5 text-green-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-slate-900">Модель ИИ</h2>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Выберите модель
                    </label>
                    <ModelSelector
                      models={models?.models || []}
                      value={selectedModel}
                      onChange={setSelectedModel}
                      placeholder="Выберите модель..."
                      disabled={modelsLoading}
                    />
                    {modelsLoading && (
                      <p className="text-xs text-slate-500 mt-1">Загрузка моделей...</p>
                    )}
                  </div>

                  {selectedModel && (
                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-600" />
                        <span className="text-sm font-medium text-green-800">
                          {models?.models?.find(m => m.id === selectedModel)?.name}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Balance & Prompt */}
          <div className="space-y-6">
            {/* Balance Card */}
            {settings && (
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-amber-100 rounded-lg">
                      <DollarSign className="h-5 w-5 text-amber-600" />
                    </div>
                    <h2 className="text-lg font-semibold text-slate-900">Баланс</h2>
                  </div>
                  <button
                    onClick={handleRefreshBalance}
                    disabled={balanceLoading}
                    className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
                    title="Обновить баланс"
                  >
                    <RefreshCw className={`h-4 w-4 ${balanceLoading ? 'animate-spin' : ''}`} />
                  </button>
                </div>

                {balance ? (
                  <div className="space-y-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-amber-600">
                        {formatBalance(balance.balance.credits)}
                      </p>
                      <p className="text-sm text-slate-600">Доступно</p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="text-center p-2 bg-green-50 rounded-lg">
                        <p className="font-semibold text-green-700">
                          {formatBalance(balance.balance.total_credits)}
                        </p>
                        <p className="text-slate-600">Всего</p>
                      </div>
                      <div className="text-center p-2 bg-red-50 rounded-lg">
                        <p className="font-semibold text-red-700">
                          {formatBalance(balance.balance.total_usage)}
                        </p>
                        <p className="text-slate-600">Использовано</p>
                      </div>
                    </div>

                    <p className="text-xs text-slate-500 text-center">
                      {new Date(balance.last_updated).toLocaleString('ru-RU')}
                    </p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <AlertCircle className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-600">Загрузка баланса...</p>
                  </div>
                )}
              </div>
            )}

            {/* Prompt Card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <FileText className="h-5 w-5 text-purple-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900">Системный промпт</h2>
              </div>

              <div>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-all"
                  placeholder="Введите системный промпт для нейросетевой модели..."
                />
                <p className="text-xs text-slate-500 mt-2">
                  Опционально. Будет использоваться как системное сообщение для всех запросов.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {settingsError && settingsError.response?.status !== 404 && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-sm text-red-700">
                Ошибка загрузки настроек: {settingsError.message}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
