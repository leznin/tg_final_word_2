import React from 'react';
import { DivideIcon as LucideIcon } from 'lucide-react';

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
      className={`relative overflow-hidden rounded-xl p-6 text-white cursor-pointer transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl ${gradient} ${onClick ? 'hover:opacity-90' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-white/80">{title}</p>
          <p className="text-3xl font-bold">{value.toLocaleString()}</p>
        </div>
        <Icon className="h-12 w-12 text-white/80" />
      </div>
      <div className="absolute top-0 right-0 w-32 h-32 rounded-full bg-white/10 translate-x-16 -translate-y-16"></div>
    </div>
  );
};