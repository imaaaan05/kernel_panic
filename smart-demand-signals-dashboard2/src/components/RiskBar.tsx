import React from 'react';

interface RiskBarProps {
  value: number; // 1–100
  compact?: boolean;
}

export const RiskBar: React.FC<RiskBarProps> = ({ value, compact = false }) => {
  const pct = Math.min(100, Math.max(1, value));

  const getColor = (v: number) => {
    if (v >= 80) return { bar: 'bg-red-500', text: 'text-red-600', bg: 'bg-red-50', badge: 'bg-red-500' };
    if (v >= 60) return { bar: 'bg-orange-500', text: 'text-orange-600', bg: 'bg-orange-50', badge: 'bg-orange-500' };
    if (v >= 40) return { bar: 'bg-amber-400', text: 'text-amber-600', bg: 'bg-amber-50', badge: 'bg-amber-400' };
    return { bar: 'bg-emerald-500', text: 'text-emerald-600', bg: 'bg-emerald-50', badge: 'bg-emerald-500' };
  };

  const colors = getColor(pct);

  if (compact) {
    return (
      <div className="flex items-center gap-2 min-w-[100px]">
        <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${colors.bar}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className={`text-xs font-bold tabular-nums ${colors.text} w-7 text-right`}>{pct}</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center gap-2.5 px-2 py-1 rounded-lg ${colors.bg} min-w-[130px]`}>
      <div className="flex-1 h-2 bg-white/60 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${colors.bar}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-xs font-bold tabular-nums ${colors.text} min-w-[24px] text-right`}>{pct}</span>
    </div>
  );
};
