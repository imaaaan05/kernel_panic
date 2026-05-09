import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, Shield, Code2, GitBranch } from 'lucide-react';

export const MethodologyExpander: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50/60 to-slate-50 overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-6 py-4 hover:bg-white/50 transition-colors duration-200"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100">
            <BookOpen className="h-4 w-4 text-indigo-600" />
          </div>
          <div className="text-left">
            <p className="font-bold text-slate-800 text-sm">Methodology: 100% Pandas Rule-Based Engine</p>
            <p className="text-xs text-slate-500 mt-0.5">
              Full algorithmic transparency — no ML black boxes · Click to expand
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold">
            <Shield className="h-3 w-3" />
            Explainable AI
          </span>
          {open ? (
            <ChevronUp className="h-4 w-4 text-slate-400" />
          ) : (
            <ChevronDown className="h-4 w-4 text-slate-400" />
          )}
        </div>
      </button>

      {open && (
        <div className="px-6 pb-6 border-t border-indigo-100">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-5">
            {/* Step 1 */}
            <StepCard
              number="01"
              icon={<Code2 className="h-4 w-4 text-blue-600" />}
              iconBg="bg-blue-100"
              title="Data Ingestion & Cleaning"
              color="border-blue-200"
            >
              <ul className="space-y-1.5 text-xs text-slate-600">
                <li className="flex gap-2"><span className="text-blue-500 font-bold flex-shrink-0">▸</span>Read with <code className="bg-slate-100 px-1 rounded font-mono">pd.read_csv(sep=';', encoding='latin1', dtype=str)</code></li>
                <li className="flex gap-2"><span className="text-blue-500 font-bold flex-shrink-0">▸</span>European decimal repair: replace <code className="bg-slate-100 px-1 rounded font-mono">',' → '.'</code> then <code className="bg-slate-100 px-1 rounded font-mono">pd.to_numeric(errors='coerce')</code></li>
                <li className="flex gap-2"><span className="text-blue-500 font-bold flex-shrink-0">▸</span>Standardize <code className="bg-slate-100 px-1 rounded font-mono">Analytical_Block</code>: 'Productos Técnicos' → 'Technical'</li>
                <li className="flex gap-2"><span className="text-blue-500 font-bold flex-shrink-0">▸</span>Drop rows where <code className="bg-slate-100 px-1 rounded font-mono">Qty ≤ 0 OR Value ≤ 0</code></li>
              </ul>
            </StepCard>

            {/* Step 2 */}
            <StepCard
              number="02"
              icon={<GitBranch className="h-4 w-4 text-violet-600" />}
              iconBg="bg-violet-100"
              title="Feature Engineering"
              color="border-violet-200"
            >
              <ul className="space-y-1.5 text-xs text-slate-600">
                <li className="flex gap-2"><span className="text-violet-500 font-bold flex-shrink-0">▸</span><strong>Loyalty Factor</strong>: Group by Client_ID → monthly aggregation → Avg_Monthly_Spend</li>
                <li className="flex gap-2"><span className="text-violet-500 font-bold flex-shrink-0">▸</span>If <code className="bg-slate-100 px-1 rounded font-mono">Avg_Spend ≥ 0.85 × Max_Potential</code> → <strong>Loyal</strong>, else → <strong>Promiscuous</strong></li>
                <li className="flex gap-2"><span className="text-violet-500 font-bold flex-shrink-0">▸</span>Group by <code className="bg-slate-100 px-1 rounded font-mono">[Client, Date, Family]</code> → sum Qty & Value</li>
                <li className="flex gap-2"><span className="text-violet-500 font-bold flex-shrink-0">▸</span>Sort chronologically → compute <code className="bg-slate-100 px-1 rounded font-mono">Days_Between</code> per pair</li>
              </ul>
            </StepCard>

            {/* Step 3 */}
            <StepCard
              number="03"
              icon={<span className="text-amber-600 text-sm">σ</span>}
              iconBg="bg-amber-100"
              title="Statistical Engine & Cold Start"
              color="border-amber-200"
            >
              <ul className="space-y-1.5 text-xs text-slate-600">
                <li className="flex gap-2"><span className="text-amber-500 font-bold flex-shrink-0">▸</span>Per Client/Family pair: compute <code className="bg-slate-100 px-1 rounded font-mono">Mean(Qty)</code>, <code className="bg-slate-100 px-1 rounded font-mono">Std(Qty)</code>, <code className="bg-slate-100 px-1 rounded font-mono">Mean(Days)</code>, <code className="bg-slate-100 px-1 rounded font-mono">Std(Days)</code></li>
                <li className="flex gap-2"><span className="text-amber-500 font-bold flex-shrink-0">▸</span><strong>Cold Start</strong>: if purchases &lt; 3, fall back to global family statistics</li>
                <li className="flex gap-2"><span className="text-amber-500 font-bold flex-shrink-0">▸</span>Fill remaining NaN with 0</li>
                <li className="flex gap-2"><span className="text-amber-500 font-bold flex-shrink-0">▸</span>All statistics use <strong>sample std</strong> (ddof=1) for unbiased estimates</li>
              </ul>
            </StepCard>

            {/* Step 4 */}
            <StepCard
              number="04"
              icon={<span className="text-red-600 text-sm font-bold">!</span>}
              iconBg="bg-red-100"
              title="Alert Rules (Deterministic)"
              color="border-red-200"
            >
              <ul className="space-y-2 text-xs text-slate-600">
                <li className="flex gap-2">
                  <span className="text-cyan-500 font-bold flex-shrink-0">▸</span>
                  <div><strong className="text-cyan-700">Rule A – Ventana de Captura</strong> (Commodities + Promiscuous): fires when <code className="bg-slate-100 px-1 rounded font-mono">Days_Since_Last ≥ Mean_Days</code></div>
                </li>
                <li className="flex gap-2">
                  <span className="text-orange-500 font-bold flex-shrink-0">▸</span>
                  <div><strong className="text-orange-700">Rule B1 – Retraso anómalo</strong> (Technical): fires when <code className="bg-slate-100 px-1 rounded font-mono">Days_Since_Last &gt; (Mean_Days × Last_Qty/Mean_Qty) + 1.5σ</code></div>
                </li>
                <li className="flex gap-2">
                  <span className="text-red-500 font-bold flex-shrink-0">▸</span>
                  <div><strong className="text-red-700">Rule B2 – Caída de volumen</strong> (Technical): fires when <code className="bg-slate-100 px-1 rounded font-mono">Last_Qty &lt; Mean_Qty − 1.0σ</code></div>
                </li>
              </ul>
            </StepCard>

            {/* Step 5 - full width */}
            <div className="md:col-span-2">
              <StepCard
                number="05"
                icon={<span className="text-emerald-600 text-sm font-bold">#</span>}
                iconBg="bg-emerald-100"
                title="Prioritization Score — Nivel de Riesgo (1–100)"
                color="border-emerald-200"
              >
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-slate-600">
                  <div className="bg-white/70 rounded-xl p-3 border border-emerald-100">
                    <p className="font-bold text-slate-700 mb-1">Raw Score</p>
                    <code className="bg-slate-100 px-2 py-1 rounded block font-mono text-slate-600">
                      Avg_Tx_Value × (1 + Days_Delayed / Mean_Days)
                    </code>
                    <p className="mt-1.5 text-slate-500">Rewards both high-value clients and those most overdue relative to their expected cadence</p>
                  </div>
                  <div className="bg-white/70 rounded-xl p-3 border border-emerald-100">
                    <p className="font-bold text-slate-700 mb-1">Min-Max Normalization</p>
                    <code className="bg-slate-100 px-2 py-1 rounded block font-mono text-slate-600">
                      1 + ((x − min) / (max − min)) × 99
                    </code>
                    <p className="mt-1.5 text-slate-500">Maps all scores to the [1, 100] range. Rounded to integer. Always comparable across blocks.</p>
                  </div>
                  <div className="bg-white/70 rounded-xl p-3 border border-emerald-100">
                    <p className="font-bold text-slate-700 mb-1">ML Feedback Loop</p>
                    <p className="text-slate-500">The <strong>Register Action</strong> column (✅ / ❌) captures agent feedback per alert. This structured ground-truth data is the foundation for future supervised model training — fully auditable.</p>
                  </div>
                </div>
              </StepCard>
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mt-4 flex items-start gap-3 px-4 py-3 bg-white rounded-xl border border-slate-200">
            <Shield className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-slate-600">
              <strong className="text-slate-800">Zero Black-Box Guarantee:</strong> Every single alert in this system is generated by explicit, human-readable IF/THEN rules operating on standard descriptive statistics (mean, standard deviation). No neural networks, no gradient boosting, no embeddings. Every decision can be fully audited, explained, and overridden by a domain expert. The alert engine is implemented purely in Pandas and can be reviewed line by line.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

const StepCard: React.FC<{
  number: string;
  icon: React.ReactNode;
  iconBg: string;
  title: string;
  color: string;
  children: React.ReactNode;
}> = ({ number, icon, iconBg, title, color, children }) => (
  <div className={`bg-white rounded-xl border ${color} p-4`}>
    <div className="flex items-center gap-2 mb-3">
      <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${iconBg}`}>{icon}</div>
      <div>
        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Step {number}</span>
        <h4 className="text-xs font-bold text-slate-700 leading-tight">{title}</h4>
      </div>
    </div>
    {children}
  </div>
);
