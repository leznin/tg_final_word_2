import React, { useState } from 'react';
import { MessageSquare, ChevronLeft, ChevronRight } from 'lucide-react';
import { useChatPosts } from '../../hooks/useChatPosts';
import { ChatPostCard } from './ChatPostCard';
import { Loading } from '../ui/Loading';

interface ChatPostsListProps {
  chatId: number;
}

export const ChatPostsList: React.FC<ChatPostsListProps> = ({ chatId }) => {
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading, refetch } = useChatPosts(chatId, page, pageSize);

  if (isLoading) {
    return <Loading />;
  }

  if (!data || data.posts.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-12 text-center">
        <MessageSquare className="h-12 w-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-600 font-medium mb-1">Постов пока нет</p>
        <p className="text-sm text-gray-500">
          Создайте первый пост для этого чата
        </p>
      </div>
    );
  }

  const totalPages = data.total_pages;

  return (
    <div className="space-y-4">
      {/* Posts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
        {data.posts.map((post) => (
          <ChatPostCard
            key={post.id}
            post={post}
            onUpdate={() => refetch()}
          />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Показано {((page - 1) * pageSize) + 1} - {Math.min(page * pageSize, data.total)} из {data.total}
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                disabled={page === 1}
                className="p-2 rounded-lg border border-gray-300 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="text-sm text-gray-700">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                disabled={page === totalPages}
                className="p-2 rounded-lg border border-gray-300 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
