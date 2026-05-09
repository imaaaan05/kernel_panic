import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { Alert } from '../engine/dataEngine';

// ─── Alert Distribution by Reason ─────────────────────────────────────────────
export const AlertsByReasonChart: React.FC<{ alerts: Alert[] }> = ({ alerts }) => {
  const counts: Record<string, number> = {};
  for (const a of alerts) {
    counts[a.Motivo] = (counts[a.Motivo] ?? 0) + 1;
  }
  const data = Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const COLORS: Record<string, string> = {
    'Ventana de Captura': '#06b6d4',
    'Retraso anómalo en tiempo': '#f97316',
    'Caída drástica de volumen': '#ef4444',
  };

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          tickLine={false}
          axisLine={false}
          width={80}
        />
        <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            background: '#1e293b',
            border: 'none',
            borderRadius: '10px',
            color: '#f8fafc',
            fontSize: '12px',
            padding: '8px 12px',
          }}
          itemStyle={{ color: '#e2e8f0' }}
          cursor={{ fill: '#f1f5f9' }}
        />
        <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={48}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] ?? '#818cf8'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// ─── Block Distribution Pie ────────────────────────────────────────────────────
export const BlockDistributionChart: React.FC<{ alerts: Alert[] }> = ({ alerts }) => {
  const counts: Record<string, number> = {};
  for (const a of alerts) {
    counts[a.Analytical_Block] = (counts[a.Analytical_Block] ?? 0) + 1;
  }
  const data = Object.entries(counts).map(([name, value]) => ({ name, value }));

  const COLORS: Record<string, string> = {
    Technical: '#818cf8',
    Commodities: '#22d3ee',
  };

  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={80}
          paddingAngle={4}
          dataKey="value"
        >
          {data.map((entry) => (
            <Cell key={entry.name} fill={COLORS[entry.name] ?? '#94a3b8'} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: '#1e293b',
            border: 'none',
            borderRadius: '10px',
            color: '#f8fafc',
            fontSize: '12px',
            padding: '8px 12px',
          }}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => (
            <span style={{ fontSize: '11px', color: '#64748b', fontWeight: 600 }}>{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

// ─── Top Opportunities Bar ─────────────────────────────────────────────────────
export const TopOpportunitiesChart: React.FC<{ alerts: Alert[] }> = ({ alerts }) => {
  const data = [...alerts]
    .sort((a, b) => b.Valor_Oportunidad - a.Valor_Oportunidad)
    .slice(0, 8)
    .map((a) => ({
      name: a.Client_ID,
      family: a.Product_Family,
      value: Math.round(a.Valor_Oportunidad),
      risk: a.Nivel_de_Riesgo,
    }));

  const getRiskColor = (risk: number) => {
    if (risk >= 70) return '#ef4444';
    if (risk >= 40) return '#f97316';
    return '#10b981';
  };

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 50, left: 10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
        <XAxis
          type="number"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => `€${(v / 1000).toFixed(0)}k`}
        />
        <YAxis
          dataKey="name"
          type="category"
          tick={{ fontSize: 10, fill: '#64748b', fontWeight: 600 }}
          tickLine={false}
          axisLine={false}
          width={70}
        />
        <Tooltip
          contentStyle={{
            background: '#1e293b',
            border: 'none',
            borderRadius: '10px',
            color: '#f8fafc',
            fontSize: '12px',
            padding: '8px 12px',
          }}
          formatter={(value) => [`€${Number(value ?? 0).toLocaleString('es-ES')}`, 'Opportunity']}
        />
        <Bar dataKey="value" radius={[0, 6, 6, 0]} maxBarSize={18}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={getRiskColor(entry.risk)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};

// ─── Risk Score Distribution ───────────────────────────────────────────────────
export const RiskDistributionChart: React.FC<{ alerts: Alert[] }> = ({ alerts }) => {
  const buckets = [
    { label: '1–20', min: 1, max: 20, color: '#10b981' },
    { label: '21–40', min: 21, max: 40, color: '#34d399' },
    { label: '41–60', min: 41, max: 60, color: '#fbbf24' },
    { label: '61–80', min: 61, max: 80, color: '#f97316' },
    { label: '81–100', min: 81, max: 100, color: '#ef4444' },
  ];

  const data = buckets.map((b) => ({
    label: b.label,
    count: alerts.filter((a) => a.Nivel_de_Riesgo >= b.min && a.Nivel_de_Riesgo <= b.max).length,
    color: b.color,
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
        <XAxis
          dataKey="label"
          tick={{ fontSize: 10, fill: '#94a3b8' }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis tick={{ fontSize: 10, fill: '#94a3b8' }} tickLine={false} axisLine={false} />
        <Tooltip
          contentStyle={{
            background: '#1e293b',
            border: 'none',
            borderRadius: '10px',
            color: '#f8fafc',
            fontSize: '12px',
            padding: '8px 12px',
          }}
          cursor={{ fill: '#f1f5f9' }}
        />
        <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={40}>
          {data.map((entry) => (
            <Cell key={entry.label} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
