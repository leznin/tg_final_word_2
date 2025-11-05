import React, { useState, useEffect } from 'react';
import { X, Check } from 'lucide-react';
import { useChats } from '../../hooks/useChats';
import { useManagerChats, useAssignChatsToManager } from '../../hooks/useManagerChatAccess';
import { AdminUser } from '../../types';

interface ManageChatAccessModalProps {
  manager: AdminUser;
  onClose: () => void;
}

export const ManageChatAccessModal: React.FC<ManageChatAccessModalProps> = ({
  manager,
  onClose,
}) => {
  const { data: allChats } = useChats();
  const { data: managerChats } = useManagerChats(manager.id);
  const assignChats = useAssignChatsToManager();
  
  const [selectedChatIds, setSelectedChatIds] = useState<number[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (managerChats) {
      setSelectedChatIds(managerChats.map(c => c.chat_id));
    }
  }, [managerChats]);

  const handleToggleChat = (chatId: number) => {
    setSelectedChatIds(prev =>
      prev.includes(chatId)
        ? prev.filter(id => id !== chatId)
        : [...prev, chatId]
    );
  };

  const handleSubmit = async () => {
    try {
      await assignChats.mutateAsync({
        admin_user_id: manager.id,
        chat_ids: selectedChatIds,
      });
      onClose();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при сохранении');
    }
  };

  const chats = allChats?.chats || [];
  const filteredChats = chats.filter(chat =>
    chat.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    String(chat.telegram_chat_id).includes(searchTerm)
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-6 border-b">
          <div>
            <h2 className="text-xl font-bold">Управление доступом к чатам</h2>
            <p className="text-sm text-gray-600 mt-1">{manager.email}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6 space-y-4 flex-1 overflow-y-auto">
          <div>
            <input
              type="text"
              placeholder="Поиск чатов..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="text-sm text-gray-600">
            Выбрано: {selectedChatIds.length} из {chats.length}
          </div>

          <div className="space-y-2">
            {filteredChats.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Чаты не найдены
              </div>
            ) : (
              filteredChats.map(chat => (
                <div
                  key={chat.id}
                  className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => handleToggleChat(chat.id)}
                >
                  <div className="flex-shrink-0">
                    <div
                      className={`w-5 h-5 border-2 rounded flex items-center justify-center ${
                        selectedChatIds.includes(chat.id)
                          ? 'bg-blue-600 border-blue-600'
                          : 'border-gray-300'
                      }`}
                    >
                      {selectedChatIds.includes(chat.id) && (
                        <Check className="w-3 h-3 text-white" />
                      )}
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">{chat.title || 'Без названия'}</div>
                    <div className="text-xs text-gray-500">
                      ID: {chat.telegram_chat_id} • {chat.chat_type}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-3 p-6 border-t">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Отмена
          </button>
          <button
            onClick={handleSubmit}
            disabled={assignChats.isPending}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {assignChats.isPending ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </div>
    </div>
  );
};
