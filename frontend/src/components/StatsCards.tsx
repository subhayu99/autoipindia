import React from 'react';
import { TrendingUp, CheckCircle, Clock, FileText } from 'lucide-react';
import type { Trademark } from '../types';

interface StatsCardsProps {
  trademarks: Trademark[];
}

export const StatsCards: React.FC<StatsCardsProps> = ({ trademarks }) => {
  const total = trademarks.length;
  const registered = trademarks.filter((tm) =>
    tm.status.toLowerCase().includes('registered')
  ).length;
  const pending = trademarks.filter((tm) =>
    tm.status.toLowerCase().includes('pending') ||
    tm.status.toLowerCase().includes('examination')
  ).length;
  const other = total - registered - pending;

  const stats = [
    { label: 'Total Trademarks', value: total, icon: FileText, color: 'blue' },
    { label: 'Registered', value: registered, icon: CheckCircle, color: 'green' },
    { label: 'Pending', value: pending, icon: Clock, color: 'yellow' },
    { label: 'Other Status', value: other, icon: TrendingUp, color: 'purple' },
  ];

  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-700',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-200 dark:border-green-700',
    yellow: 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-700',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border-purple-200 dark:border-purple-700',
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        return (
          <div
            key={stat.label}
            className={`p-6 rounded-lg border-2 transition-colors ${colorClasses[stat.color as keyof typeof colorClasses]}`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium opacity-80">{stat.label}</p>
                <p className="text-3xl font-bold mt-2">{stat.value}</p>
              </div>
              <Icon className="w-10 h-10 opacity-50" />
            </div>
          </div>
        );
      })}
    </div>
  );
};
