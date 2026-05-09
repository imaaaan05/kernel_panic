"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          SMART DEMAND SIGNALS — Inibsa Commercial Intelligence              ║
║          Lead Data Scientist & Senior Python/Streamlit Architect            ║
║                                                                              ║
║  ARCHITECTURE GUARANTEE: 100% Pandas rule-based engine.                     ║
║  Zero ML black boxes. Every alert is a deterministic IF/THEN rule           ║
║  operating on descriptive statistics. Fully auditable & explainable.        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime, date

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Demand Signals | Inibsa",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Commercial dashboard styling
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ──────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}

/* ── App background ───────────────────────────────────────────────────────── */
.stApp {
    background: #f8fafc;
}

/* ── Hide default Streamlit chrome ───────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* ── Sidebar ──────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1e1b4b;
    border-right: 1px solid #312e81;
}
[data-testid="stSidebar"] * { color: #e0e7ff !important; }
[data-testid="stSidebar"] .stSlider > div { color: #c7d2fe !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { color: #a5b4fc !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.08em; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: #3730a3 !important;
    border: 1px solid #4338ca !important;
    color: #e0e7ff !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #4338ca !important;
}

/* ── KPI metric cards ─────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
    transition: box-shadow 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #94a3b8 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    line-height: 1.1 !important;
}

/* ── Data editor / table ──────────────────────────────────────────────────── */
[data-testid="stDataEditor"] {
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    overflow: hidden;
}

