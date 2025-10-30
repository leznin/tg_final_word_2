import React from 'react';

export const Loading: React.FC = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin rounded-full h-10 w-10 border-2 border-gray-600 border-t-blue-500"></div>
  </div>
);