import React, { useRef, useState } from 'react';
import { Upload, FileText, AlertCircle, Loader2 } from 'lucide-react';

interface FileUploadProps {
  onData: (text: string) => void;
  onDemo: () => void;
  loading: boolean;
  error: string | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onData, onDemo, loading, error }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      onData(text);
    };
    reader.readAsText(file, 'latin1');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 flex items-center justify-center p-6">
      {/* Animated background orbs */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-cyan-600/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
      </div>

      <div className="relative w-full max-w-lg">
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-600 shadow-lg shadow-indigo-500/30 mb-4">
            <span className="text-3xl">📡</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-1">Smart Demand Signals</h1>
          <p className="text-indigo-300 font-medium text-sm">Commercial Intelligence Dashboard</p>
          <div className="flex items-center justify-center gap-2 mt-2">
            <span className="text-xs text-slate-500 font-mono bg-slate-800/60 px-2 py-0.5 rounded">Powered by</span>
            <span className="text-xs font-bold text-indigo-400">Inibsa Analytics</span>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 shadow-2xl">
          {/* Drop Zone */}
          <div
            className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 cursor-pointer ${
              dragging
                ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]'
                : 'border-slate-600 hover:border-indigo-500 hover:bg-indigo-500/5'
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFile(file);
              }}
            />
            {loading ? (
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-10 w-10 text-indigo-400 animate-spin" />
                <p className="text-slate-300 font-medium">Processing data pipeline...</p>
                <p className="text-xs text-slate-500">Running statistical engine</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-800 border border-slate-700">
                  <Upload className="h-6 w-6 text-indigo-400" />
                </div>
                <div>
                  <p className="font-semibold text-white mb-1">Upload database_clean.csv</p>
                  <p className="text-xs text-slate-400">Drag & drop or click to browse</p>
                  <p className="text-xs text-slate-500 mt-1">
                    European CSV format · sep=';' · encoding=latin1
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Error */}
          {error && (
            <div className="mt-4 flex items-start gap-2 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl">
              <AlertCircle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-red-300">{error}</p>
            </div>
          )}

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-slate-700" />
            <span className="text-xs text-slate-500 font-medium">or</span>
            <div className="flex-1 h-px bg-slate-700" />
          </div>

          {/* Demo Button */}
          <button
            onClick={onDemo}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold text-sm hover:from-indigo-500 hover:to-violet-500 transition-all duration-200 shadow-lg shadow-indigo-500/20 disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-indigo-500/30 hover:scale-[1.01] active:scale-[0.99]"
          >
            <span className="text-lg">🚀</span>
            Launch with Demo Data (12 clients · 8 families)
          </button>

          {/* Info pills */}
          <div className="flex flex-wrap gap-2 mt-5 justify-center">
            {[
              { icon: '⚡', label: '100% Pandas Engine' },
              { icon: '🔍', label: 'Zero Black Box' },
              { icon: '🎯', label: 'Rule-Based Alerts' },
              { icon: '📊', label: 'Min-Max Scoring' },
            ].map((pill) => (
              <span
                key={pill.label}
                className="inline-flex items-center gap-1.5 px-3 py-1 bg-slate-800/60 border border-slate-700 rounded-full text-xs text-slate-300 font-medium"
              >
                <span>{pill.icon}</span>
                {pill.label}
              </span>
            ))}
          </div>
        </div>

        {/* Expected schema */}
        <div className="mt-5 bg-slate-900/60 border border-slate-700/50 rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Expected CSV Schema</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5">
            {[
              ['Id.Cliente', 'Client ID'],
              ['Fecha', 'Date (DD/MM/YYYY)'],
              ['Familia_H', 'Product Family'],
              ['Unidades', 'Quantity (comma decimal)'],
              ['Valores_H', 'Transaction Value'],
              ['Potencial_H', 'Client Potential'],
              ['Bloque analítico', 'Analytical Block'],
            ].map(([raw, desc]) => (
              <div key={raw} className="flex items-center gap-1.5">
                <code className="text-[10px] font-mono text-cyan-400 bg-slate-800 px-1.5 py-0.5 rounded">{raw}</code>
                <span className="text-[10px] text-slate-500">→ {desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
