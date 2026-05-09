import { useState, useMemo } from "react";

// ─── Types ─────────────────────────────────────────────────────────────────
type Block = "Commodities" | "Technical";
type Loyalty = "Loyal" | "Promiscuous";
type Motivo =
  | "Ventana de Captura"
  | "Retraso anómalo en tiempo"
  | "Caída drástica de volumen";
type Action = "" | "✅ Success" | "❌ False Positive";

interface Alert {
  id: number;
  client_id: string;
  product_family: string;
  analytical_block: Block;
  loyalty: Loyalty;
  motivo: Motivo;
  risk_score: number;
  days_since_last: number;
  oportunidad: number;
  mean_days: number;
  mean_qty: number;
  action: Action;
}

// ─── Synthetic Demo Data ─────────────────────────────────────────────────────
const DEMO_ALERTS: Alert[] = [
  { id:1,  client_id:"C001", product_family:"IMPLANTES BONE",       analytical_block:"Technical",    loyalty:"Loyal",       motivo:"Retraso anómalo en tiempo",    risk_score:97, days_since_last:62, oportunidad:3840, mean_days:21, mean_qty:5,   action:"" },
  { id:2,  client_id:"C014", product_family:"MOTOR ENDODONCIA",     analytical_block:"Technical",    loyalty:"Promiscuous",  motivo:"Retraso anómalo en tiempo",    risk_score:91, days_since_last:55, oportunidad:2980, mean_days:18, mean_qty:3,   action:"" },
  { id:3,  client_id:"C022", product_family:"LASER DIODO",          analytical_block:"Technical",    loyalty:"Promiscuous",  motivo:"Caída drástica de volumen",    risk_score:88, days_since_last:40, oportunidad:4200, mean_days:30, mean_qty:2,   action:"" },
  { id:4,  client_id:"C007", product_family:"ANESTESIA LOCAL",      analytical_block:"Commodities",  loyalty:"Promiscuous",  motivo:"Ventana de Captura",           risk_score:85, days_since_last:30, oportunidad:1750, mean_days:14, mean_qty:120, action:"" },
  { id:5,  client_id:"C019", product_family:"MEMBRANA GUIDED",      analytical_block:"Technical",    loyalty:"Loyal",       motivo:"Retraso anómalo en tiempo",    risk_score:79, days_since_last:48, oportunidad:5100, mean_days:25, mean_qty:4,   action:"" },
  { id:6,  client_id:"C003", product_family:"AGUJAS DENTALES",      analytical_block:"Commodities",  loyalty:"Promiscuous",  motivo:"Ventana de Captura",           risk_score:74, days_since_last:22, oportunidad:960,  mean_days:10, mean_qty:200, action:"" },
  { id:7,  client_id:"C011", product_family:"COMPOSITE NANO",       analytical_block:"Technical",    loyalty:"Promiscuous",  motivo:"Caída drástica de volumen",    risk_score:68, days_since_last:35, oportunidad:2200, mean_days:20, mean_qty:8,   action:"" },
  { id:8,  client_id:"C028", product_family:"BRACKET CERAMIC",      analytical_block:"Technical",    loyalty:"Loyal",       motivo:"Retraso anómalo en tiempo",    risk_score:61, days_since_last:44, oportunidad:3300, mean_days:28, mean_qty:15,  action:"" },
  { id:9,  client_id:"C005", product_family:"DESINFECTANTE A",      analytical_block:"Commodities",  loyalty:"Promiscuous",  motivo:"Ventana de Captura",           risk_score:55, days_since_last:18, oportunidad:640,  mean_days:12, mean_qty:80,  action:"" },
  { id:10, client_id:"C016", product_family:"IMPLANTES BONE",       analytical_block:"Technical",    loyalty:"Promiscuous",  motivo:"Caída drástica de volumen",    risk_score:50, days_since_last:29, oportunidad:1800, mean_days:21, mean_qty:5,   action:"" },
  { id:11, client_id:"C009", product_family:"ANESTESIA LOCAL",      analytical_block:"Commodities",  loyalty:"Promiscuous",  motivo:"Ventana de Captura",           risk_score:44, days_since_last:15, oportunidad:820,  mean_days:14, mean_qty:100, action:"" },
  { id:12, client_id:"C024", product_family:"MOTOR ENDODONCIA",     analytical_block:"Technical",    loyalty:"Loyal",       motivo:"Retraso anómalo en tiempo",    risk_score:38, days_since_last:38, oportunidad:1400, mean_days:30, mean_qty:2,   action:"" },
  { id:13, client_id:"C031", product_family:"COMPOSITE NANO",       analytical_block:"Technical",    loyalty:"Promiscuous",  motivo:"Caída drástica de volumen",    risk_score:29, days_since_last:25, oportunidad:900,  mean_days:20, mean_qty:6,   action:"" },
  { id:14, client_id:"C017", product_family:"AGUJAS DENTALES",      analytical_block:"Commodities",  loyalty:"Promiscuous",  motivo:"Ventana de Captura",           risk_score:21, days_since_last:11, oportunidad:350,  mean_days:10, mean_qty:150, action:"" },
  { id:15, client_id:"C008", product_family:"LASER DIODO",          analytical_block:"Technical",    loyalty:"Loyal",       motivo:"Retraso anómalo en tiempo",    risk_score:14, days_since_last:33, oportunidad:600,  mean_days:28, mean_qty:1,   action:"" },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────
function riskColor(score: number): string {
  if (score >= 70) return "#ff5252";
  if (score >= 40) return "#ffab40";
  return "#69f0ae";
}

function blockColor(block: Block) {
  return block === "Commodities"
    ? { color: "#ffb74d", bg: "rgba(255,152,0,0.15)",  border: "rgba(255,152,0,0.3)"  }
    : { color: "#64b5f6", bg: "rgba(33,150,243,0.15)", border: "rgba(33,150,243,0.3)" };
}
function motivoIcon(motivo: Motivo): string {
  if (motivo === "Ventana de Captura")         return "🎯";
  if (motivo === "Retraso anómalo en tiempo")  return "⏰";
  return "📉";
}
function fmtEur(n: number): string {
  return new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(n);
}

// ─── Sub-components ───────────────────────────────────────────────────────────
function KpiCard({
  label, value, delta, icon, accentColor,
}: { label: string; value: string; delta: string; icon: string; accentColor: string }) {
  return (
    <div style={{
      background: "linear-gradient(145deg,#1e2538,#252d40)",
      border: "1px solid rgba(255,255,255,0.07)",
      borderRadius: 14,
      padding: "22px 24px",
      position: "relative",
      overflow: "hidden",
      boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
      flex: "1 1 0",
      minWidth: 0,
    }}>
      <div style={{ position:"absolute", top:0, left:0, right:0, height:3, borderRadius:"14px 14px 0 0", background: accentColor }} />
      <div style={{ position:"absolute", top:16, right:18, fontSize:28, opacity:.14 }}>{icon}</div>
      <div style={{ fontSize:11, fontWeight:700, letterSpacing:"1.2px", textTransform:"uppercase", color:"#8892a4", marginBottom:10 }}>{label}</div>
      <div style={{ fontSize:34, fontWeight:900, color:"#f1f5f9", lineHeight:1, marginBottom:6 }}>{value}</div>
      <div style={{ fontSize:12, color:"#64748b" }}>{delta}</div>
    </div>
  );
}

function RiskBar({ score }: { score: number }) {
  const color = riskColor(score);
  return (
    <div style={{ display:"flex", alignItems:"center", gap:8, minWidth:120 }}>
      <div style={{ flex:1, background:"rgba(255,255,255,0.07)", borderRadius:99, height:7, overflow:"hidden" }}>
        <div style={{ width:`${score}%`, height:"100%", borderRadius:99, background: color, transition:"width 0.4s ease" }} />
      </div>
      <span style={{ fontSize:13, fontWeight:700, color, minWidth:26 }}>{score}</span>
    </div>
  );
}

function Pill({ text, color, bg, border }: { text:string; color:string; bg:string; border:string }) {
  return (
    <span style={{ display:"inline-block", padding:"2px 10px", borderRadius:20, fontSize:11, fontWeight:700, letterSpacing:.3, color, background:bg, border:`1px solid ${border}` }}>
      {text}
    </span>
  );
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:14, fontSize:15, fontWeight:700, color:"#e2e8f0" }}>
      {children}
      <div style={{ flex:1, height:1, background:"linear-gradient(90deg,rgba(255,255,255,0.1),transparent)", marginLeft:6 }} />
    </div>
  );
}

