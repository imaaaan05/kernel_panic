import { useState, useMemo, useCallback } from 'react';
import {
  Bell,
  Users,
  TrendingUp,
  Euro,
  Menu,
  Download,
  RefreshCw,
  Activity,
  BarChart3,
  AlertTriangle,
} from 'lucide-react';
import { parseEuropeanCSV, runEngine, generateDemoData, Alert, ProcessedResult } from './engine/dataEngine';
import { KPICard } from './components/KPICard';
import { AlertTable } from './components/AlertTable';
import { Sidebar } from './components/Sidebar';
import { MethodologyExpander } from './components/MethodologyExpander';
import { FileUpload } from './components/FileUpload';
import {
  AlertsByReasonChart,
  BlockDistributionChart,
  TopOpportunitiesChart,
  RiskDistributionChart,
} from './components/Charts';

export default function App() {
  const [result, setResult] = useState<ProcessedResult | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Filter state
  const [selectedBlock, setSelectedBlock] = useState('');
  const [minRisk, setMinRisk] = useState(1);
  const [selectedMotivo, setSelectedMotivo] = useState('');
  const [selectedLoyalty, setSelectedLoyalty] = useState('');

  // Active tab
  const [activeTab, setActiveTab] = useState<'alerts' | 'charts'>('alerts');

  const handleData = useCallback((text: string) => {
    setLoading(true);
    setError(null);
    try {
      const rows = parseEuropeanCSV(text);
      if (rows.length === 0) {
        setError('No valid data rows found. Check CSV format, separator (;), and column names.');
        setLoading(false);
        return;
      }
      const engineResult = runEngine(rows);
      setResult(engineResult);
      setAlerts(engineResult.alerts);
    } catch (e) {
      setError(`Processing error: ${String(e)}`);
    }
    setLoading(false);
  }, []);

  const handleDemo = useCallback(() => {
    setLoading(true);
    setError(null);
    setTimeout(() => {
      try {
        const rows = generateDemoData();
        const engineResult = runEngine(rows);
        setResult(engineResult);
        setAlerts(engineResult.alerts);
      } catch (e) {
        setError(`Demo error: ${String(e)}`);
      }
      setLoading(false);
    }, 600);
  }, []);

  const handleActionChange = useCallback((id: string, action: string) => {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, Register_Action: action } : a)));
  }, []);

  const handleReset = useCallback(() => {
    setResult(null);
    setAlerts([]);
    setError(null);
    setSelectedBlock('');
    setMinRisk(1);
    setSelectedMotivo('');
    setSelectedLoyalty('');
    setActiveTab('alerts');
  }, []);

  // Filter alerts
  const filteredAlerts = useMemo(() => {
    let f = alerts;
    if (selectedBlock) f = f.filter((a) => a.Analytical_Block === selectedBlock);
    if (selectedMotivo) f = f.filter((a) => a.Motivo === selectedMotivo);
    if (selectedLoyalty) f = f.filter((a) => a.Loyalty_Factor === selectedLoyalty);
    f = f.filter((a) => a.Nivel_de_Riesgo >= minRisk);
    return f;
  }, [alerts, selectedBlock, selectedMotivo, selectedLoyalty, minRisk]);

  // KPIs
  const kpis = useMemo(() => {
    const total = filteredAlerts.length;
    const uniqueClients = new Set(filteredAlerts.map((a) => a.Client_ID)).size;
    const highRisk = filteredAlerts.filter((a) => a.Nivel_de_Riesgo >= 70).length;
    const totalOpportunity = filteredAlerts.reduce((s, a) => s + a.Valor_Oportunidad, 0);
    return { total, uniqueClients, highRisk, totalOpportunity };
  }, [filteredAlerts]);

  const handleExportCSV = () => {
    if (!filteredAlerts.length) return;
    const headers = [
      'Client_ID', 'Product_Family', 'Analytical_Block', 'Motivo',
      'Nivel_de_Riesgo', 'Days_Since_Last', 'Valor_Oportunidad',
      'Loyalty_Factor', 'Register_Action',
    ];
    const rows = filteredAlerts.map((a) =>
      [
        a.Client_ID, a.Product_Family, a.Analytical_Block, a.Motivo,
        a.Nivel_de_Riesgo, a.Days_Since_Last,
        a.Valor_Oportunidad.toFixed(2), a.Loyalty_Factor, a.Register_Action,
      ].join(';')
    );
    const csv = [headers.join(';'), ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `smart_demand_signals_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
  };

  if (!result) {
    return (
      <FileUpload
        onData={handleData}
        onDemo={handleDemo}
        loading={loading}
        error={error}
      />
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      {/* ── Header ── */}
      <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-slate-100 shadow-sm">
        <div className="flex items-center gap-3 px-4 lg:px-6 py-3">
          {/* Mobile sidebar toggle */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-xl hover:bg-slate-100 transition-colors"
          >
            <Menu className="h-5 w-5 text-slate-600" />
          </button>

          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 shadow-md shadow-indigo-200 flex-shrink-0">
              <span className="text-lg">📡</span>
            </div>
            <div>
              <h1 className="font-bold text-slate-900 text-base leading-tight">Smart Demand Signals</h1>
              <p className="text-[10px] text-slate-400 font-medium leading-tight">
                Inibsa Commercial Intelligence · Reference date:{' '}
                <span className="font-bold text-indigo-500">{result.todayDate}</span>
              </p>
            </div>
          </div>

          <div className="flex-1" />

          {/* Status badge */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-semibold text-emerald-600">Engine Active</span>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleExportCSV}
              title="Export CSV"
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
            >
              <Download className="h-3.5 w-3.5" />
              Export
            </button>
            <button
              onClick={handleReset}
              title="Load new file"
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">New File</span>
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* ── Sidebar ── */}
        <Sidebar
          blockOptions={result.blockOptions}
          selectedBlock={selectedBlock}
          onBlockChange={setSelectedBlock}
          minRisk={minRisk}
          onMinRiskChange={setMinRisk}
          selectedMotivo={selectedMotivo}
          onMotivoChange={setSelectedMotivo}
          selectedLoyalty={selectedLoyalty}
          onLoyaltyChange={setSelectedLoyalty}
          onReset={() => {
            setSelectedBlock('');
            setMinRisk(1);
            setSelectedMotivo('');
            setSelectedLoyalty('');
          }}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* ── Main Content ── */}
        <main className="flex-1 min-w-0 px-4 lg:px-6 py-5 space-y-5">
          {/* ── KPI Cards ── */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <KPICard
              title="Total Alerts"
              value={kpis.total}
              subtitle={`of ${alerts.length} total generated`}
              icon={Bell}
              iconBg="bg-indigo-100"
              iconColor="text-indigo-600"
              accent="from-indigo-500 to-violet-500"
            />
            <KPICard
              title="Clients at Risk"
              value={kpis.uniqueClients}
              subtitle={`of ${result.totalClients} clients`}
              icon={Users}
              iconBg="bg-orange-100"
              iconColor="text-orange-600"
              accent="from-orange-500 to-red-500"
            />
            <KPICard
              title="High Risk"
              value={kpis.highRisk}
              subtitle="Score ≥ 70 · Critical"
              icon={AlertTriangle}
              iconBg="bg-red-100"
              iconColor="text-red-500"
              accent="from-red-500 to-rose-500"
            />
            <KPICard
              title="Total Opportunity"
              value={`€${kpis.totalOpportunity >= 1000 ? (kpis.totalOpportunity / 1000).toFixed(0) + 'k' : kpis.totalOpportunity.toFixed(0)}`}
              subtitle="Recoverable revenue"
              icon={Euro}
              iconBg="bg-emerald-100"
              iconColor="text-emerald-600"
              accent="from-emerald-500 to-teal-500"
            />
          </div>

          {/* ── Tabs ── */}
          <div className="flex items-center gap-1 bg-slate-100/80 rounded-xl p-1 w-fit">
            <button
              onClick={() => setActiveTab('alerts')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                activeTab === 'alerts'
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Activity className="h-3.5 w-3.5" />
              Alert Dashboard
              {filteredAlerts.length > 0 && (
                <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${activeTab === 'alerts' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-200 text-slate-500'}`}>
                  {filteredAlerts.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('charts')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
                activeTab === 'charts'
                  ? 'bg-white text-indigo-700 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <BarChart3 className="h-3.5 w-3.5" />
              Analytics
            </button>
          </div>

          {/* ── Alert Dashboard Tab ── */}
          {activeTab === 'alerts' && (
            <div className="space-y-4">
              {/* Alert breakdown pills */}
              <div className="flex flex-wrap gap-2 items-center">
                {[
                  { label: 'Ventana de Captura', color: 'bg-cyan-100 text-cyan-700 border-cyan-200' },
                  { label: 'Retraso anómalo en tiempo', color: 'bg-orange-100 text-orange-700 border-orange-200' },
                  { label: 'Caída drástica de volumen', color: 'bg-red-100 text-red-700 border-red-200' },
                ].map((m) => {
                  const count = filteredAlerts.filter((a) => a.Motivo === m.label).length;
                  return (
                    <button
                      key={m.label}
                      onClick={() => setSelectedMotivo(selectedMotivo === m.label ? '' : m.label)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-all duration-150 ${m.color} ${selectedMotivo === m.label ? 'ring-2 ring-offset-1 ring-indigo-400 shadow-sm' : 'opacity-80 hover:opacity-100'}`}
                    >
                      {m.label}
                      <span className="bg-white/70 px-1.5 py-0.5 rounded-full tabular-nums">{count}</span>
                    </button>
                  );
                })}
              </div>

              {/* Table Card */}
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm">
                <div className="flex items-center justify-between px-5 py-4 border-b border-slate-50">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-indigo-500" />
                    <h2 className="font-bold text-slate-800 text-sm">
                      Commercial Alert Registry
                    </h2>
                    <span className="text-xs text-slate-400 font-medium">
                      · sorted by Nivel de Riesgo
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">
                      {filteredAlerts.filter((a) => a.Register_Action !== '').length} actions registered
                    </span>
                  </div>
                </div>
                <div className="p-4">
                  <AlertTable alerts={filteredAlerts} onActionChange={handleActionChange} />
                </div>
              </div>
            </div>
          )}

          {/* ── Analytics Tab ── */}
          {activeTab === 'charts' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Alert Reasons */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-1">Alerts by Reason</h3>
                  <p className="text-xs text-slate-400 mb-4">Distribution of triggered alert rules</p>
                  <AlertsByReasonChart alerts={filteredAlerts} />
                </div>

                {/* Block Distribution */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-1">Block Distribution</h3>
                  <p className="text-xs text-slate-400 mb-4">Technical vs Commodities alert split</p>
                  <BlockDistributionChart alerts={filteredAlerts} />
                </div>

                {/* Risk Distribution */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-1">Risk Score Distribution</h3>
                  <p className="text-xs text-slate-400 mb-4">Nivel de Riesgo buckets (1–100)</p>
                  <RiskDistributionChart alerts={filteredAlerts} />
                </div>

                {/* Top Opportunities */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                  <h3 className="font-bold text-slate-800 text-sm mb-1">Top 8 Opportunities</h3>
                  <p className="text-xs text-slate-400 mb-4">Highest Valor_Oportunidad (€) · color = risk</p>
                  <TopOpportunitiesChart alerts={filteredAlerts} />
                </div>
              </div>

              {/* Summary stats */}
              <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
                <h3 className="font-bold text-slate-800 text-sm mb-4">Statistical Summary</h3>
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
                  {[
                    {
                      label: 'Avg Risk Score',
                      value: filteredAlerts.length > 0
                        ? Math.round(filteredAlerts.reduce((s, a) => s + a.Nivel_de_Riesgo, 0) / filteredAlerts.length)
                        : 0,
                      unit: '',
                      color: 'text-indigo-600',
                    },
                    {
                      label: 'Avg Days Overdue',
                      value: filteredAlerts.length > 0
                        ? Math.round(filteredAlerts.reduce((s, a) => s + a.Days_Since_Last, 0) / filteredAlerts.length)
                        : 0,
                      unit: 'd',
                      color: 'text-orange-600',
                    },
                    {
                      label: 'Avg Opportunity',
                      value: filteredAlerts.length > 0
                        ? '€' + Math.round(filteredAlerts.reduce((s, a) => s + a.Valor_Oportunidad, 0) / filteredAlerts.length).toLocaleString('es-ES')
                        : '€0',
                      unit: '',
                      color: 'text-emerald-600',
                    },
                    {
                      label: 'Technical Alerts',
                      value: filteredAlerts.filter((a) => a.Analytical_Block === 'Technical').length,
                      unit: '',
                      color: 'text-violet-600',
                    },
                    {
                      label: 'Commodities Alerts',
                      value: filteredAlerts.filter((a) => a.Analytical_Block === 'Commodities').length,
                      unit: '',
                      color: 'text-cyan-600',
                    },
                    {
                      label: 'Loyal Clients Flagged',
                      value: new Set(filteredAlerts.filter((a) => a.Loyalty_Factor === 'Loyal').map((a) => a.Client_ID)).size,
                      unit: '',
                      color: 'text-amber-600',
                    },
                  ].map((stat) => (
                    <div key={stat.label} className="text-center px-2">
                      <p className={`text-2xl font-bold tabular-nums ${stat.color}`}>
                        {stat.value}{stat.unit}
                      </p>
                      <p className="text-xs text-slate-400 mt-1 font-medium">{stat.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ── Methodology Expander ── */}
          <MethodologyExpander />

          {/* Footer */}
          <footer className="pb-6 text-center">
            <p className="text-xs text-slate-400">
              Smart Demand Signals · Inibsa Hackathon 2024 · Built with{' '}
              <span className="font-semibold text-indigo-400">100% Pandas rule-based engine</span>{' '}
              · Zero ML black boxes · Full explainability guaranteed
            </p>
          </footer>
        </main>
      </div>
    </div>
  );
}
