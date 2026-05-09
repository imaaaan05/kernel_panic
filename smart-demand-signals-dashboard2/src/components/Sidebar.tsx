import React from 'react';
import { SlidersHorizontal, X } from 'lucide-react';

interface SidebarProps {
  blockOptions: string[];
  selectedBlock: string;
  onBlockChange: (v: string) => void;
  minRisk: number;
  onMinRiskChange: (v: number) => void;
  selectedMotivo: string;
  onMotivoChange: (v: string) => void;
  selectedLoyalty: string;
  onLoyaltyChange: (v: string) => void;
  onReset: () => void;
  isOpen: boolean;
  onClose: () => void;
}

const MOTIVOS = ['', 'Ventana de Captura', 'Retraso anómalo en tiempo', 'Caída drástica de volumen'];
const LOYALTIES = ['', 'Loyal', 'Promiscuous'];

export const Sidebar: React.FC<SidebarProps> = ({
  blockOptions,
  selectedBlock,
  onBlockChange,
  minRisk,
  onMinRiskChange,
  selectedMotivo,
  onMotivoChange,
  selectedLoyalty,
  onLoyaltyChange,
  onReset,
  isOpen,
  onClose,
}) => {
  const hasFilters =
    selectedBlock !== '' || minRisk > 1 || selectedMotivo !== '' || selectedLoyalty !== '';

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full z-50 w-72 bg-white shadow-2xl border-r border-slate-100
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:relative lg:translate-x-0 lg:shadow-none lg:z-auto lg:block lg:h-auto lg:flex-shrink-0
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-indigo-600" />
              <span className="font-bold text-slate-800 text-sm">Filters</span>
              {hasFilters && (
                <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse" />
              )}
            </div>
            <button
              onClick={onClose}
              className="lg:hidden p-1 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <X className="h-4 w-4 text-slate-400" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-6">
            {/* Analytical Block */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Analytical Block
              </label>
              <div className="flex flex-col gap-1.5">
                {['', ...blockOptions].map((opt) => (
                  <button
                    key={opt}
                    onClick={() => onBlockChange(opt)}
                    className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 text-left ${
                      selectedBlock === opt
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <span className="text-base leading-none">
                      {opt === '' ? '🌐' : opt === 'Technical' ? '⚙️' : '📦'}
                    </span>
                    {opt === '' ? 'All Blocks' : opt}
                  </button>
                ))}
              </div>
            </div>

            {/* Alert Reason */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Alert Reason
              </label>
              <select
                value={selectedMotivo}
                onChange={(e) => onMotivoChange(e.target.value)}
                className="w-full text-sm px-3 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all"
              >
                {MOTIVOS.map((m) => (
                  <option key={m} value={m}>
                    {m || 'All Reasons'}
                  </option>
                ))}
              </select>
            </div>

            {/* Loyalty Factor */}
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                Loyalty Factor
              </label>
              <div className="flex gap-1.5">
                {LOYALTIES.map((l) => (
                  <button
                    key={l}
                    onClick={() => onLoyaltyChange(l)}
                    className={`flex-1 px-2 py-2 rounded-xl text-xs font-semibold transition-all duration-150 ${
                      selectedLoyalty === l
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                    }`}
                  >
                    {l === '' ? 'All' : l}
                  </button>
                ))}
              </div>
            </div>

            {/* Minimum Risk Score */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                  Min. Risk Score
                </label>
                <span
                  className={`text-sm font-bold px-2 py-0.5 rounded-lg tabular-nums ${
                    minRisk >= 70
                      ? 'bg-red-100 text-red-600'
                      : minRisk >= 40
                      ? 'bg-orange-100 text-orange-600'
                      : 'bg-slate-100 text-slate-600'
                  }`}
                >
                  {minRisk}
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={100}
                value={minRisk}
                onChange={(e) => onMinRiskChange(Number(e.target.value))}
                className="w-full h-2 rounded-full appearance-none cursor-pointer accent-indigo-600 bg-gradient-to-r from-emerald-300 via-amber-300 to-red-400"
              />
              <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-medium">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
              </div>

              {/* Risk thresholds */}
              <div className="mt-3 flex flex-col gap-1">
                {[
                  { label: 'High Risk', min: 70, color: 'bg-red-500' },
                  { label: 'Medium Risk', min: 40, color: 'bg-amber-400' },
                  { label: 'Low Risk', min: 1, color: 'bg-emerald-500' },
                ].map((t) => (
                  <button
                    key={t.label}
                    onClick={() => onMinRiskChange(t.min)}
                    className={`flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                      minRisk === t.min ? 'bg-slate-100' : 'hover:bg-slate-50'
                    } text-slate-600`}
                  >
                    <span className={`h-2 w-2 rounded-full ${t.color}`} />
                    {t.label} (≥ {t.min})
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Reset */}
          <div className="p-5 border-t border-slate-100">
            <button
              onClick={onReset}
              disabled={!hasFilters}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-500 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </aside>
    </>
  );
};