// ─── Bar Chart ────────────────────────────────────────────────────────────────
function SimpleBarChart({ data, color, height=140 }: { data:{label:string;value:number}[]; color:string; height?:number }) {
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div style={{ display:"flex", alignItems:"flex-end", gap:10, height, paddingTop:8 }}>
      {data.map(d => (
        <div key={d.label} style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", gap:4, height:"100%" }}>
          <div style={{ fontSize:11, fontWeight:700, color }}>
            {d.value}
          </div>
          <div style={{
            width:"100%", borderRadius:"4px 4px 0 0",
            background: color,
            height: `${Math.max((d.value / max) * (height - 36), 4)}px`,
            opacity:.85,
            transition:"height 0.4s ease",
          }} />
          <div style={{ fontSize:10, color:"#64748b", textAlign:"center", lineHeight:1.2, maxWidth:64 }}>
            {d.label}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Methodology Expander ─────────────────────────────────────────────────────
function MethodologyExpander() {
  const [open, setOpen] = useState(false);
  return (
    <div style={{ border:"1px solid rgba(255,255,255,0.07)", borderRadius:14, overflow:"hidden", marginTop:24 }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width:"100%", padding:"16px 20px", background:"rgba(255,255,255,0.02)",
          border:"none", cursor:"pointer", textAlign:"left", color:"#e2e8f0",
          fontSize:14, fontWeight:700, display:"flex", alignItems:"center", gap:10,
        }}
      >
        <span style={{ fontSize:18 }}>🔬</span>
        Methodology: Why This Is 100% Explainable (No Black Box)
        <span style={{ marginLeft:"auto", fontSize:18, transition:"transform 0.2s", transform: open ? "rotate(180deg)" : "rotate(0deg)" }}>⌄</span>
      </button>
      {open && (
        <div style={{ padding:"0 24px 24px", color:"#94a3b8", fontSize:13, lineHeight:1.8 }}>
          <hr style={{ border:"none", borderTop:"1px solid rgba(255,255,255,0.07)", margin:"0 0 20px" }} />

          {[
            {
              title: "1 · Data Ingestion & Decimal Parsing",
              color: "#2196f3",
              content: (
                <>
                  <p>European comma-decimals are handled before any computation:</p>
                  <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#90caf9", fontSize:12, whiteSpace:"pre" }}>
                    {`df[col] = df[col].str.replace(",", ".", regex=False)\ndf[col] = pd.to_numeric(df[col], errors="coerce")`}
                  </code>
                </>
              )
            },
            {
              title: "2 · Analytical Block Classification",
              color: "#ff9800",
              content: (
                <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#ffcc80", fontSize:12, whiteSpace:"pre" }}>
                  {`IF Family.upper() CONTAINS ['ANESTE' | 'AGUJA' | 'DESINFEC']:\n    → Commodities\nELSE:\n    → Technical`}
                </code>
              )
            },
            {
              title: "3 · Loyalty Factor",
              color: "#9c27b0",
              content: (
                <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#ce93d8", fontSize:12, whiteSpace:"pre" }}>
                  {`IF Avg_Monthly_Spend >= 0.85 × Max_Client_Potential:\n    → Loyal\nELSE:\n    → Promiscuous`}
                </code>
              )
            },
            {
              title: "4 · Statistical Engine + Cold-Start Fallback",
              color: "#4caf50",
              content: (
                <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#a5d6a7", fontSize:12, whiteSpace:"pre" }}>
                  {`Mean_Qty, Std_Qty     = per Client × Family\nMean_Days, Std_Days  = per Client × Family\n\nIf Purchase_Count < 3:\n    → Use global Product_Family mean/std`}
                </code>
              )
            },
            {
              title: "5 · Alert Rules A, B1, B2",
              color: "#f44336",
              content: (
                <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#ef9a9a", fontSize:12, whiteSpace:"pre" }}>
                  {`Rule A  — Commodities + Promiscuous + Days_Since >= Mean_Days\nRule B1 — Technical + Days_Since > Expected + 1.5×Std_Days\nRule B2 — Technical + Last_Qty < Mean_Qty - 1.0×Std_Qty`}
                </code>
              )
            },
            {
              title: "6 · Nivel de Riesgo (Prioritization Score)",
              color: "#00bcd4",
              content: (
                <code style={{ display:"block", background:"rgba(0,0,0,0.3)", borderRadius:8, padding:"10px 14px", color:"#80deea", fontSize:12, whiteSpace:"pre" }}>
                  {`Raw_Score = Avg_Value × (1 + Days_Delayed / Mean_Days)\nNivel_Riesgo = MinMax(Raw_Score) → integer [1, 100]`}
                </code>
              )
            },
          ].map(block => (
            <div key={block.title} style={{ borderLeft:`3px solid ${block.color}`, paddingLeft:16, marginBottom:20 }}>
              <div style={{ fontWeight:700, color:"#e2e8f0", marginBottom:8 }}>{block.title}</div>
              {block.content}
            </div>
          ))}

          <div style={{ background:"rgba(255,255,255,0.03)", borderRadius:10, overflow:"hidden", marginTop:8 }}>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12 }}>
              <thead>
                <tr style={{ background:"rgba(255,255,255,0.05)" }}>
                  {["Concern","Pandas Rule Engine","Black-Box ML"].map(h => (
                    <th key={h} style={{ padding:"10px 14px", textAlign:"left", color:"#e2e8f0", fontWeight:700 }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  ["Auditability",         "✅ Every output traceable", "❌ Opaque weights"],
                  ["GDPR Compliance",      "✅ Full explainability",    "⚠️ Requires XAI layer"],
                  ["Cold-start handling",  "✅ Explicit fallback rules","❌ Needs training data"],
                  ["Sales team trust",     "✅ \"I understand this\"",  "❌ \"Why did it flag me?\""],
                  ["Hackathon robustness", "✅ Zero training time",     "❌ Risk of overfitting"],
                ].map((row, i) => (
                  <tr key={i} style={{ borderTop:"1px solid rgba(255,255,255,0.05)", background: i%2===0?"transparent":"rgba(255,255,255,0.02)" }}>
                    {row.map((cell, j) => (
                      <td key={j} style={{ padding:"9px 14px", color: j===0?"#e2e8f0":"#94a3b8" }}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p style={{ marginTop:16, fontStyle:"italic", color:"#64748b", fontSize:12 }}>
            ✅ Smart Demand Signals — Built for Inibsa Hackathon · 100% Pandas · Zero Black-Box · Full Auditability
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [blockFilter, setBlockFilter] = useState<Set<Block>>(new Set(["Commodities","Technical"]));
  const [minRisk, setMinRisk] = useState(1);
  const [motivoFilter, setMotivoFilter] = useState<string>("All");
  const [activeTab, setActiveTab] = useState<"alerts"|"analytics"|"raw">("alerts");
  const [actions, setActions] = useState<Record<number, Action>>({});
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleBlock = (b: Block) => setBlockFilter(prev => {
    const next = new Set(prev);
    next.has(b) ? next.delete(b) : next.add(b);
    return next;
  });

  const filtered = useMemo(() => {
    return DEMO_ALERTS
      .filter(a => blockFilter.has(a.analytical_block))
      .filter(a => a.risk_score >= minRisk)
      .filter(a => motivoFilter === "All" || a.motivo === motivoFilter)
      .sort((a, b) => b.risk_score - a.risk_score);
  }, [blockFilter, minRisk, motivoFilter]);

  const totalAlerts   = filtered.length;
  const clientsAtRisk = new Set(filtered.map(a => a.client_id)).size;
  const highRisk      = filtered.filter(a => a.risk_score >= 70).length;
  const totalOpp      = filtered.reduce((s, a) => s + a.oportunidad, 0);

  // Analytics data
  const blockCounts = useMemo(() => [
    { label: "Commodities", value: filtered.filter(a=>a.analytical_block==="Commodities").length },
    { label: "Technical",   value: filtered.filter(a=>a.analytical_block==="Technical").length },
  ], [filtered]);

  const riskDist = useMemo(() => [
    { label: "Bajo (<40)",    value: filtered.filter(a=>a.risk_score<40).length },
    { label: "Medio (40-69)", value: filtered.filter(a=>a.risk_score>=40&&a.risk_score<70).length },
    { label: "Alto (≥70)",    value: filtered.filter(a=>a.risk_score>=70).length },
  ], [filtered]);

  const motivoCounts = useMemo(() => {
    const motivos: Motivo[] = ["Ventana de Captura","Retraso anómalo en tiempo","Caída drástica de volumen"];
    return motivos.map(m => ({ label: m.slice(0,18)+"…", value: filtered.filter(a=>a.motivo===m).length }));
  }, [filtered]);

  const top5Opp = useMemo(() => {
    const map: Record<string, number> = {};
    filtered.forEach(a => { map[a.client_id] = (map[a.client_id]||0) + a.oportunidad; });
    return Object.entries(map)
      .sort((a,b) => b[1]-a[1])
      .slice(0,5)
      .map(([label, value]) => ({ label, value }));
  }, [filtered]);

  return (
    <div style={{
      minHeight:"100vh",
      background:"linear-gradient(135deg,#0f1117 0%,#1a1d2e 50%,#0f1117 100%)",
      color:"#e2e8f0",
      fontFamily:"'Inter', sans-serif",
      display:"flex",
      flexDirection:"column",
    }}>

      {/* ── Header Banner ── */}
      <div style={{
        background:"linear-gradient(90deg,#1e3a5f 0%,#0d47a1 40%,#1565c0 70%,#1e3a5f 100%)",
        borderBottom:"1px solid rgba(66,165,245,0.25)",
        padding:"18px 28px",
        display:"flex", alignItems:"center", justifyContent:"space-between",
        boxShadow:"0 4px 24px rgba(13,71,161,0.4)",
        flexShrink:0,
      }}>
        <div style={{ display:"flex", alignItems:"center", gap:14 }}>
          <button
            onClick={() => setSidebarOpen(o=>!o)}
            style={{ background:"rgba(255,255,255,0.1)", border:"1px solid rgba(255,255,255,0.15)", borderRadius:8, padding:"6px 10px", cursor:"pointer", color:"#fff", fontSize:16, lineHeight:1 }}
          >
            ☰
          </button>
          <div>
            <div style={{ fontSize:22, fontWeight:900, color:"#fff", letterSpacing:"-0.5px" }}>
              📡 Smart Demand Signals
            </div>
            <div style={{ fontSize:12, color:"#90caf9", marginTop:2, letterSpacing:".3px" }}>
              Inibsa · Commercial Intelligence Engine · 100% Rule-Based · Zero Black-Box
            </div>
          </div>
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:12 }}>
          <span style={{ background:"rgba(255,255,255,0.1)", border:"1px solid rgba(255,255,255,0.2)", borderRadius:20, padding:"5px 14px", fontSize:11, color:"#bbdefb", fontWeight:700, letterSpacing:.5 }}>
            ⚡ HACKATHON LIVE
          </span>
          <span style={{ background:"rgba(105,240,174,0.15)", border:"1px solid rgba(105,240,174,0.3)", borderRadius:20, padding:"5px 14px", fontSize:11, color:"#69f0ae", fontWeight:700 }}>
            🟢 ENGINE ACTIVE
          </span>
          <div style={{ fontSize:12, color:"#64748b" }}>
            {new Date().toLocaleDateString("es-ES", { day:"2-digit", month:"short", year:"numeric" })}
          </div>
        </div>
      </div>

      <div style={{ display:"flex", flex:1, overflow:"hidden" }}>

        {/* ── Sidebar ── */}
        {sidebarOpen && (
          <div style={{
            width:260,
            background:"linear-gradient(180deg,#141824 0%,#1a1f30 100%)",
            borderRight:"1px solid rgba(255,255,255,0.06)",
            padding:"20px 16px",
            overflowY:"auto",
            flexShrink:0,
          }}>
            {/* Brand */}
            <div style={{ background:"linear-gradient(135deg,#0d47a1,#1565c0)", borderRadius:12, padding:16, textAlign:"center", marginBottom:20, border:"1px solid rgba(66,165,245,0.2)" }}>
              <div style={{ fontSize:24, marginBottom:4 }}>🦷</div>
              <div style={{ fontSize:15, fontWeight:800, color:"#fff" }}>Inibsa</div>
              <div style={{ fontSize:11, color:"#90caf9", marginTop:2 }}>Smart Demand Signals v1.0</div>
            </div>

            <div style={{ fontSize:12, fontWeight:700, letterSpacing:"1px", textTransform:"uppercase", color:"#4a5568", marginBottom:10 }}>Data Source</div>
            <div style={{ background:"rgba(33,150,243,0.1)", border:"1px solid rgba(33,150,243,0.2)", borderRadius:8, padding:"10px 12px", fontSize:12, color:"#90caf9", marginBottom:20, lineHeight:1.5 }}>
              ℹ️ Using <strong style={{color:"#bbdefb"}}>synthetic demo dataset</strong><br/>30 clients · 9 product families
            </div>

            <hr style={{ border:"none", borderTop:"1px solid rgba(255,255,255,0.06)", margin:"0 0 16px" }} />

            <div style={{ fontSize:12, fontWeight:700, letterSpacing:"1px", textTransform:"uppercase", color:"#4a5568", marginBottom:10 }}>🔎 Filters</div>

            {/* Block filter */}
            <div style={{ marginBottom:16 }}>
              <div style={{ fontSize:12, color:"#8892a4", marginBottom:6, fontWeight:500 }}>Analytical Block</div>
              {(["Commodities","Technical"] as Block[]).map(b => {
                const bc = blockColor(b);
                const active = blockFilter.has(b);
                return (
                  <button key={b} onClick={() => toggleBlock(b)} style={{
                    display:"flex", alignItems:"center", gap:8, width:"100%",
                    background: active ? bc.bg : "transparent",
                    border: `1px solid ${active ? bc.border : "rgba(255,255,255,0.07)"}`,
                    borderRadius:8, padding:"8px 12px", cursor:"pointer",
                    color: active ? bc.color : "#64748b", fontSize:13, fontWeight:600,
                    marginBottom:6, transition:"all .15s",
                  }}>
                    <span style={{ width:8, height:8, borderRadius:"50%", background: active ? bc.color : "#374151", flexShrink:0 }} />
                    {b}
                  </button>
                );
              })}
            </div>

            {/* Risk slider */}
            <div style={{ marginBottom:16 }}>
              <div style={{ fontSize:12, color:"#8892a4", marginBottom:6, fontWeight:500, display:"flex", justifyContent:"space-between" }}>
                <span>Min Risk Score</span>
                <span style={{ color: riskColor(minRisk), fontWeight:700 }}>{minRisk}</span>
              </div>
              <input type="range" min={1} max={100} value={minRisk}
                onChange={e => setMinRisk(Number(e.target.value))}
                style={{ width:"100%", accentColor:"#2196f3" }}
              />
            </div>

            {/* Motivo filter */}
            <div style={{ marginBottom:20 }}>
              <div style={{ fontSize:12, color:"#8892a4", marginBottom:6, fontWeight:500 }}>Alert Type (Motivo)</div>
              {["All","Ventana de Captura","Retraso anómalo en tiempo","Caída drástica de volumen"].map(m => (
                <button key={m} onClick={() => setMotivoFilter(m)} style={{
                  display:"block", width:"100%", textAlign:"left",
                  background: motivoFilter===m ? "rgba(33,150,243,0.15)" : "transparent",
                  border:`1px solid ${motivoFilter===m ? "rgba(33,150,243,0.3)" : "rgba(255,255,255,0.06)"}`,
                  borderRadius:7, padding:"7px 10px", cursor:"pointer",
                  color: motivoFilter===m ? "#64b5f6" : "#64748b", fontSize:12,
                  marginBottom:5, fontWeight: motivoFilter===m ? 700 : 400,
                }}>
                  {m === "All" ? "🔘 All" : `${motivoIcon(m as Motivo)} ${m}`}
                </button>
              ))}
            </div>

            <hr style={{ border:"none", borderTop:"1px solid rgba(255,255,255,0.06)", margin:"0 0 14px" }} />
            <div style={{ fontSize:12, fontWeight:700, letterSpacing:"1px", textTransform:"uppercase", color:"#4a5568", marginBottom:10 }}>📊 Legend</div>
            {[{l:"Alto (≥70)",c:"#ff5252"},{l:"Medio (40-69)",c:"#ffab40"},{l:"Bajo (<40)",c:"#69f0ae"}].map(({l,c})=>(
              <div key={l} style={{ display:"flex", alignItems:"center", gap:8, marginBottom:7, fontSize:12, color:"#8892a4" }}>
                <div style={{ width:10, height:10, borderRadius:"50%", background:c, flexShrink:0 }}/>
                <span style={{ color:c, fontWeight:600 }}>{l}</span>
              </div>
            ))}

            <div style={{ marginTop:20, fontSize:11, color:"#374151", textAlign:"center" }}>
              Engine clock: {new Date().toLocaleTimeString("es-ES")}
            </div>
          </div>
        )}

        {/* ── Main Content ── */}
        <div style={{ flex:1, overflowY:"auto", padding:"24px 28px" }}>

          {/* KPI Cards */}
          <div style={{ display:"flex", gap:14, marginBottom:26 }}>
            <KpiCard label="Total Alerts"      value={String(totalAlerts)}       delta="Filtered result set"        icon="📡" accentColor="linear-gradient(90deg,#2196f3,#42a5f5)" />
            <KpiCard label="Clients at Risk"   value={String(clientsAtRisk)}     delta="Unique client accounts"     icon="👤" accentColor="linear-gradient(90deg,#ff9800,#ffb74d)" />
            <KpiCard label="High Risk (≥70)"   value={String(highRisk)}          delta="Immediate action needed"    icon="🔥" accentColor="linear-gradient(90deg,#f44336,#ef5350)" />
            <KpiCard label="Total Opportunity" value={fmtEur(totalOpp)}          delta="Recoverable revenue"        icon="💶" accentColor="linear-gradient(90deg,#4caf50,#66bb6a)" />
          </div>

          {/* Tabs */}
          <div style={{ display:"flex", gap:6, marginBottom:20, background:"rgba(255,255,255,0.03)", borderRadius:10, padding:5, border:"1px solid rgba(255,255,255,0.06)", width:"fit-content" }}>
            {(["alerts","analytics","raw"] as const).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)} style={{
                padding:"8px 20px", borderRadius:8, border:"none", cursor:"pointer",
                background: activeTab===tab ? "linear-gradient(90deg,#0d47a1,#1565c0)" : "transparent",
                color: activeTab===tab ? "#fff" : "#94a3b8",
                fontSize:13, fontWeight:600, transition:"all .15s",
              }}>
                {tab==="alerts" ? "🚨 Alert Dashboard" : tab==="analytics" ? "📈 Analytics" : "🗃️ Raw Data"}
              </button>
            ))}
          </div>

          {/* ── Tab: Alert Dashboard ── */}
          {activeTab === "alerts" && (
            <div>
              <SectionHeader>
                🚨 Live Alert Table
                <span style={{ fontSize:12, color:"#64748b", fontWeight:400, marginLeft:4 }}>
                  — {totalAlerts} signals detected · sorted by Nivel de Riesgo
                </span>
              </SectionHeader>

              {filtered.length === 0 ? (
                <div style={{ textAlign:"center", padding:"60px 20px", color:"#4a5568" }}>
                  <div style={{ fontSize:48, marginBottom:16 }}>✅</div>
                  <div style={{ fontSize:16, fontWeight:600 }}>No alerts match the current filters.</div>
                  <div style={{ fontSize:13, marginTop:8 }}>Adjust the sidebar criteria to see results.</div>
                </div>
              ) : (
                <div style={{ background:"rgba(255,255,255,0.02)", borderRadius:14, border:"1px solid rgba(255,255,255,0.06)", overflow:"hidden" }}>
                  {/* Table header */}
                  <div style={{
                    display:"grid",
                    gridTemplateColumns:"100px 1fr 110px 1fr 140px 90px 110px 100px 160px",
                    gap:0,
                    padding:"12px 16px",
                    background:"rgba(255,255,255,0.04)",
                    borderBottom:"1px solid rgba(255,255,255,0.07)",
                    fontSize:11, fontWeight:700, letterSpacing:"0.8px", textTransform:"uppercase", color:"#4a5568",
                  }}>
                    <div>Client ID</div>
                    <div>Product Family</div>
                    <div>Block</div>
                    <div>Motivo</div>
                    <div>Nivel de Riesgo</div>
                    <div>Days Silent</div>
                    <div>Oportunidad €</div>
                    <div>Loyalty</div>
                    <div>Register Action</div>
                  </div>

                  {/* Table rows */}
                  {filtered.map((alert, i) => {
                    const bc   = blockColor(alert.analytical_block);
                    const curAction = actions[alert.id] ?? "";
                    return (
                      <div key={alert.id} style={{
                        display:"grid",
                        gridTemplateColumns:"100px 1fr 110px 1fr 140px 90px 110px 100px 160px",
                        gap:0,
                        padding:"13px 16px",
                        borderBottom: i < filtered.length-1 ? "1px solid rgba(255,255,255,0.04)" : "none",
                        background: i%2===0 ? "transparent" : "rgba(255,255,255,0.015)",
                        alignItems:"center",
                        fontSize:13,
                        transition:"background .15s",
                      }}>
                        <div style={{ fontWeight:700, color:"#e2e8f0", fontSize:12 }}>{alert.client_id}</div>
                        <div style={{ color:"#94a3b8", fontSize:12, paddingRight:8 }}>{alert.product_family}</div>
                        <div><Pill text={alert.analytical_block} color={bc.color} bg={bc.bg} border={bc.border}/></div>
                        <div style={{ display:"flex", alignItems:"center", gap:5, color:"#c9d1e0", fontSize:12 }}>
                          <span>{motivoIcon(alert.motivo)}</span>
                          <span>{alert.motivo}</span>
                        </div>
                        <div><RiskBar score={alert.risk_score}/></div>
                        <div style={{ color:"#64b5f6", fontWeight:700 }}>{alert.days_since_last}d</div>
                        <div style={{ color:"#69f0ae", fontWeight:700 }}>{fmtEur(alert.oportunidad)}</div>
                        <div>
                          <Pill
                            text={alert.loyalty}
                            color={alert.loyalty==="Loyal"?"#a5d6a7":"#ffcc80"}
                            bg={alert.loyalty==="Loyal"?"rgba(76,175,80,0.12)":"rgba(255,152,0,0.12)"}
                            border={alert.loyalty==="Loyal"?"rgba(76,175,80,0.3)":"rgba(255,152,0,0.3)"}
                          />
                        </div>
                        <div>
                          <select
                            value={curAction}
                            onChange={e => setActions(prev => ({ ...prev, [alert.id]: e.target.value as Action }))}
                            style={{
                              background:"rgba(255,255,255,0.05)",
                              border:`1px solid ${curAction==="✅ Success"?"rgba(76,175,80,0.4)":curAction==="❌ False Positive"?"rgba(244,67,54,0.4)":"rgba(255,255,255,0.1)"}`,
                              borderRadius:7, padding:"5px 8px", color:"#e2e8f0", fontSize:12,
                              cursor:"pointer", outline:"none", width:"100%",
                              fontFamily:"inherit",
                            }}
                          >
                            <option value="">— Tag result —</option>
                            <option value="✅ Success">✅ Success</option>
                            <option value="❌ False Positive">❌ False Positive</option>
                          </select>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Feedback summary */}
              {(() => {
                const tagged   = Object.values(actions).filter(a => a !== "");
                const success  = Object.values(actions).filter(a => a === "✅ Success").length;
                const fp       = Object.values(actions).filter(a => a === "❌ False Positive").length;
                if (tagged.length === 0) return null;
                return (
                  <div style={{
                    marginTop:16, padding:"12px 16px",
                    background:"rgba(76,175,80,0.08)", border:"1px solid rgba(76,175,80,0.2)", borderRadius:10,
                    fontSize:13, color:"#a5d6a7",
                  }}>
                    🔁 <strong>Feedback captured:</strong> {success} success{success!==1?"es":""}, {fp} false positive{fp!==1?"s":""}. In production, this retrains the threshold parameters automatically.
                  </div>
                );
              })()}

              {/* Export row */}
              <div style={{ marginTop:16, display:"flex", alignItems:"center", gap:12 }}>
                <button
                  onClick={() => {
                    const csv = [
                      "Client_ID,Product_Family,Analytical_Block,Motivo,Nivel_de_Riesgo,Days_Since_Last,Valor_Oportunidad,Loyalty_Factor",
                      ...filtered.map(a =>
                        `${a.client_id},${a.product_family},${a.analytical_block},"${a.motivo}",${a.risk_score},${a.days_since_last},${a.oportunidad},${a.loyalty}`
                      )
                    ].join("\n");
                    const blob = new Blob([csv], { type:"text/csv" });
                    const url  = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url; link.download = `smart_demand_signals_${Date.now()}.csv`;
                    link.click(); URL.revokeObjectURL(url);
                  }}
                  style={{
                    background:"linear-gradient(90deg,#0d47a1,#1565c0)", border:"none",
                    borderRadius:8, padding:"10px 20px", color:"#fff",
                    fontSize:13, fontWeight:600, cursor:"pointer",
                    boxShadow:"0 4px 12px rgba(13,71,161,0.3)", transition:"all .15s",
                  }}
                >
                  ⬇️ Export Alerts CSV
                </button>
                <span style={{ fontSize:12, color:"#374151" }}>
                  Last refresh: {new Date().toLocaleTimeString("es-ES")}
                </span>
              </div>
            </div>
          )}

          {/* ── Tab: Analytics ── */}
          {activeTab === "analytics" && (
            <div>
              {filtered.length === 0 ? (
                <div style={{ textAlign:"center", padding:"60px 20px", color:"#4a5568" }}>
                  <div style={{ fontSize:36 }}>📊</div>
                  <div style={{ marginTop:12 }}>No data available for current filters.</div>
                </div>
              ) : (
                <>
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20, marginBottom:20 }}>
                    {[
                      { title:"🍰 Alerts by Analytical Block", data:blockCounts,  color:"#2196f3" },
                      { title:"📊 Risk Score Distribution",    data:riskDist,     color:"#ff9800" },
                      { title:"🔔 Alerts by Motivo",           data:motivoCounts, color:"#4caf50" },
                      { title:"💶 Top 5 Opportunity Clients",  data:top5Opp,      color:"#e91e63" },
                    ].map(({ title, data, color }) => (
                      <div key={title} style={{
                        background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)",
                        borderRadius:14, padding:"20px 20px 16px",
                      }}>
                        <SectionHeader>{title}</SectionHeader>
                        <SimpleBarChart data={data} color={color} />
                      </div>
                    ))}
                  </div>

                  {/* Stats table */}
                  <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:14, padding:"20px", overflow:"hidden" }}>
                    <SectionHeader>📋 Statistical Summary</SectionHeader>
                    <div style={{ overflowX:"auto" }}>
                      <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
                        <thead>
                          <tr style={{ background:"rgba(255,255,255,0.04)" }}>
                            {["Metric","Count","Mean","Std","Min","Max"].map(h => (
                              <th key={h} style={{ padding:"10px 14px", textAlign:"left", color:"#8892a4", fontWeight:700, fontSize:11, letterSpacing:".8px", textTransform:"uppercase" }}>{h}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {[
                            { name:"Nivel de Riesgo",  vals: filtered.map(a=>a.risk_score) },
                            { name:"Days Silent",       vals: filtered.map(a=>a.days_since_last) },
                            { name:"Oportunidad (€)",   vals: filtered.map(a=>a.oportunidad) },
                          ].map(({ name, vals }, i) => {
                            const n   = vals.length;
                            const avg = vals.reduce((a,b)=>a+b,0)/n;
                            const std = Math.sqrt(vals.reduce((a,b)=>a+(b-avg)**2,0)/n);
                            const mn  = Math.min(...vals);
                            const mx  = Math.max(...vals);
                            return (
                              <tr key={name} style={{ borderTop:"1px solid rgba(255,255,255,0.05)", background:i%2?"rgba(255,255,255,0.02)":"transparent" }}>
                                <td style={{ padding:"10px 14px", color:"#e2e8f0", fontWeight:600 }}>{name}</td>
                                <td style={{ padding:"10px 14px", color:"#94a3b8" }}>{n}</td>
                                <td style={{ padding:"10px 14px", color:"#94a3b8" }}>{avg.toFixed(1)}</td>
                                <td style={{ padding:"10px 14px", color:"#94a3b8" }}>{std.toFixed(1)}</td>
                                <td style={{ padding:"10px 14px", color:"#94a3b8" }}>{mn.toFixed(1)}</td>
                                <td style={{ padding:"10px 14px", color:"#94a3b8" }}>{mx.toFixed(1)}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* ── Tab: Raw Data ── */}
          {activeTab === "raw" && (
            <div>
              <SectionHeader>🗃️ Ingested Dataset — {DEMO_ALERTS.length} demo alert records</SectionHeader>
              <div style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:14, overflow:"hidden" }}>
                <div style={{
                  display:"grid",
                  gridTemplateColumns:"80px 80px 1fr 110px 90px 90px 90px 90px 90px",
                  padding:"11px 16px",
                  background:"rgba(255,255,255,0.04)", borderBottom:"1px solid rgba(255,255,255,0.07)",
                  fontSize:11, fontWeight:700, letterSpacing:".8px", textTransform:"uppercase", color:"#4a5568",
                }}>
                  {["ID","Client","Product Family","Block","Risk","Days","Opp €","Motivo Type","Loyalty"].map(h=><div key={h}>{h}</div>)}
                </div>
                {DEMO_ALERTS.map((a,i) => {
                  const bc = blockColor(a.analytical_block);
                  return (
                    <div key={a.id} style={{
                      display:"grid",
                      gridTemplateColumns:"80px 80px 1fr 110px 90px 90px 90px 90px 90px",
                      padding:"10px 16px",
                      borderBottom: i<DEMO_ALERTS.length-1?"1px solid rgba(255,255,255,0.04)":"none",
                      background: i%2?"rgba(255,255,255,0.015)":"transparent",
                      fontSize:12, alignItems:"center", color:"#94a3b8",
                    }}>
                      <div style={{ color:"#64748b" }}>#{a.id}</div>
                      <div style={{ fontWeight:700, color:"#e2e8f0" }}>{a.client_id}</div>
                      <div style={{ fontSize:11 }}>{a.product_family}</div>
                      <div><Pill text={a.analytical_block} color={bc.color} bg={bc.bg} border={bc.border}/></div>
                      <div style={{ color:riskColor(a.risk_score), fontWeight:700 }}>{a.risk_score}</div>
                      <div>{a.days_since_last}d</div>
                      <div style={{ color:"#69f0ae" }}>{fmtEur(a.oportunidad)}</div>
                      <div style={{ fontSize:10 }}>{motivoIcon(a.motivo)}</div>
                      <div style={{ fontSize:11, color:a.loyalty==="Loyal"?"#a5d6a7":"#ffcc80" }}>{a.loyalty}</div>
                    </div>
                  );
                })}
              </div>
              <div style={{ marginTop:8, fontSize:11, color:"#374151" }}>
                Note: In production this table shows up to 500 rows of the real database_clean.csv after cleaning.
              </div>
            </div>
          )}

          {/* ── Methodology Expander ── */}
          <MethodologyExpander />

          {/* Footer */}
          <div style={{ marginTop:28, textAlign:"center", fontSize:11, color:"#374151", paddingBottom:20, lineHeight:1.8 }}>
            Smart Demand Signals · Built for Inibsa Hackathon · 100% Pandas · Zero Black-Box<br/>
            <span style={{ color:"#1e3a5f" }}>─────────────────────────────────────────────</span><br/>
            Run the engine: <code style={{ background:"rgba(255,255,255,0.05)", padding:"2px 8px", borderRadius:4, color:"#90caf9" }}>streamlit run app.py</code>
          </div>
        </div>
      </div>
    </div>
  );
}
