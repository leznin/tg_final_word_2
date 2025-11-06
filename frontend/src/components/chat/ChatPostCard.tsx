import React, { useState, useEffect } from 'react';
import { Pin, Edit2, Trash2, Clock, Image as ImageIcon, Video, File as FileIcon, AlertCircle } from 'lucide-react';
import { ChatPost } from '../../types';
import { useDeleteChatPost, usePinChatPost, useUnpinChatPost } from '../../hooks/useChatPosts';
import { EditPostModal } from '../modals/EditPostModal';
import { getMediaUrl } from '../../utils/media';

interface ChatPostCardProps {
  post: ChatPost;
  onUpdate?: () => void;
}

export const ChatPostCard: React.FC<ChatPostCardProps> = ({ post, onUpdate }) => {
  const [showEditModal, setShowEditModal] = useState(false);
  const [timeUntilAction, setTimeUntilAction] = useState<string>('');
  
  const deletePostMutation = useDeleteChatPost();
  const pinPostMutation = usePinChatPost();
  const unpinPostMutation = useUnpinChatPost();

  // Update countdown timer
  useEffect(() => {
    const updateTimer = () => {
      const now = new Date();
      
      if (post.scheduled_unpin_at) {
        const unpinTime = new Date(post.scheduled_unpin_at);
        const diff = unpinTime.getTime() - now.getTime();
        
        if (diff > 0) {
          const minutes = Math.floor(diff / 60000);
          const seconds = Math.floor((diff % 60000) / 1000);
          setTimeUntilAction(`Открепление через ${minutes}м ${seconds}с`);
          return;
        }
      }
      
      if (post.scheduled_delete_at) {
        const deleteTime = new Date(post.scheduled_delete_at);
        const diff = deleteTime.getTime() - now.getTime();
        
        if (diff > 0) {
          const minutes = Math.floor(diff / 60000);
          const seconds = Math.floor((diff % 60000) / 1000);
          setTimeUntilAction(`Удаление через ${minutes}м ${seconds}с`);
          return;
        }
      }
      
      setTimeUntilAction('');
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [post.scheduled_unpin_at, post.scheduled_delete_at]);

  const handleDelete = async () => {
    if (!window.confirm('Вы уверены, что хотите удалить этот пост?')) {
      return;
    }

    try {
      await deletePostMutation.mutateAsync(post.id);
      onUpdate?.();
    } catch (error) {
      console.error('Failed to delete post:', error);
      alert('Не удалось удалить пост');
    }
  };

  const handleTogglePin = async () => {
    try {
      if (post.is_pinned) {
        await unpinPostMutation.mutateAsync(post.id);
      } else {
        await pinPostMutation.mutateAsync({ postId: post.id, pinRequest: {} });
      }
      onUpdate?.();
    } catch (error) {
      console.error('Failed to toggle pin:', error);
      alert('Не удалось изменить закрепление');
    }
  };

  const getMediaIcon = () => {
    if (post.media_type === 'photo') return <ImageIcon className="h-4 w-4" />;
    if (post.media_type === 'video') return <Video className="h-4 w-4" />;
    if (post.media_type === 'document') return <FileIcon className="h-4 w-4" />;
    return null;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        {/* Status Badge */}
        {!post.is_sent && (
          <div className="mb-3 bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-blue-600" />
              <div className="flex-1">
                <p className="text-xs font-medium text-blue-900">Запланирован</p>
                {post.scheduled_send_at && (
                  <p className="text-xs text-blue-700">
                    Отправка: {formatDate(post.scheduled_send_at)}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center space-x-2">
            {post.is_pinned && (
              <div className="flex items-center space-x-1 bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
                <Pin className="h-3 w-3" />
                <span>Закреплено</span>
              </div>
            )}
            {post.media_type && (
              <div className="flex items-center space-x-1 bg-gray-100 text-gray-700 px-2 py-1 rounded-full text-xs">
                {getMediaIcon()}
                <span>{post.media_type}</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setShowEditModal(true)}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              title="Редактировать"
            >
              <Edit2 className="h-4 w-4 text-gray-600" />
            </button>
            <button
              onClick={handleTogglePin}
              disabled={pinPostMutation.isPending || unpinPostMutation.isPending}
              className="p-1.5 hover:bg-blue-100 rounded-lg transition-colors disabled:opacity-50"
              title={post.is_pinned ? 'Открепить' : 'Закрепить'}
            >
              <Pin className={`h-4 w-4 ${post.is_pinned ? 'text-blue-600' : 'text-gray-600'}`} />
            </button>
            <button
              onClick={handleDelete}
              disabled={deletePostMutation.isPending}
              className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
              title="Удалить"
            >
              <Trash2 className="h-4 w-4 text-red-600" />
            </button>
          </div>
        </div>

        {/* Media Preview */}
        {post.media_type && post.media_url && (
          <div className="mb-3 bg-gray-50 rounded-lg overflow-hidden">
            {post.media_type === 'photo' && (
              <img 
                src={getMediaUrl(post.media_url)} 
                alt="Post media" 
                className="w-full h-48 object-cover rounded-lg"
                onError={(e) => {
                  // Fallback if image fails to load
                  e.currentTarget.style.display = 'none';
                  const parent = e.currentTarget.parentElement;
                  if (parent) {
                    parent.innerHTML = `
                      <div class="flex items-center justify-center h-48 bg-gray-100">
                        <div class="text-center">
                          <svg class="h-12 w-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                          <p class="text-sm text-gray-500">Изображение недоступно</p>
                        </div>
                      </div>
                    `;
                  }
                }}
              />
            )}
            
            {post.media_type === 'video' && (
              <div className="relative">
                <video 
                  src={getMediaUrl(post.media_url)}
                  controls
                  className="w-full h-48 object-cover rounded-lg"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    const parent = e.currentTarget.parentElement;
                    if (parent) {
                      parent.innerHTML = `
                        <div class="flex items-center justify-center h-48 bg-gray-100">
                          <div class="text-center">
                            <svg class="h-12 w-12 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            <p class="text-sm text-gray-500">Видео недоступно</p>
                          </div>
                        </div>
                      `;
                    }
                  }}
                >
                  Ваш браузер не поддерживает воспроизведение видео.
                </video>
                <div className="absolute top-2 left-2 bg-black bg-opacity-60 text-white px-2 py-1 rounded text-xs">
                  <Video className="h-3 w-3 inline mr-1" />
                  Видео
                </div>
              </div>
            )}
            
            {post.media_type === 'document' && (
              <div className="flex items-center space-x-3 p-4 bg-gray-100 rounded-lg">
                <div className="flex-shrink-0">
                  <FileIcon className="h-10 w-10 text-gray-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {post.media_filename || 'document'}
                  </p>
                  <p className="text-xs text-gray-500">Документ</p>
                  {post.media_url && (
                    <a
                      href={getMediaUrl(post.media_url)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Просмотреть документ →
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Content */}
        {post.content_text && (
          <div className="mb-3">
            <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
              {post.content_text}
            </p>
          </div>
        )}

        {/* Scheduled Actions Alert */}
        {timeUntilAction && (
          <div className="mb-3 flex items-center space-x-2 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2">
            <Clock className="h-4 w-4 text-yellow-600 flex-shrink-0" />
            <span className="text-xs text-yellow-700">{timeUntilAction}</span>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
          {post.is_sent ? (
            <>
              <span>Отправлен: {post.sent_at ? formatDate(post.sent_at) : formatDate(post.created_at)}</span>
              {post.updated_at !== post.created_at && (
                <span>Изменен: {formatDate(post.updated_at)}</span>
              )}
            </>
          ) : (
            <span>Создан: {formatDate(post.created_at)}</span>
          )}
        </div>

        {/* Telegram Message ID */}
        {post.telegram_message_id && (
          <div className="mt-2 text-xs text-gray-400">
            ID сообщения: {post.telegram_message_id}
          </div>
        )}
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <EditPostModal
          post={post}
          onClose={() => setShowEditModal(false)}
          onSuccess={() => {
            setShowEditModal(false);
            onUpdate?.();
          }}
        />
      )}
    </>
  );
};
