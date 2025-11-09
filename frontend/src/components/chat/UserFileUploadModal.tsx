import React, { useState, useRef, useEffect } from 'react';
import { Upload, X, FileText, CheckCircle, XCircle, AlertTriangle, RefreshCw, Users, Download } from 'lucide-react';
import { ProgressBar } from '../ui/ProgressBar';

interface UserVerificationResult {
  telegram_user_id: number;
  chat_id: number;
  chat_title: string | null;
  is_updated: boolean;
  has_changes: boolean;
  changes: Record<string, { old_value: string | null; new_value: string | null }>;
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

interface UserFileUploadModalProps {
  chatId: number;
  onClose: () => void;
  onSuccess?: () => void;
}

export const UserFileUploadModal: React.FC<UserFileUploadModalProps> = ({ chatId, onClose, onSuccess }) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedUserIds, setUploadedUserIds] = useState<number[]>([]);
  const [fileError, setFileError] = useState<string | null>(null);
  const [autoUpdate, setAutoUpdate] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [verificationProgress, setVerificationProgress] = useState<any>(null);
  const [results, setResults] = useState<UserVerificationResult[]>([]);
  const [stats, setStats] = useState<BulkVerificationResponse | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'changes' | 'errors'>('all');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const handleClose = () => {
    // If results exist and onSuccess callback is provided, call it before closing
    if (results.length > 0 && onSuccess) {
      onSuccess();
    }
    onClose();
  };

  // Parse TXT file with user IDs
  const parseUserIdsFile = (content: string): number[] => {
    const lines = content.split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);
    
    const userIds: number[] = [];
    const errors: string[] = [];
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const id = parseInt(line, 10);
      
      if (isNaN(id)) {
        errors.push(`Строка ${i + 1}: "${line}" не является числом`);
      } else if (id <= 0) {
        errors.push(`Строка ${i + 1}: ID должен быть положительным числом`);
      } else {
        userIds.push(id);
      }
    }
    
    if (errors.length > 0 && errors.length < 10) {
      setFileError(`Обнаружены ошибки:\n${errors.slice(0, 5).join('\n')}${errors.length > 5 ? '\n...' : ''}`);
    } else if (errors.length >= 10) {
      setFileError(`Обнаружено ${errors.length} ошибок в файле. Проверьте формат.`);
    }
    
    // Remove duplicates
    return [...new Set(userIds)];
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileError(null);
    setUploadedUserIds([]);
    setResults([]);
    setStats(null);

    // Check file extension
    if (!file.name.endsWith('.txt')) {
      setFileError('Пожалуйста, выберите файл с расширением .txt');
      return;
    }

    // Check file size (max 10 MB)
    if (file.size > 10 * 1024 * 1024) {
      setFileError('Файл слишком большой. Максимальный размер: 10 МБ');
      return;
    }

    setUploadedFile(file);

    // Read and parse file
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const userIds = parseUserIdsFile(content);
      
      if (userIds.length === 0) {
        setFileError('Файл не содержит валидных User ID');
        return;
      }

      if (userIds.length > 10000) {
        setFileError('Слишком много ID. Максимум: 10000');
        return;
      }

      setUploadedUserIds(userIds);
    };

    reader.onerror = () => {
      setFileError('Ошибка чтения файла');
    };

    reader.readAsText(file);
  };

  const startProgressPolling = () => {
    pollingIntervalRef.current = setInterval(async () => {
      try {
        const response = await fetch('/api/v1/admin/user-verification/status');
        const data = await response.json();
        setVerificationProgress(data);
        
        if (!data.is_running) {
          stopProgressPolling();
          setVerifying(false);
        }
      } catch (error) {
        console.error('Error polling progress:', error);
      }
    }, 1000);
  };

  const stopProgressPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  const verifyUsers = async () => {
    if (uploadedUserIds.length === 0) return;

    setVerifying(true);
    setVerificationProgress({ is_running: true, current_progress: 0, total_users: uploadedUserIds.length });
    startProgressPolling();

    try {
      const response = await fetch('/api/v1/admin/user-verification/verify-active-users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          telegram_user_ids: uploadedUserIds,
          auto_update: autoUpdate,
          delay_between_requests: 0.5
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Ошибка проверки');
      }

      const result: BulkVerificationResponse = await response.json();
      setResults(result.results);
      setStats(result);
      
      // Don't call onSuccess here - let user see results first
      // onSuccess will be called when modal is closed
    } catch (error: any) {
      console.error('Error verifying users:', error);
      alert('Ошибка проверки: ' + error.message);
    } finally {
      setVerifying(false);
      stopProgressPolling();
    }
  };

  const getFilteredResults = () => {
    if (!results) return [];
    
    switch (filterType) {
      case 'changes':
        return results.filter(r => r.has_changes);
      case 'errors':
        return results.filter(r => r.error);
      default:
        return results;
    }
  };

  const downloadResults = () => {
    if (!results || results.length === 0) return;

    const csvContent = [
      ['User ID', 'Статус', 'Изменения', 'Ошибка', 'Время проверки'].join(','),
      ...results.map(r => [
        r.telegram_user_id,
        r.current_status || 'N/A',
        r.has_changes ? Object.keys(r.changes).join('; ') : 'Нет',
        r.error || 'Нет',
        new Date(r.checked_at).toLocaleString('ru-RU')
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `verification_results_${chatId}_${Date.now()}.csv`;
    link.click();
  };

  useEffect(() => {
    return () => {
      stopProgressPolling();
    };
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex items-center justify-between">
          <div className="flex items-center">
            <Upload className="h-6 w-6 mr-3" />
            <div>
              <h2 className="text-xl font-bold">Загрузка файла с User ID</h2>
              <p className="text-sm text-blue-100">Проверка пользователей в чате</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-all"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* File Upload Section */}
          {!results || results.length === 0 ? (
            <div className="space-y-6">
              {/* Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-bold text-blue-900 mb-2 flex items-center">
                  <FileText className="h-4 w-4 mr-2" />
                  Формат файла
                </h3>
                <p className="text-sm text-blue-800 mb-2">
                  Загрузите TXT файл, где каждая строка содержит один Telegram User ID
                </p>
                <div className="bg-white rounded p-2 text-xs font-mono text-gray-700">
                  123456789<br/>
                  987654321<br/>
                  111222333<br/>
                  444555666
                </div>
              </div>

              {/* File Input */}
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full py-8 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all flex flex-col items-center justify-center"
                >
                  <Upload className="h-12 w-12 text-gray-400 mb-3" />
                  <span className="text-lg font-medium text-gray-700">
                    Нажмите для выбора файла
                  </span>
                  <span className="text-sm text-gray-500 mt-1">
                    Максимальный размер: 10 МБ, до 10000 ID
                  </span>
                </button>
              </div>

              {/* Error Display */}
              {fileError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start">
                    <AlertTriangle className="h-5 w-5 text-red-600 mr-2 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="font-bold text-red-900 mb-1">Ошибка</h4>
                      <p className="text-sm text-red-800 whitespace-pre-line">{fileError}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* File Info */}
              {uploadedFile && uploadedUserIds.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start">
                      <CheckCircle className="h-5 w-5 text-green-600 mr-2 flex-shrink-0 mt-0.5" />
                      <div>
                        <h4 className="font-bold text-green-900">Файл загружен успешно</h4>
                        <p className="text-sm text-green-800 mt-1">
                          <strong>{uploadedFile.name}</strong>
                        </p>
                        <p className="text-sm text-green-700 mt-1">
                          Найдено {uploadedUserIds.length} уникальных User ID
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Preview of IDs */}
                  <div className="bg-white rounded p-3 max-h-32 overflow-y-auto">
                    <div className="text-xs font-mono text-gray-700">
                      {uploadedUserIds.slice(0, 20).join(', ')}
                      {uploadedUserIds.length > 20 && '...'}
                    </div>
                  </div>
                </div>
              )}

              {/* Auto Update Checkbox */}
              {uploadedUserIds.length > 0 && (
                <label className="flex items-center gap-3 cursor-pointer p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all">
                  <input
                    type="checkbox"
                    checked={autoUpdate}
                    onChange={(e) => setAutoUpdate(e.target.checked)}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <span className="font-medium text-gray-900">Автообновление при изменениях</span>
                    <p className="text-sm text-gray-600">
                      Автоматически обновлять данные пользователей в базе при обнаружении изменений
                    </p>
                  </div>
                </label>
              )}

              {/* Progress Bar */}
              {verificationProgress && verificationProgress.is_running && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <RefreshCw className="w-5 h-5 text-blue-600 animate-spin mr-2" />
                      <span className="font-bold text-blue-900">Проверка пользователей...</span>
                    </div>
                    <span className="text-sm text-blue-700">
                      {verificationProgress.current_progress || 0} / {verificationProgress.total_users || uploadedUserIds.length}
                    </span>
                  </div>
                  <ProgressBar
                    progress={verificationProgress.current_progress || 0}
                    total={verificationProgress.total_users || uploadedUserIds.length}
                  />
                  <div className="flex items-center justify-between mt-3 text-xs text-blue-700">
                    <div className="flex items-center gap-4">
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
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* Results Section */
            <div className="space-y-4">
              {/* Stats Cards */}
              {stats && (
                <div className="grid grid-cols-4 gap-3">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-center">
                    <Users className="h-5 w-5 text-blue-600 mx-auto mb-1" />
                    <div className="text-2xl font-bold text-blue-900">{stats.total_checked}</div>
                    <div className="text-xs text-blue-700">Проверено</div>
                  </div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                    <CheckCircle className="h-5 w-5 text-green-600 mx-auto mb-1" />
                    <div className="text-2xl font-bold text-green-900">{stats.total_updated}</div>
                    <div className="text-xs text-green-700">Обновлено</div>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-center">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mx-auto mb-1" />
                    <div className="text-2xl font-bold text-yellow-900">{stats.total_with_changes}</div>
                    <div className="text-xs text-yellow-700">Изменений</div>
                  </div>
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                    <XCircle className="h-5 w-5 text-red-600 mx-auto mb-1" />
                    <div className="text-2xl font-bold text-red-900">{stats.total_errors}</div>
                    <div className="text-xs text-red-700">Ошибок</div>
                  </div>
                </div>
              )}

              {/* Filters */}
              <div className="flex items-center justify-between">
                <div className="flex gap-2">
                  <button
                    onClick={() => setFilterType('all')}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                      filterType === 'all'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Все ({results.length})
                  </button>
                  <button
                    onClick={() => setFilterType('changes')}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                      filterType === 'changes'
                        ? 'bg-yellow-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    С изменениями ({results.filter(r => r.has_changes).length})
                  </button>
                  <button
                    onClick={() => setFilterType('errors')}
                    className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                      filterType === 'errors'
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    С ошибками ({results.filter(r => r.error).length})
                  </button>
                </div>
                <button
                  onClick={downloadResults}
                  className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-all"
                >
                  <Download className="h-4 w-4" />
                  Скачать CSV
                </button>
              </div>

              {/* Results Table */}
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 sticky top-0">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 uppercase">User ID</th>
                        <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 uppercase">Статус</th>
                        <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 uppercase">Изменения</th>
                        <th className="px-3 py-2 text-left text-xs font-bold text-gray-700 uppercase">Время</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {getFilteredResults().map((result, index) => (
                        <tr key={index} className="hover:bg-gray-50 transition-colors">
                          <td className="px-3 py-2 whitespace-nowrap">
                            <span className="text-sm font-semibold text-gray-900">{result.telegram_user_id}</span>
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
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
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-700">
                                <AlertTriangle className="w-3 h-3" />
                                Изменения
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-gray-100 text-gray-700">
                                <CheckCircle className="w-3 h-3" />
                                Без изменений
                              </span>
                            )}
                          </td>
                          <td className="px-3 py-2">
                            {result.error ? (
                              <span className="text-xs text-red-600">{result.error}</span>
                            ) : result.has_changes ? (
                              <div className="text-xs text-gray-700">
                                {Object.keys(result.changes).join(', ')}
                              </div>
                            ) : (
                              <span className="text-xs text-gray-500">Нет изменений</span>
                            )}
                          </td>
                          <td className="px-3 py-2 whitespace-nowrap">
                            <span className="text-xs text-gray-600">
                              {new Date(result.checked_at).toLocaleTimeString('ru-RU')}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 p-4 bg-gray-50 flex items-center justify-end gap-3">
          {!results || results.length === 0 ? (
            <>
              <button
                onClick={handleClose}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-all"
              >
                Отмена
              </button>
              <button
                onClick={verifyUsers}
                disabled={verifying || uploadedUserIds.length === 0}
                className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
              >
                {verifying ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Проверка...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Проверить пользователей
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={downloadResults}
                className="flex items-center gap-2 px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-all"
              >
                <Download className="w-4 h-4" />
                Скачать CSV
              </button>
              <button
                onClick={handleClose}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
              >
                Закрыть
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
