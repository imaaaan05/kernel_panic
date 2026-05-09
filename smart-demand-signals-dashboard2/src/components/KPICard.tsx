import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  trend?: { value: string; positive: boolean };
  accent?: string;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  iconBg,
  iconColor,
  trend,
  accent = 'from-slate-800 to-slate-700',
}) => {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-all duration-300 group">
      {/* Accent bar */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r ${accent}`} />

      <div className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">{title}</p>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-slate-800 tabular-nums leading-none">{value}</span>
            </div>
            {subtitle && (
              <p className="text-xs text-slate-400 mt-1.5 font-medium">{subtitle}</p>
            )}
            {trend && (
              <div className={`inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded-full text-xs font-semibold ${trend.positive ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-500'}`}>
                <span>{trend.positive ? '▲' : '▼'}</span>
                <span>{trend.value}</span>
              </div>
            )}
          </div>
          <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${iconBg} group-hover:scale-110 transition-transform duration-300`}>
            <Icon className={`h-5 w-5 ${iconColor}`} strokeWidth={2} />
          </div>
        </div>
      </div>
    </div>
  );
};
