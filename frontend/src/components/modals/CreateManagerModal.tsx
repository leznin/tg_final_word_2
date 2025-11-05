import React, { useState } from 'react';
import { X, RefreshCw, Copy, Check, Shield } from 'lucide-react';
import { useCreateAdminUser } from '../../hooks/useAdminUsers';
import { UserRole } from '../../types';
import { Select } from '../ui/Select';

interface CreateManagerModalProps {
  onClose: () => void;
}

// Функция генерации надежного пароля
const generatePassword = (length: number = 16): string => {
  const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const lowercase = 'abcdefghijklmnopqrstuvwxyz';
  const numbers = '0123456789';
  const symbols = '!@#$%^&*';
  const allChars = uppercase + lowercase + numbers + symbols;
  
  let password = '';
  // Гарантируем наличие хотя бы одного символа каждого типа
  password += uppercase[Math.floor(Math.random() * uppercase.length)];
  password += lowercase[Math.floor(Math.random() * lowercase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += symbols[Math.floor(Math.random() * symbols.length)];
  
  // Добавляем оставшиеся символы
  for (let i = password.length; i < length; i++) {
    password += allChars[Math.floor(Math.random() * allChars.length)];
  }
  
  // Перемешиваем пароль
  return password.split('').sort(() => Math.random() - 0.5).join('');
};

export const CreateManagerModal: React.FC<CreateManagerModalProps> = ({ onClose }) => {
  const createAdmin = useCreateAdminUser();
  
  const [formData, setFormData] = useState({
    email: '',
    password: generatePassword(),
    username: '',
    role: UserRole.MANAGER,
    is_active: true,
  });
  
  const [error, setError] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [emailError, setEmailError] = useState<string>('');
  const [showSuccess, setShowSuccess] = useState(false);
  const [createdUser, setCreatedUser] = useState<{ email: string; password: string } | null>(null);

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setEmailError('Email обязателен');
      return false;
    }
    if (!emailRegex.test(email)) {
      setEmailError('Некорректный формат email');
      return false;
    }
    setEmailError('');
    return true;
  };

  const handleEmailChange = (email: string) => {
    setFormData({ ...formData, email });
    if (email) {
      validateEmail(email);
    } else {
      setEmailError('');
    }
  };

  const handleRegeneratePassword = () => {
    setFormData({ ...formData, password: generatePassword() });
    setCopied(false);
  };

  const handleCopyPassword = async () => {
    try {
      await navigator.clipboard.writeText(formData.password);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy password:', err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Валидация перед отправкой
    if (!validateEmail(formData.email)) {
      return;
    }
    
    if (formData.username && formData.username.length < 3) {
      setError('Имя пользователя должно быть минимум 3 символа');
      return;
    }
    
    try {
      await createAdmin.mutateAsync(formData);
      // Сохраняем данные для отображения
      setCreatedUser({
        email: formData.email,
        password: formData.password,
      });
      setShowSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании пользователя');
    }
  };

  // Если пользователь создан успешно, показываем экран с данными
  if (showSuccess && createdUser) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
          <div className="flex justify-between items-center p-6 border-b bg-green-50">
            <h2 className="text-xl font-bold text-green-800">✓ Пользователь создан</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          <div className="p-6 space-y-4">
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm font-semibold text-yellow-800 mb-2">
                ⚠️ Важно: Сохраните эти данные!
              </p>
              <p className="text-xs text-yellow-700">
                Пароль больше не будет показан. Обязательно передайте его пользователю.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  readOnly
                  value={createdUser.email}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50"
                />
                <button
                  type="button"
                  onClick={async () => {
                    await navigator.clipboard.writeText(createdUser.email);
                  }}
                  className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  title="Скопировать"
                >
                  <Copy className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Пароль
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  readOnly
                  value={createdUser.password}
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
          </div>

          <div className="flex justify-end p-6 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Закрыть
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold">Создать пользователя</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              required
              value={formData.email}
              onChange={(e) => handleEmailChange(e.target.value)}
              onBlur={(e) => validateEmail(e.target.value)}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                emailError ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="example@email.com"
            />
            {emailError && (
              <p className="mt-1 text-sm text-red-600">{emailError}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Пароль (автоматически сгенерирован) *
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                readOnly
                value={formData.password}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 font-mono text-sm"
              />
              <button
                type="button"
                onClick={handleRegeneratePassword}
                className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                title="Сгенерировать новый пароль"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
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
            <p className="mt-1 text-xs text-gray-500">
              ⚠️ Обязательно сохраните пароль - он не будет показан снова
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Имя пользователя
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Опционально"
            />
            <p className="mt-1 text-xs text-gray-500">
              Минимум 3 символа, если указано
            </p>
          </div>

          <Select
            label="Роль *"
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value as UserRole })}
            icon={<Shield className="w-5 h-5" />}
          >
            <option value={UserRole.ADMIN}>Администратор</option>
            <option value={UserRole.MANAGER}>Менеджер</option>
          </Select>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
              Активен
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={createAdmin.isPending || !!emailError}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createAdmin.isPending ? 'Создание...' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
