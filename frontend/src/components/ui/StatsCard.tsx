import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: number;
  icon: LucideIcon;
  gradient: string;
  onClick?: () => void;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  icon: Icon,
  gradient,
  onClick
}) => {
  return (
    <div 
      className={`relative overflow-hidden rounded-xl p-4 md:p-6 text-white cursor-pointer transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl touch-target ${gradient} ${onClick ? 'hover:opacity-90' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs md:text-sm font-medium text-white/80 truncate">{title}</p>
          <p className="text-xl md:text-3xl font-bold">{value.toLocaleString()}</p>
        </div>
        <Icon className="h-8 w-8 md:h-12 md:w-12 text-white/80 flex-shrink-0 ml-2" />
      </div>
      <div className="absolute top-0 right-0 w-24 h-24 md:w-32 md:h-32 rounded-full bg-white/10 translate-x-12 md:translate-x-16 -translate-y-12 md:-translate-y-16"></div>
    </div>
  );
};