import React, { useState } from 'react';
import { X, Copy, Check, RefreshCw } from 'lucide-react';
import { AdminUser } from '../../types';
import { useResetAdminPassword } from '../../hooks/useAdminUsers';

interface EditManagerModalProps {
  manager: AdminUser;
  onClose: () => void;
}

export const EditManagerModal: React.FC<EditManagerModalProps> = ({
  manager,
  onClose,
}) => {
  const resetPassword = useResetAdminPassword();
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [newPassword, setNewPassword] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  const handleResetPassword = async () => {
    if (!window.confirm(`Вы уверены, что хотите сбросить пароль для ${manager.email}?`)) {
      return;
    }

    setIsResetting(true);
    try {
      const result = await resetPassword.mutateAsync(manager.id);
      setNewPassword(result.new_password);
      setShowPasswordReset(true);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при сбросе пароля');
    } finally {
      setIsResetting(false);
    }
  };

  const handleCopyPassword = async () => {
    if (newPassword) {
      try {
        await navigator.clipboard.writeText(newPassword);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (err) {
        console.error('Failed to copy password:', err);
      }
    }
  };

  const handleClose = () => {
    if (showPasswordReset && newPassword) {
      if (window.confirm('Вы скопировали новый пароль? После закрытия он больше не будет доступен.')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-xl font-bold">Редактирование менеджера</h2>
            <p className="text-sm text-gray-600 mt-1">{manager.email}</p>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {showPasswordReset && newPassword ? (
            <>
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm font-semibold text-green-800 mb-2">
                  ✓ Пароль успешно сброшен
                </p>
                <p className="text-xs text-green-700">
                  Новый пароль сгенерирован. Обязательно скопируйте и передайте его пользователю.
                </p>
              </div>

              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm font-semibold text-yellow-800 mb-2">
                  ⚠️ Важно: Сохраните этот пароль!
                </p>
                <p className="text-xs text-yellow-700">
                  После закрытия окна пароль больше не будет доступен.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email пользователя
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    readOnly
                    value={manager.email}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                  <button
                    type="button"
                    onClick={async () => {
                      await navigator.clipboard.writeText(manager.email);
                    }}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    title="Скопировать email"
                  >
                    <Copy className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Новый пароль
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    readOnly
                    value={newPassword}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleCopyPassword}
                    className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    title="Скопировать пароль"
                  >
                    {copied ? (
                      <Check className="w-5 h-5 text-green-600" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={manager.email}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Имя пользователя
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={manager.username || '—'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Роль
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={manager.role === 'admin' ? 'Администратор' : 'Менеджер'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Статус
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={manager.is_active ? 'Активен' : 'Неактивен'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                </div>
              </div>

              <div className="pt-4 border-t">
                <button
                  onClick={handleResetPassword}
                  disabled={isResetting}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <RefreshCw className={`w-5 h-5 ${isResetting ? 'animate-spin' : ''}`} />
                  <span>{isResetting ? 'Сброс пароля...' : 'Сбросить пароль'}</span>
                </button>
                <p className="mt-2 text-xs text-gray-500 text-center">
                  Будет сгенерирован новый случайный пароль
                </p>
              </div>
            </>
          )}
        </div>

        <div className="flex justify-end space-x-3 p-6 border-t">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};
