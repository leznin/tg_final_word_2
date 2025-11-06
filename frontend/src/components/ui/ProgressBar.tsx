import React from 'react';

interface ProgressBarProps {
  progress: number; // 0-100
  total?: number;
  current?: number;
  label?: string;
  showPercentage?: boolean;
  showCount?: boolean;
  estimatedTimeRemaining?: number | null; // in seconds
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  total,
  current,
  label,
  showPercentage = true,
  showCount = true,
  estimatedTimeRemaining,
  className = '',
  size = 'md',
  variant = 'default'
}) => {
  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-4',
    lg: 'h-6'
  };

  const variantClasses = {
    default: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    danger: 'bg-red-600'
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) {
      return `${Math.round(seconds)}с`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      const secs = Math.round(seconds % 60);
      return `${minutes}м ${secs}с`;
    } else {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}ч ${minutes}м`;
    }
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Header with label and stats */}
      {(label || showPercentage || showCount) && (
        <div className="flex justify-between items-center mb-2 text-sm">
          <div className="flex items-center gap-2">
            {label && <span className="font-medium text-gray-700">{label}</span>}
            {showCount && current !== undefined && total !== undefined && (
              <span className="text-gray-500">
                ({current} / {total})
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {estimatedTimeRemaining !== null && estimatedTimeRemaining !== undefined && estimatedTimeRemaining > 0 && (
              <span className="text-xs text-gray-500">
                Осталось: {formatTime(estimatedTimeRemaining)}
              </span>
            )}
            {showPercentage && (
              <span className="font-semibold text-gray-900">
                {clampedProgress.toFixed(1)}%
              </span>
            )}
          </div>
        </div>
      )}

      {/* Progress bar */}
      <div className={`w-full ${sizeClasses[size]} bg-gray-200 rounded-full overflow-hidden`}>
        <div
          className={`${sizeClasses[size]} ${variantClasses[variant]} rounded-full transition-all duration-300 ease-out flex items-center justify-end pr-2`}
          style={{ width: `${clampedProgress}%` }}
        >
          {size === 'lg' && clampedProgress > 10 && (
            <span className="text-xs text-white font-semibold">
              {clampedProgress.toFixed(0)}%
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