/* ── Section headers ──────────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
}
.section-header h2 {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
}
.section-header .badge {
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    background: #eef2ff;
    color: #4f46e5;
}

/* ── Alert reason badges ──────────────────────────────────────────────────── */
.motivo-captura    { background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.motivo-retraso    { background:#fff7ed; color:#c2410c; border:1px solid #fed7aa; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }
.motivo-caida      { background:#fef2f2; color:#b91c1c; border:1px solid #fecaca; padding:2px 8px; border-radius:20px; font-size:11px; font-weight:600; }

/* ── Risk score progress bar ──────────────────────────────────────────────── */
.risk-bar-wrap { display:flex; align-items:center; gap:8px; width:100%; }
.risk-bar-bg   { flex:1; height:6px; background:#f1f5f9; border-radius:9999px; overflow:hidden; }
.risk-bar-fill { height:100%; border-radius:9999px; transition:width 0.5s; }
.risk-val      { font-size:12px; font-weight:700; min-width:24px; text-align:right; }

/* ── Custom expander ──────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e0e7ff !important;
    border-radius: 16px !important;
    background: #fafbff !important;
    box-shadow: none !important;
}
[data-testid="stExpander"] summary {
    font-weight: 700 !important;
    color: #312e81 !important;
    font-size: 0.95rem !important;
}

/* ── Dashboard title ──────────────────────────────────────────────────────── */
.dashboard-title {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 16px;
}
.dashboard-title .icon {
    font-size: 2.5rem;
    background: rgba(255,255,255,0.15);
    border-radius: 14px;
    width: 56px; height: 56px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.dashboard-title h1 { font-size: 1.5rem; font-weight: 800; margin: 0; color: white; }
.dashboard-title p { font-size: 0.8rem; opacity: 0.75; margin: 2px 0 0 0; }
.dashboard-title .badge-engine {
    margin-left:auto; padding:6px 14px; border-radius:20px;
    background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.25);
    font-size:11px; font-weight:700; letter-spacing:0.05em; color:white;
    white-space: nowrap;
}

/* ── Divider ──────────────────────────────────────────────────────────────── */
hr { border:none; border-top:1px solid #e2e8f0; margin:1.5rem 0; }

/* ── Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#cbd5e1; border-radius:3px; }

</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 1 — DATA INGESTION & CLEANING                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def load_and_clean(filepath: str = "database_clean.csv") -> pd.DataFrame:
    """
    Load the European CSV with all critical parameters, rename columns to English,
    repair European decimals, standardize Analytical_Block, parse dates,
    and remove invalid rows.
    """
    # ── 1.1 Load raw file ──────────────────────────────────────────────────────
    df = pd.read_csv(
        filepath,
        dtype=str,
        sep=';',
        encoding='latin1',
    )

    # ── 1.2 Rename columns ────────────────────────────────────────────────────
    rename_map = {
        'Id.Cliente':       'Client_ID',
        'Fecha':            'Date',
        'Familia_H':        'Product_Family',
        'Unidades':         'Quantity',
        'Valores_H':        'Transaction_Value',
        'Potencial_H':      'Client_Potential',
        'Bloque analítico': 'Analytical_Block',
    }
    df.rename(columns=rename_map, inplace=True)

    # ── 1.3 CRITICAL: European decimal parsing ────────────────────────────────
    for col in ['Quantity', 'Transaction_Value', 'Client_Potential']:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # ── 1.4 Standardize Analytical_Block ─────────────────────────────────────
    df['Analytical_Block'] = df['Analytical_Block'].str.strip()
    df['Analytical_Block'] = df['Analytical_Block'].replace('Productos Técnicos', 'Technical')
    # Keep 'Commodities' as is

    # ── 1.5 Parse date ────────────────────────────────────────────────────────
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')

    # ── 1.6 Drop invalid rows ─────────────────────────────────────────────────
    df = df.dropna(subset=['Date', 'Quantity', 'Transaction_Value'])
    df = df[(df['Quantity'] > 0) & (df['Transaction_Value'] > 0)]
    df = df.reset_index(drop=True)

    return df


@st.cache_data(show_spinner=False)
def load_from_upload(file_bytes: bytes) -> pd.DataFrame:
    """Load from uploaded file bytes using the same cleaning pipeline."""
    content = io.StringIO(file_bytes.decode('latin1'))
    df = pd.read_csv(content, dtype=str, sep=';')
    return _apply_cleaning(df)


def _apply_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """Shared cleaning logic for both file load paths."""
    rename_map = {
        'Id.Cliente':       'Client_ID',
        'Fecha':            'Date',
        'Familia_H':        'Product_Family',
        'Unidades':         'Quantity',
        'Valores_H':        'Transaction_Value',
        'Potencial_H':      'Client_Potential',
        'Bloque analítico': 'Analytical_Block',
    }
    df.rename(columns=rename_map, inplace=True)

    for col in ['Quantity', 'Transaction_Value', 'Client_Potential']:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['Analytical_Block'] = df['Analytical_Block'].str.strip()
    df['Analytical_Block'] = df['Analytical_Block'].replace('Productos Técnicos', 'Technical')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date', 'Quantity', 'Transaction_Value'])
    df = df[(df['Quantity'] > 0) & (df['Transaction_Value'] > 0)]
    return df.reset_index(drop=True)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 2 — FEATURE ENGINEERING (Bottom-Up Approach)                          ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Loyalty_Factor and Days_Between per Client/Family pair.
    """
    # ── 2.1 Loyalty Factor ────────────────────────────────────────────────────
    # Monthly spend per client
    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_spend = (
        df.groupby(['Client_ID', 'YearMonth'])['Transaction_Value']
        .sum()
        .reset_index()
        .groupby('Client_ID')['Transaction_Value']
        .mean()
        .rename('Average_Monthly_Spend')
    )
    max_potential = (
        df.groupby('Client_ID')['Client_Potential']
        .max()
        .rename('Max_Client_Potential')
    )
    client_profile = pd.concat([monthly_spend, max_potential], axis=1).reset_index()
    client_profile['Loyalty_Factor'] = np.where(
        client_profile['Average_Monthly_Spend'] >= 0.85 * client_profile['Max_Client_Potential'],
        'Loyal',
        'Promiscuous',
    )

    # ── 2.2 Aggregation ───────────────────────────────────────────────────────
    agg = (
        df.groupby(['Client_ID', 'Date', 'Product_Family'])
        .agg(
            Quantity=('Quantity', 'sum'),
            Transaction_Value=('Transaction_Value', 'sum'),
            Analytical_Block=('Analytical_Block', 'first'),
        )
        .reset_index()
    )

    # Merge loyalty data
    agg = agg.merge(
        client_profile[['Client_ID', 'Loyalty_Factor', 'Average_Monthly_Spend', 'Max_Client_Potential']],
        on='Client_ID',
        how='left',
    )

    # ── 2.3 Days_Between per Client/Family pair ───────────────────────────────
    agg = agg.sort_values(['Client_ID', 'Product_Family', 'Date']).reset_index(drop=True)
    agg['Days_Between'] = (
        agg.groupby(['Client_ID', 'Product_Family'])['Date']
        .diff()
        .dt.days
    )

    return agg


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 3 — STATISTICAL ENGINE & COLD START                                   ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def compute_statistics(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate per-pair Mean/Std statistics.
    Cold start: if < 3 purchases, use global family statistics.
    """
    # ── 3.1 Per-pair statistics ───────────────────────────────────────────────
    pair_stats = (
        agg.groupby(['Client_ID', 'Product_Family'])
        .agg(
            Mean_Qty=('Quantity', 'mean'),
            Std_Qty=('Quantity', 'std'),
            Mean_Days=('Days_Between', 'mean'),
            Std_Days=('Days_Between', 'std'),
            Purchase_Count=('Quantity', 'count'),
            Average_Transaction_Value=('Transaction_Value', 'mean'),
        )
        .reset_index()
    )

    # ── 3.2 Global family statistics (cold-start fallback) ───────────────────
    family_stats = (
        agg.groupby('Product_Family')
        .agg(
            Global_Mean_Qty=('Quantity', 'mean'),
            Global_Std_Qty=('Quantity', 'std'),
            Global_Mean_Days=('Days_Between', 'mean'),
            Global_Std_Days=('Days_Between', 'std'),
        )
        .reset_index()
    )

    pair_stats = pair_stats.merge(family_stats, on='Product_Family', how='left')

    # ── 3.3 Apply cold-start fallback ────────────────────────────────────────
    cold = pair_stats['Purchase_Count'] < 3

    pair_stats.loc[cold, 'Mean_Qty']  = pair_stats.loc[cold, 'Global_Mean_Qty']
    pair_stats.loc[cold, 'Std_Qty']   = pair_stats.loc[cold, 'Global_Std_Qty']
    pair_stats.loc[cold, 'Mean_Days'] = pair_stats.loc[cold, 'Global_Mean_Days']
    pair_stats.loc[cold, 'Std_Days']  = pair_stats.loc[cold, 'Global_Std_Days']

    # ── 3.4 Fill remaining NaNs with 0 ───────────────────────────────────────
    stat_cols = ['Mean_Qty', 'Std_Qty', 'Mean_Days', 'Std_Days']
    pair_stats[stat_cols] = pair_stats[stat_cols].fillna(0)

    # Drop global fallback columns (only used internally)
    pair_stats.drop(
        columns=['Global_Mean_Qty', 'Global_Std_Qty', 'Global_Mean_Days', 'Global_Std_Days'],
        inplace=True,
        errors='ignore',
    )

    return pair_stats


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 4 — ALERT ENGINE                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def generate_alerts(agg: pd.DataFrame, stats: pd.DataFrame) -> pd.DataFrame:
    """
    Rule-based alert generation.
    'Today' = maximum date in the dataset.
    Rule A: Commodities capture window
    Rule B: Technical churn risk (time drop + volume drop)
    """
    # ── Today = max date in dataset ───────────────────────────────────────────
    today = agg['Date'].max()

    # ── Most recent purchase per Client/Family ────────────────────────────────
    latest = (
        agg.sort_values('Date')
        .groupby(['Client_ID', 'Product_Family'])
        .last()
        .reset_index()
        .rename(columns={'Quantity': 'Last_Qty', 'Transaction_Value': 'Last_Transaction_Value'})
    )

    # Merge statistics
    latest = latest.merge(stats, on=['Client_ID', 'Product_Family'], how='left')

    # ── Days since last purchase ──────────────────────────────────────────────
    latest['Days_Since_Last'] = (today - latest['Date']).dt.days

    alerts_list = []

    # ─────────────────────────────────────────────────────────────────────────
    # RULE A — Commodities: Capture Window
    # Condition: block=='Commodities' AND loyalty=='Promiscuous' AND days_since >= mean_days
    # ─────────────────────────────────────────────────────────────────────────
    mask_a = (
        (latest['Analytical_Block'] == 'Commodities') &
        (latest['Loyalty_Factor'] == 'Promiscuous') &
        (latest['Days_Since_Last'] >= latest['Mean_Days'])
    )
    df_a = latest[mask_a].copy()
    df_a['Motivo'] = 'Ventana de Captura'
    # Opportunity = potential gap (bounded to 0)
    df_a['Valor_Oportunidad'] = (
        df_a['Max_Client_Potential'] - df_a['Average_Monthly_Spend']
    ).clip(lower=0)
    df_a['Days_Delayed'] = (df_a['Days_Since_Last'] - df_a['Mean_Days']).clip(lower=0)
    alerts_list.append(df_a)

    # ─────────────────────────────────────────────────────────────────────────
    # RULE B1 — Technical: Anomalous Time Delay
    # Adjusted for bulk purchases: Expected_Days = Mean_Days * (Last_Qty / Mean_Qty)
    # Fire if: Days_Since_Last > Expected_Days + 1.5 * Std_Days
    # ─────────────────────────────────────────────────────────────────────────
    tech = latest[latest['Analytical_Block'] == 'Technical'].copy()
    tech['Expected_Days'] = tech['Mean_Days'] * (
        tech['Last_Qty'] / tech['Mean_Qty'].replace(0, np.nan)
    ).fillna(1)
    tech['Time_Threshold'] = tech['Expected_Days'] + 1.5 * tech['Std_Days']

    mask_b1 = tech['Days_Since_Last'] > tech['Time_Threshold']
    df_b1 = tech[mask_b1].copy()
    df_b1['Motivo'] = 'Retraso anómalo en tiempo'
    df_b1['Valor_Oportunidad'] = df_b1['Average_Monthly_Spend']
    df_b1['Days_Delayed'] = (df_b1['Days_Since_Last'] - df_b1['Expected_Days']).clip(lower=0)
    alerts_list.append(df_b1)

    # ─────────────────────────────────────────────────────────────────────────
    # RULE B2 — Technical: Drastic Volume Drop
    # Fire if: Last_Qty < Mean_Qty - 1.0 * Std_Qty
    # ─────────────────────────────────────────────────────────────────────────
    mask_b2 = tech['Last_Qty'] < (tech['Mean_Qty'] - 1.0 * tech['Std_Qty'])
    df_b2 = tech[mask_b2].copy()
    df_b2['Motivo'] = 'Caída drástica de volumen'
    df_b2['Valor_Oportunidad'] = df_b2['Average_Monthly_Spend']
    df_b2['Days_Delayed'] = (df_b2['Days_Since_Last'] - df_b2['Mean_Days']).clip(lower=0)
    alerts_list.append(df_b2)

    # ── Combine all alerts ────────────────────────────────────────────────────
    if not any(len(d) > 0 for d in alerts_list):
        return pd.DataFrame()

    alerts = pd.concat([d for d in alerts_list if len(d) > 0], ignore_index=True)

    # ── Select & order output columns ─────────────────────────────────────────
    keep_cols = [
        'Client_ID', 'Product_Family', 'Analytical_Block',
        'Loyalty_Factor', 'Motivo',
        'Days_Since_Last', 'Valor_Oportunidad',
        'Average_Monthly_Spend', 'Max_Client_Potential',
        'Mean_Days', 'Std_Days', 'Mean_Qty', 'Std_Qty',
        'Last_Qty', 'Average_Transaction_Value', 'Days_Delayed',
        'Purchase_Count',
    ]
    existing_cols = [c for c in keep_cols if c in alerts.columns]
    alerts = alerts[existing_cols].copy()

    return alerts


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  STEP 5 — PRIORITIZATION SCORE                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def score_alerts(alerts: pd.DataFrame) -> pd.DataFrame:
    """
    Raw_Score = Avg_Transaction_Value * (1 + Days_Delayed / Mean_Days)
    Min-Max normalize to [1, 100], round to integer → Nivel de Riesgo
    """
    if len(alerts) == 0:
        return alerts

    # Avoid division by zero
    mean_days_safe = alerts['Mean_Days'].replace(0, 1)
    alerts = alerts.copy()

    # Raw score
    alerts['Raw_Score'] = (
        alerts['Average_Transaction_Value'] *
        (1 + alerts['Days_Delayed'] / mean_days_safe)
    )

    # Min-Max normalization → [1, 100]
    min_s = alerts['Raw_Score'].min()
    max_s = alerts['Raw_Score'].max()
    rng = max_s - min_s if max_s != min_s else 1.0

    alerts['Nivel de Riesgo'] = (
        ((alerts['Raw_Score'] - min_s) / rng) * 99 + 1
    ).round().astype(int)

    # Add feedback column
    alerts['Register_Action'] = ''

    # Sort descending
    alerts = alerts.sort_values('Nivel de Riesgo', ascending=False).reset_index(drop=True)

    return alerts


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  RISK BAR RENDERER                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def risk_color(score: int) -> tuple:
    """Returns (bar_color_hex, text_color_hex) based on score."""
    if score >= 80:   return '#ef4444', '#dc2626'
    if score >= 60:   return '#f97316', '#ea580c'
    if score >= 40:   return '#fbbf24', '#d97706'
    return '#10b981', '#059669'


def render_risk_html(score: int) -> str:
    bar_c, txt_c = risk_color(score)
    return (
        f'<div class="risk-bar-wrap">'
        f'<div class="risk-bar-bg">'
        f'<div class="risk-bar-fill" style="width:{score}%;background:{bar_c}"></div>'
        f'</div>'
        f'<span class="risk-val" style="color:{txt_c}">{score}</span>'
        f'</div>'
    )


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DEMO DATA GENERATOR                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@st.cache_data(show_spinner=False)
def generate_demo_data() -> pd.DataFrame:
    """Generate realistic synthetic data for demonstration purposes."""
    np.random.seed(42)

    families = [
        ('Gloves Nitrile',      'Commodities'),
        ('Surgical Masks',       'Commodities'),
        ('IV Catheters',         'Technical'),
        ('Suture Kit Pro',       'Technical'),
        ('Syringes 5ml',         'Commodities'),
        ('Compression Bandages', 'Technical'),
        ('Disinfectant Gel',     'Commodities'),
        ('Surgical Drapes',      'Technical'),
    ]
    clients = [
        ('CLI-0001', 18000), ('CLI-0002', 25000), ('CLI-0003', 12000),
        ('CLI-0004', 32000), ('CLI-0005',  9500), ('CLI-0006', 41000),
        ('CLI-0007', 15500), ('CLI-0008', 28000), ('CLI-0009',  7800),
        ('CLI-0010', 55000), ('CLI-0011', 22000), ('CLI-0012', 18500),
    ]

    rows = []
    today = pd.Timestamp('2024-10-15')

    for client_id, potential in clients:
        n_families = np.random.randint(3, 7)
        assigned = np.random.choice(len(families), n_families, replace=False)

        for fi in assigned:
            fname, fblock = families[fi]
            n_purchases = np.random.randint(4, 12)
            base_qty   = np.random.uniform(50, 250)
            base_val   = np.random.uniform(500, 4000)
            interval   = np.random.randint(18, 45)

            start = today - pd.Timedelta(days=n_purchases * interval + np.random.randint(30, 90))

            for p in range(n_purchases):
                is_last = (p == n_purchases - 1)
                anomalous = is_last and np.random.random() < 0.40

                qty = (
                    base_qty * np.random.uniform(0.15, 0.40)
                    if anomalous
                    else base_qty * np.random.uniform(0.70, 1.30)
                )
                val = qty * (base_val / base_qty) * np.random.uniform(0.92, 1.08)

                stale_gap = (
                    interval + np.random.randint(25, 55)
                    if (is_last and np.random.random() < 0.45)
                    else max(5, interval + np.random.randint(-8, 12))
                )

                rows.append({
                    'Client_ID':          client_id,
                    'Date':               start,
                    'Product_Family':     fname,
                    'Quantity':           max(1.0, round(qty, 2)),
                    'Transaction_Value':  max(10.0, round(val, 2)),
                    'Client_Potential':   float(potential),
                    'Analytical_Block':   fblock,
                })
                start += pd.Timedelta(days=stale_gap)

    df = pd.DataFrame(rows)
    df['Date'] = pd.to_datetime(df['Date'])
    return df


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  FULL PIPELINE                                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def run_full_pipeline(df: pd.DataFrame):
    """Execute Steps 2–5 on a cleaned DataFrame."""
    with st.spinner("🔬 Running feature engineering…"):
        agg = engineer_features(df)
    with st.spinner("📐 Computing statistical profiles…"):
        stats = compute_statistics(agg)
    with st.spinner("⚡ Generating alerts…"):
        alerts_raw = generate_alerts(agg, stats)
    with st.spinner("🏆 Scoring & prioritizing…"):
        alerts = score_alerts(alerts_raw)
    return alerts


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN STREAMLIT APPLICATION                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def main():
    # ── Dashboard Title Banner ────────────────────────────────────────────────
    st.markdown("""
    <div class="dashboard-title">
        <div class="icon">📡</div>
        <div>
            <h1>Smart Demand Signals</h1>
            <p>Inibsa Commercial Intelligence · 100% Explainable Rule-Based Engine</p>
        </div>
        <div class="badge-engine">⚡ ZERO BLACK BOX</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Initialize session state ──────────────────────────────────────────────
    if 'alerts' not in st.session_state:
        st.session_state.alerts = None
    if 'today_date' not in st.session_state:
        st.session_state.today_date = None

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  SIDEBAR — Filters & Data Source                                       ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    with st.sidebar:
        st.markdown("## 📡 Smart Demand Signals")
        st.markdown("---")

        # ── Data Source ───────────────────────────────────────────────────────
        st.markdown("### 📂 Data Source")
        data_source = st.radio(
            "Select data source:",
            ["📁 Upload CSV", "🚀 Demo Data", "💾 Load database_clean.csv"],
            label_visibility="collapsed",
        )

        if data_source == "📁 Upload CSV":
            uploaded = st.file_uploader(
                "Upload database_clean.csv",
                type=['csv'],
                help="European CSV: sep=';', encoding=latin1, comma decimals",
            )
            if uploaded and st.button("▶ Run Engine", use_container_width=True):
                try:
                    df = load_from_upload(uploaded.read())
                    st.session_state.today_date = df['Date'].max().date()
                    st.session_state.alerts = run_full_pipeline(df)
                    st.success(f"✅ Loaded {len(df):,} rows")
                except Exception as e:
                    st.error(f"Error: {e}")

        elif data_source == "🚀 Demo Data":
            st.info("12 clients · 8 product families · synthetic anomalies injected")
            if st.button("🚀 Launch Demo", use_container_width=True):
                df = generate_demo_data()
                st.session_state.today_date = df['Date'].max().date()
                st.session_state.alerts = run_full_pipeline(df)

        else:  # Load database_clean.csv
            if st.button("💾 Load File", use_container_width=True):
                try:
                    df = load_and_clean("database_clean.csv")
                    st.session_state.today_date = df['Date'].max().date()
                    st.session_state.alerts = run_full_pipeline(df)
                    st.success(f"✅ Loaded {len(df):,} rows")
                except FileNotFoundError:
                    st.error("database_clean.csv not found. Place it in the same directory as app.py.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # ── Filters (only if data loaded) ─────────────────────────────────────
        if st.session_state.alerts is not None and len(st.session_state.alerts) > 0:
            alerts_df: pd.DataFrame = st.session_state.alerts

            st.markdown("---")
            st.markdown("### 🎯 Filters")

            # Analytical Block
            blocks = ['All'] + sorted(alerts_df['Analytical_Block'].unique().tolist())
            selected_block = st.selectbox("Analytical Block", blocks)

            # Alert Reason
            motivos = ['All'] + sorted(alerts_df['Motivo'].unique().tolist())
            selected_motivo = st.selectbox("Alert Reason / Motivo", motivos)

            # Loyalty Factor
            loyalty_opts = ['All', 'Loyal', 'Promiscuous']
            selected_loyalty = st.selectbox("Loyalty Factor", loyalty_opts)

            # Minimum Risk Score
            min_risk = st.slider(
                "Minimum Nivel de Riesgo",
                min_value=1, max_value=100, value=1, step=1,
            )

            st.markdown("---")
            if st.button("🔄 Reset Filters", use_container_width=True):
                st.rerun()

    # ── Guard: no data loaded yet ─────────────────────────────────────────────
    if st.session_state.alerts is None:
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; color:#94a3b8;">
            <div style="font-size:4rem; margin-bottom:1rem;">📡</div>
            <h2 style="color:#475569; font-weight:700;">Awaiting Data</h2>
            <p style="font-size:1rem; max-width:420px; margin:0 auto;">
                Use the sidebar to upload <code>database_clean.csv</code> or launch with demo data.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    alerts_df: pd.DataFrame = st.session_state.alerts

    if len(alerts_df) == 0:
        st.warning("⚠️ No alerts generated. Check that data contains valid Commodities or Technical rows.")
        return

    # ── Apply filters ─────────────────────────────────────────────────────────
    filtered = alerts_df.copy()
    try:
        if selected_block != 'All':
            filtered = filtered[filtered['Analytical_Block'] == selected_block]
        if selected_motivo != 'All':
            filtered = filtered[filtered['Motivo'] == selected_motivo]
        if selected_loyalty != 'All':
            filtered = filtered[filtered['Loyalty_Factor'] == selected_loyalty]
        filtered = filtered[filtered['Nivel de Riesgo'] >= min_risk]
    except NameError:
        pass  # Filters not yet initialized (first load)

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  KPI CARDS                                                             ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    today_str = str(st.session_state.today_date) if st.session_state.today_date else "N/A"
    unique_clients = filtered['Client_ID'].nunique()
    high_risk_count = (filtered['Nivel de Riesgo'] >= 70).sum()
    total_opportunity = filtered['Valor_Oportunidad'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="🔔 Total Alerts",
            value=f"{len(filtered):,}",
            delta=f"of {len(alerts_df)} generated",
        )
    with col2:
        st.metric(
            label="👥 Clients at Risk",
            value=f"{unique_clients}",
            delta="unique clients flagged",
        )
    with col3:
        st.metric(
            label="🔴 High Risk (≥70)",
            value=f"{high_risk_count}",
            delta="critical priority",
        )
    with col4:
        st.metric(
            label="💶 Total Opportunity",
            value=f"€{total_opportunity:,.0f}",
            delta="recoverable revenue",
        )

    st.markdown(
        f"<p style='text-align:right;font-size:11px;color:#94a3b8;margin-top:-8px;'>"
        f"Reference date (max in dataset): <strong>{today_str}</strong></p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  ALERT TABLE — st.data_editor with interactive feedback               ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    st.markdown("""
    <div class="section-header">
        <h2>📋 Commercial Alert Registry</h2>
        <span class="badge">Sorted by Nivel de Riesgo ↓</span>
    </div>
    """, unsafe_allow_html=True)

    # Prepare display dataframe
    display_cols = [
        'Client_ID', 'Product_Family', 'Analytical_Block', 'Motivo',
        'Nivel de Riesgo', 'Days_Since_Last', 'Valor_Oportunidad',
        'Register_Action',
    ]
    existing_display = [c for c in display_cols if c in filtered.columns]
    display_df = filtered[existing_display].copy()

    if 'Valor_Oportunidad' in display_df.columns:
        display_df['Valor_Oportunidad'] = display_df['Valor_Oportunidad'].round(2)

    # Column config for data_editor
    column_config = {
        'Client_ID': st.column_config.TextColumn(
            "Client ID",
            width="small",
        ),
        'Product_Family': st.column_config.TextColumn(
            "Product Family",
            width="medium",
        ),
        'Analytical_Block': st.column_config.TextColumn(
            "Block",
            width="small",
        ),
        'Motivo': st.column_config.TextColumn(
            "Alert Reason (Motivo)",
            width="large",
        ),
        'Nivel de Riesgo': st.column_config.ProgressColumn(
            "Nivel de Riesgo",
            help="Risk score 1–100 (higher = more urgent). Formula: AvgTxValue × (1 + DaysDelayed/MeanDays), min-max normalized.",
            min_value=1,
            max_value=100,
            format="%d",
            width="medium",
        ),
        'Days_Since_Last': st.column_config.NumberColumn(
            "Days Since Last",
            help="Days elapsed since the last recorded purchase for this Client/Family pair.",
            format="%d days",
            width="small",
        ),
        'Valor_Oportunidad': st.column_config.NumberColumn(
            "Valor Oportunidad (€)",
            help="Estimated recoverable revenue opportunity for this alert.",
            format="€%.2f",
            width="medium",
        ),
        'Register_Action': st.column_config.SelectboxColumn(
            "Register Action",
            help="Mock ML feedback loop — actions are logged for future model training.",
            options=["", "✅ Success", "❌ False Positive"],
            required=False,
            width="medium",
        ),
    }

    edited = st.data_editor(
        display_df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="alert_editor",
    )

    # Feedback summary
    if 'Register_Action' in edited.columns:
        n_success = (edited['Register_Action'] == '✅ Success').sum()
        n_fp = (edited['Register_Action'] == '❌ False Positive').sum()
        if n_success > 0 or n_fp > 0:
            fc1, fc2, fc3 = st.columns([1, 1, 3])
            with fc1:
                st.success(f"✅ {n_success} marked as Success")
            with fc2:
                st.error(f"❌ {n_fp} marked as False Positive")
            with fc3:
                precision = n_success / (n_success + n_fp) if (n_success + n_fp) > 0 else 0
                st.info(f"📐 Estimated Precision: {precision:.0%}  ·  This feedback trains future supervised models.")

    # Export button
    csv_export = filtered.to_csv(index=False, sep=';', decimal=',').encode('latin1')
    st.download_button(
        label="⬇️ Export Alerts as CSV",
        data=csv_export,
        file_name=f"smart_demand_signals_{date.today().isoformat()}.csv",
        mime="text/csv",
    )

    # ╔════════════════════════════════════════════════════════════════════════╗
    # ║  METHODOLOGY EXPANDER                                                  ║
    # ╚════════════════════════════════════════════════════════════════════════╝
    st.markdown("---")

    with st.expander("🔬 Methodology: 100% Pandas Rule-Based Engine — Full Transparency (No Black Box)", expanded=False):
        st.markdown("""
        ### Why Rule-Based? The Explainability Guarantee

        This system deliberately uses **zero machine learning models**. Every alert is generated by
        explicit, auditable IF/THEN rules operating on standard descriptive statistics.
        A domain expert can read every line of code and understand exactly why any alert fired.

        ---

        #### ⚡ Step 1 — Data Ingestion & Cleaning (Pandas)
        ```python
        df = pd.read_csv(filepath, dtype=str, sep=';', encoding='latin1')
        # European decimal repair — CRITICAL
        for col in ['Quantity', 'Transaction_Value', 'Client_Potential']:
            df[col] = df[col].str.replace(',', '.').pipe(pd.to_numeric, errors='coerce')
        # Standardize block names
        df['Analytical_Block'] = df['Analytical_Block'].replace('Productos Técnicos', 'Technical')
        # Remove invalid rows
        df = df[(df['Quantity'] > 0) & (df['Transaction_Value'] > 0)]
        ```

        ---

        #### 🧮 Step 2 — Loyalty Factor (Bottom-Up)
        ```python
        monthly_spend = df.groupby(['Client_ID', 'YearMonth'])['Transaction_Value'].sum()
        avg_monthly   = monthly_spend.groupby('Client_ID').mean()
        max_potential = df.groupby('Client_ID')['Client_Potential'].max()

        # Loyalty Rule:
        loyalty = np.where(avg_monthly >= 0.85 * max_potential, 'Loyal', 'Promiscuous')
        ```

        ---

        #### 📐 Step 3 — Statistical Profiles (Per Client/Family Pair)
        ```python
        pair_stats = df.groupby(['Client_ID', 'Product_Family']).agg(
            Mean_Qty  = ('Quantity',      'mean'),
            Std_Qty   = ('Quantity',      'std'),   # Sample std, ddof=1
            Mean_Days = ('Days_Between',  'mean'),
            Std_Days  = ('Days_Between',  'std'),
        )

        # Cold Start: if < 3 purchases, fall back to global family statistics
        cold_mask = pair_stats['Purchase_Count'] < 3
        pair_stats.loc[cold_mask, 'Mean_Qty'] = global_family_mean_qty
        # ... (same for Std, Mean_Days, Std_Days)
        ```

        ---

        #### 🎯 Step 4 — Alert Rules (Deterministic IF/THEN)

        | Rule | Block | Condition | Alert |
        |------|-------|-----------|-------|
        | **A** | Commodities | `Loyalty=='Promiscuous' AND Days_Since_Last >= Mean_Days` | Ventana de Captura |
        | **B1** | Technical | `Days_Since_Last > (Mean_Days × Last_Qty/Mean_Qty) + 1.5σ_Days` | Retraso anómalo en tiempo |
        | **B2** | Technical | `Last_Qty < Mean_Qty − 1.0 × Std_Qty` | Caída drástica de volumen |

        ```python
        # Rule A — Commodities Capture Window
        mask_a = (
            (df['Analytical_Block'] == 'Commodities') &
            (df['Loyalty_Factor']   == 'Promiscuous') &
            (df['Days_Since_Last']  >= df['Mean_Days'])
        )
        # Opportunity = unrealized potential
        df.loc[mask_a, 'Valor_Oportunidad'] = (df['Max_Client_Potential'] - df['Avg_Monthly_Spend']).clip(0)

        # Rule B1 — Technical Time Delay (bulk-purchase adjusted)
        expected_days = Mean_Days * (Last_Qty / Mean_Qty)   # accounts for bulk orders
        mask_b1 = Days_Since_Last > expected_days + 1.5 * Std_Days

        # Rule B2 — Technical Volume Drop
        mask_b2 = Last_Qty < Mean_Qty - 1.0 * Std_Qty
        ```

        ---

        #### 🏆 Step 5 — Prioritization Score (Min-Max Normalized)
        ```python
        Raw_Score = Average_Transaction_Value * (1 + Days_Delayed / Mean_Days)
        #           ↑ rewards high-value clients  ↑ rewards most-overdue accounts

        # Min-Max normalization to [1, 100]
        Nivel_de_Riesgo = round(1 + ((Raw_Score - min) / (max - min)) * 99)
        ```

        ---

        #### 🔄 ML Feedback Loop Architecture
        The **Register_Action** column (✅ Success / ❌ False Positive) captures commercial agent
        feedback per alert. This structured labeled data is the foundation for a future supervised
        classification model. Current precision can be estimated in real-time from agent feedback.
        All decisions remain fully human-overridable.

        ---

        > **Zero Black-Box Guarantee**: No neural networks. No gradient boosting. No hidden embeddings.
        > Every number in this dashboard traces directly to a pandas `.mean()`, `.std()`, or a comparison
        > operator. The full source code is ~300 lines of pure Python.
        """)


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
