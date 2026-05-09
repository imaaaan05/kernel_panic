import React, { useState, useMemo } from 'react';
import { Alert } from '../engine/dataEngine';
import { RiskBar } from './RiskBar';
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react';

interface AlertTableProps {
  alerts: Alert[];
  onActionChange: (id: string, action: string) => void;
}

type SortKey = keyof Alert;
type SortDir = 'asc' | 'desc' | null;

const MOTIVO_BADGE: Record<string, { bg: string; text: string; dot: string }> = {
  'Ventana de Captura': {
    bg: 'bg-blue-50 border border-blue-200',
    text: 'text-blue-700',
    dot: 'bg-blue-500',
  },
  'Retraso anómalo en tiempo': {
    bg: 'bg-orange-50 border border-orange-200',
    text: 'text-orange-700',
    dot: 'bg-orange-500',
  },
  'Caída drástica de volumen': {
    bg: 'bg-red-50 border border-red-200',
    text: 'text-red-700',
    dot: 'bg-red-500',
  },
};

const ACTION_OPTIONS = ['', '✅ Success', '❌ False Positive'];

const ACTION_STYLE: Record<string, string> = {
  '': 'bg-slate-50 text-slate-400 border-slate-200',
  '✅ Success': 'bg-emerald-50 text-emerald-700 border-emerald-300 font-semibold',
  '❌ False Positive': 'bg-red-50 text-red-600 border-red-300 font-semibold',
};

export const AlertTable: React.FC<AlertTableProps> = ({ alerts, onActionChange }) => {
  const [sortKey, setSortKey] = useState<SortKey>('Nivel_de_Riesgo');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [page, setPage] = useState(0);
  const PAGE_SIZE = 15;

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : d === 'desc' ? null : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
    setPage(0);
  };

  const sorted = useMemo(() => {
    if (!sortDir) return alerts;
    return [...alerts].sort((a, b) => {
      const av = a[sortKey];
      const bv = b[sortKey];
      if (typeof av === 'number' && typeof bv === 'number') {
        return sortDir === 'asc' ? av - bv : bv - av;
      }
      return sortDir === 'asc'
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av));
    });
  }, [alerts, sortKey, sortDir]);

  const paginated = sorted.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);

  const SortIcon = ({ col }: { col: SortKey }) => {
    if (sortKey !== col || !sortDir) return <ChevronsUpDown className="h-3 w-3 text-slate-300" />;
    return sortDir === 'asc' ? (
      <ChevronUp className="h-3 w-3 text-indigo-500" />
    ) : (
      <ChevronDown className="h-3 w-3 text-indigo-500" />
    );
  };

  const ColHeader = ({
    col,
    label,
    align = 'left',
  }: {
    col: SortKey;
    label: string;
    align?: string;
  }) => (
    <th
      className={`px-4 py-3 text-${align} text-xs font-semibold text-slate-500 uppercase tracking-wider cursor-pointer select-none hover:text-slate-700 whitespace-nowrap`}
      onClick={() => handleSort(col)}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <SortIcon col={col} />
      </span>
    </th>
  );

  if (alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-slate-400">
        <div className="text-5xl mb-3">🔍</div>
        <p className="font-semibold text-slate-500">No alerts match your filters</p>
        <p className="text-sm mt-1">Try adjusting the sidebar filters</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-0">
      <div className="overflow-x-auto rounded-xl border border-slate-100">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-100">
              <ColHeader col="Client_ID" label="Client ID" />
              <ColHeader col="Product_Family" label="Product Family" />
              <ColHeader col="Analytical_Block" label="Block" />
              <ColHeader col="Motivo" label="Alert Reason" />
              <ColHeader col="Nivel_de_Riesgo" label="Risk Score" align="center" />
              <ColHeader col="Days_Since_Last" label="Days Since Last" align="right" />
              <ColHeader col="Valor_Oportunidad" label="Opportunity (€)" align="right" />
              <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider whitespace-nowrap">
                Register Action
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {paginated.map((alert, idx) => {
              const motivoStyle = MOTIVO_BADGE[alert.Motivo] ?? {
                bg: 'bg-slate-50 border border-slate-200',
                text: 'text-slate-600',
                dot: 'bg-slate-400',
              };
              const isEven = idx % 2 === 0;

              return (
                <tr
                  key={alert.id}
                  className={`group transition-colors duration-100 hover:bg-indigo-50/40 ${
                    isEven ? 'bg-white' : 'bg-slate-50/30'
                  }`}
                >
                  {/* Client ID */}
                  <td className="px-4 py-3">
                    <span className="font-mono text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                      {alert.Client_ID}
                    </span>
                  </td>

                  {/* Product Family */}
                  <td className="px-4 py-3">
                    <span className="font-medium text-slate-700">{alert.Product_Family}</span>
                  </td>

                  {/* Block */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                        alert.Analytical_Block === 'Technical'
                          ? 'bg-violet-100 text-violet-700'
                          : 'bg-cyan-100 text-cyan-700'
                      }`}
                    >
                      {alert.Analytical_Block === 'Technical' ? '⚙️' : '📦'} {alert.Analytical_Block}
                    </span>
                  </td>

                  {/* Alert Reason */}
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${motivoStyle.bg} ${motivoStyle.text}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full flex-shrink-0 ${motivoStyle.dot}`} />
                      {alert.Motivo}
                    </span>
                  </td>

                  {/* Risk Score */}
                  <td className="px-4 py-3">
                    <RiskBar value={alert.Nivel_de_Riesgo} />
                  </td>

                  {/* Days Since Last */}
                  <td className="px-4 py-3 text-right">
                    <span
                      className={`text-sm font-bold tabular-nums ${
                        alert.Days_Since_Last > 60
                          ? 'text-red-600'
                          : alert.Days_Since_Last > 30
                          ? 'text-orange-500'
                          : 'text-slate-600'
                      }`}
                    >
                      {alert.Days_Since_Last}d
                    </span>
                  </td>

                  {/* Opportunity Value */}
                  <td className="px-4 py-3 text-right">
                    <span className="text-sm font-bold text-emerald-600 tabular-nums">
                      €{alert.Valor_Oportunidad.toLocaleString('es-ES', { maximumFractionDigits: 0 })}
                    </span>
                  </td>

                  {/* Register Action */}
                  <td className="px-4 py-3">
                    <select
                      value={alert.Register_Action}
                      onChange={(e) => onActionChange(alert.id, e.target.value)}
                      className={`text-xs font-medium px-2.5 py-1.5 rounded-lg border cursor-pointer transition-all duration-200 outline-none focus:ring-2 focus:ring-indigo-300 ${
                        ACTION_STYLE[alert.Register_Action] ?? ACTION_STYLE['']
                      }`}
                    >
                      {ACTION_OPTIONS.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt || '— Select —'}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 px-1">
          <p className="text-xs text-slate-400">
            Showing {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, sorted.length)} of{' '}
            {sorted.length} alerts
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              ← Prev
            </button>
            {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
              const pageNum = totalPages <= 7 ? i : Math.max(0, Math.min(page - 3, totalPages - 7)) + i;
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`w-8 h-8 rounded-lg text-xs font-semibold transition-colors ${
                    pageNum === page
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-500 hover:bg-slate-100'
                  }`}
                >
                  {pageNum + 1}
                </button>
              );
            })}
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
