"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║         SMART DEMAND SIGNALS — Inibsa Hackathon Solution                       ║
║         100% Pandas Rule-Based Engine | Zero Black-Box ML                      ║
║         Lead Data Scientist Architecture — Production Ready                    ║
╚══════════════════════════════════════════════════════════════════════════════════╝

Run:  streamlit run app.py
Deps: pip install streamlit pandas numpy
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Demand Signals · Inibsa",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Commercial-grade design system
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & Typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0f1117 0%, #1a1d2e 50%, #0f1117 100%);
    color: #e2e8f0;
}

/* ── Hide default Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Custom header banner ── */
.header-banner {
    background: linear-gradient(90deg, #1e3a5f 0%, #0d47a1 40%, #1565c0 70%, #1e3a5f 100%);
    border: 1px solid rgba(66,165,245,0.3);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(13,71,161,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}
.header-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    margin: 0;
}
.header-subtitle {
    font-size: 13px;
    color: #90caf9;
    margin: 4px 0 0 0;
    letter-spacing: 0.3px;
}
.header-badge {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    color: #bbdefb;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: linear-gradient(145deg, #1e2538, #252d40);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(0,0,0,0.4);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue::before  { background: linear-gradient(90deg, #2196f3, #42a5f5); }
.kpi-card.amber::before { background: linear-gradient(90deg, #ff9800, #ffb74d); }
.kpi-card.red::before   { background: linear-gradient(90deg, #f44336, #ef5350); }
.kpi-card.green::before { background: linear-gradient(90deg, #4caf50, #66bb6a); }
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #8892a4;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 36px;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 6px;
}
.kpi-delta {
    font-size: 12px;
    color: #64748b;
}
.kpi-icon {
    position: absolute;
    top: 18px; right: 20px;
    font-size: 28px;
    opacity: 0.15;
}

/* ── Section headers ── */
.section-header {
    font-size: 16px;
    font-weight: 700;
    color: #e2e8f0;
    letter-spacing: -0.2px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(255,255,255,0.1), transparent);
    margin-left: 8px;
}

/* ── Risk badge colours ── */
.risk-high   { color: #ff5252; font-weight: 700; }
.risk-medium { color: #ffab40; font-weight: 700; }
.risk-low    { color: #69f0ae; font-weight: 700; }

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141824 0%, #1a1f30 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] .block-container { padding-top: 20px; }

/* ── Sidebar brand mark ── */
.sidebar-brand {
    background: linear-gradient(135deg, #0d47a1, #1565c0);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    margin-bottom: 24px;
    border: 1px solid rgba(66,165,245,0.2);
}
.sidebar-brand-title {
    font-size: 16px;
    font-weight: 800;
    color: #fff;
    margin: 0;
}
.sidebar-brand-sub {
    font-size: 11px;
    color: #90caf9;
    margin: 2px 0 0 0;
}

/* ── Alert rule cards ── */
.rule-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid;
    border-radius: 8px;
    padding: 14px 16px;
    margin-bottom: 10px;
    font-size: 13px;
    line-height: 1.6;
    color: #94a3b8;
}
.rule-card.commodities { border-left-color: #ff9800; }
.rule-card.technical   { border-left-color: #2196f3; }
.rule-card strong { color: #e2e8f0; }

/* ── Metric pills ── */
.pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.pill-commodities { background: rgba(255,152,0,0.15);  color: #ffb74d; border: 1px solid rgba(255,152,0,0.3);  }
.pill-technical   { background: rgba(33,150,243,0.15); color: #64b5f6; border: 1px solid rgba(33,150,243,0.3); }

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #4a5568;
}
.empty-state-icon { font-size: 48px; margin-bottom: 16px; }
.empty-state-text { font-size: 16px; font-weight: 600; }

/* ── Data editor overrides ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Progress bar custom ── */
.risk-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    height: 8px;
    width: 100%;
    overflow: hidden;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 99px;
}

/* ── Expander styling ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: linear-gradient(90deg, #0d47a1, #1565c0) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(13,71,161,0.5) !important;
}

/* ── Toast / info boxes ── */
.stAlert { border-radius: 10px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 500;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #0d47a1, #1565c0) !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 · DATA INGESTION & CLEANING
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Load database_clean.csv with full comma-decimal handling.
    All numeric coercion is explicit — zero black-box transformations.
    """
    # ── Read everything as strings to avoid locale-dependent float parsing ──
    df = pd.read_csv(filepath, dtype=str, sep=None, engine="python", encoding="latin1")
    
    # ── Rename to English canonical column names ──
    rename_map = {
        "Id.Cliente":  "Client_ID",
        "Fecha":       "Date",
        "Familia_H":   "Product_Family",
        "Unidades":    "Quantity",
        "Valores_H":   "Transaction_Value",
        "Potencial_H": "Client_Potential",
    }
    df.rename(columns=rename_map, inplace=True)

    # ── CRITICAL: replace European comma-decimals → dot-decimals ──
    for col in ["Quantity", "Transaction_Value", "Client_Potential"]:
        if col in df.columns:
            df[col] = df[col].str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Parse dates ──
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    # ── Drop rows with unparseable dates or non-positive transactions ──
    df.dropna(subset=["Date", "Quantity", "Transaction_Value"], inplace=True)
    df = df[(df["Quantity"] > 0) & (df["Transaction_Value"] > 0)].copy()

    # ── Fill potential NaNs with 0 (handled later) ──
    df["Client_Potential"].fillna(0, inplace=True)

    # ── Ensure Client_ID is string ──
    df["Client_ID"] = df["Client_ID"].astype(str).str.strip()
    df["Product_Family"] = df["Product_Family"].astype(str).str.strip()

    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 · FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
def add_analytical_block(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clasificación a prueba de balas: limpia espacios, quita nulos y busca fragmentos.
    """
    # 1. Asegurar que es texto y limpiar espacios invisibles al principio y final
    df["Product_Family"] = df["Product_Family"].astype(str).str.strip().str.upper()
    
    # 2. Las palabras clave
    keywords = ["ANESTE", "AGUJA", "DESINFEC"]
    
    # 3. Función manual (más robusta que regex para depurar)
    def classify(family):
        for kw in keywords:
            if kw in family:
                return "Commodities"
        return "Technical"
        
    df["Analytical_Block"] = df["Product_Family"].apply(classify)
    
    return df

def add_loyalty_factor(df: pd.DataFrame) -> pd.DataFrame:
    """
    Loyalty classification: deterministic threshold vs. client potential.
    Rule: Loyal if Average_Monthly_Spend >= 85 % of Max_Client_Potential.
    """
    # Monthly spend: sum Transaction_Value per client per month
    df["YearMonth"] = df["Date"].dt.to_period("M")
    monthly = (
        df.groupby(["Client_ID", "YearMonth"])["Transaction_Value"]
        .sum()
        .reset_index()
    )
    avg_monthly = (
        monthly.groupby("Client_ID")["Transaction_Value"]
        .mean()
        .reset_index()
        .rename(columns={"Transaction_Value": "Average_Monthly_Spend"})
    )

    # Max potential per client (take the maximum value recorded)
    max_potential = (
        df.groupby("Client_ID")["Client_Potential"]
        .max()
        .reset_index()
        .rename(columns={"Client_Potential": "Max_Client_Potential"})
    )

    loyalty_df = avg_monthly.merge(max_potential, on="Client_ID", how="left")
    loyalty_df["Loyalty_Factor"] = np.where(
        loyalty_df["Average_Monthly_Spend"] >= 0.85 * loyalty_df["Max_Client_Potential"],
        "Loyal",
        "Promiscuous",
    )

    df = df.merge(
        loyalty_df[["Client_ID", "Average_Monthly_Spend", "Max_Client_Potential", "Loyalty_Factor"]],
        on="Client_ID",
        how="left",
    )
    return df


def aggregate_and_days_between(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate to [Client_ID, Date, Product_Family] granularity,
    then compute Days_Between purchases per client-family pair.
    """
    agg = (
        df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False)
        .agg(
            Quantity=("Quantity", "sum"),
            Transaction_Value=("Transaction_Value", "sum"),
            Analytical_Block=("Analytical_Block", "first"),
            Loyalty_Factor=("Loyalty_Factor", "first"),
            Average_Monthly_Spend=("Average_Monthly_Spend", "first"),
            Max_Client_Potential=("Max_Client_Potential", "first"),
            Client_Potential=("Client_Potential", "max"),
        )
        .sort_values(["Client_ID", "Product_Family", "Date"])
        .reset_index(drop=True)
    )

    # Days between consecutive purchases within each client-family pair
    agg["Days_Between"] = (
        agg.groupby(["Client_ID", "Product_Family"])["Date"]
        .diff()
        .dt.days
    )
    return agg


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 · STATISTICAL ENGINE & COLD-START FALLBACK
# ══════════════════════════════════════════════════════════════════════════════
def compute_statistics(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Per client-family pair: Mean & Std of Quantity and Days_Between.
    Cold-start (<3 purchases): fall back to global family statistics.
    All arithmetic is explicit Pandas — no sklearn, no ML.
    """
    # ── Per client-family stats ──
    pair_stats = (
        agg.groupby(["Client_ID", "Product_Family"])
        .agg(
            Purchase_Count=("Quantity", "count"),
            Mean_Qty=("Quantity", "mean"),
            Std_Qty=("Quantity", "std"),
            Mean_Days=("Days_Between", "mean"),
            Std_Days=("Days_Between", "std"),
        )
        .reset_index()
    )

    # ── Global family fallback stats ──
    global_stats = (
        agg.groupby("Product_Family")
        .agg(
            Global_Mean_Qty=("Quantity", "mean"),
            Global_Std_Qty=("Quantity", "std"),
            Global_Mean_Days=("Days_Between", "mean"),
            Global_Std_Days=("Days_Between", "std"),
        )
        .reset_index()
    )

    pair_stats = pair_stats.merge(global_stats, on="Product_Family", how="left")

    # ── Cold-start: apply fallback where Purchase_Count < 3 ──
    cold = pair_stats["Purchase_Count"] < 3
    pair_stats.loc[cold, "Mean_Qty"]  = pair_stats.loc[cold, "Global_Mean_Qty"]
    pair_stats.loc[cold, "Std_Qty"]   = pair_stats.loc[cold, "Global_Std_Qty"]
    pair_stats.loc[cold, "Mean_Days"] = pair_stats.loc[cold, "Global_Mean_Days"]
    pair_stats.loc[cold, "Std_Days"]  = pair_stats.loc[cold, "Global_Std_Days"]

    # ── Fill remaining NaNs with 0 ──
    for col in ["Mean_Qty", "Std_Qty", "Mean_Days", "Std_Days"]:
        pair_stats[col].fillna(0, inplace=True)

    # ── Drop helper columns ──
    pair_stats.drop(
        columns=["Global_Mean_Qty", "Global_Std_Qty", "Global_Mean_Days", "Global_Std_Days"],
        inplace=True,
    )

    agg = agg.merge(pair_stats, on=["Client_ID", "Product_Family"], how="left")
    return agg


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 · ALERT LOGIC
# ══════════════════════════════════════════════════════════════════════════════
def generate_alerts(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Deterministic rule engine. Each alert is a named, auditable condition.
    No model weights, no probabilities — pure business-rule translation.
    """
    TODAY = agg["Date"].max()

    # ── Last purchase per client-family ──
    last_purchase = (
        agg.sort_values("Date")
        .groupby(["Client_ID", "Product_Family"], as_index=False)
        .last()
    )
    last_purchase["Days_Since_Last"] = (TODAY - last_purchase["Date"]).dt.days

    alerts = []

    for _, row in last_purchase.iterrows():
        block        = row["Analytical_Block"]
        loyalty      = row["Loyalty_Factor"]
        days_since   = row["Days_Since_Last"]
        mean_days    = row["Mean_Days"]
        std_days     = row["Std_Days"]
        last_qty     = row["Quantity"]
        mean_qty     = row["Mean_Qty"]
        std_qty      = row["Std_Qty"]
        avg_spend    = row["Average_Monthly_Spend"]
        max_pot      = row["Max_Client_Potential"]

        # ── Guard: skip if mean_days == 0 (only one effective period) ──
        if mean_days == 0:
            continue

        # ── RULE A: Commodities Capture Window ──
        if block == "Commodities" and loyalty == "Promiscuous":
            if days_since >= mean_days:
                opportunity = max(0.0, float(max_pot) - float(avg_spend))
                alerts.append({
                    **row.to_dict(),
                    "Alert_Rule":        "A",
                    "Motivo":            "Ventana de Captura",
                    "Days_Delayed":      max(0.0, days_since - mean_days),
                    "Valor_Oportunidad": round(opportunity, 2),
                })

        # ── RULE B: Technical Products — Churn Risk ──
        elif block == "Technical":
            # Adjusted expected window correcting for bulk purchases
            expected_days = mean_days * (last_qty / mean_qty) if mean_qty > 0 else mean_days

            triggered = False

            # B1: Anomalous time delay
            if days_since > expected_days + (1.5 * std_days):
                alerts.append({
                    **row.to_dict(),
                    "Alert_Rule":        "B1",
                    "Motivo":            "Retraso anómalo en tiempo",
                    "Days_Delayed":      max(0.0, days_since - expected_days),
                    "Valor_Oportunidad": round(float(avg_spend), 2),
                })
                triggered = True

            # B2: Drastic volume drop (independent check)
            if last_qty < mean_qty - (1.0 * std_qty):
                alerts.append({
                    **row.to_dict(),
                    "Alert_Rule":        "B2",
                    "Motivo":            "Caída drástica de volumen",
                    "Days_Delayed":      max(0.0, days_since - mean_days),
                    "Valor_Oportunidad": round(float(avg_spend), 2),
                })

    if not alerts:
        return pd.DataFrame()

    alerts_df = pd.DataFrame(alerts)

    # ── Deduplicate: keep highest-severity rule per client-family ──
    rule_priority = {"B1": 0, "B2": 1, "A": 2}
    alerts_df["_priority"] = alerts_df["Alert_Rule"].map(rule_priority)
    alerts_df.sort_values("_priority", inplace=True)
    alerts_df.drop_duplicates(subset=["Client_ID", "Product_Family"], keep="first", inplace=True)
    alerts_df.drop(columns=["_priority"], inplace=True)

    return alerts_df.reset_index(drop=True)


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 · PRIORITIZATION SCORE  (Nivel de Riesgo)
# ══════════════════════════════════════════════════════════════════════════════
def compute_risk_score(alerts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Raw_Score = Average_Transaction_Value × (1 + Days_Delayed / Mean_Days)
    Normalized Min-Max → [1, 100], integer.
    Fully transparent formula, no hyperparameters.
    """
    if alerts_df.empty:
        return alerts_df

    # Average transaction value per row
    alerts_df["Average_Transaction_Value"] = alerts_df["Transaction_Value"]

    denom = alerts_df["Mean_Days"].replace(0, np.nan)
    alerts_df["Raw_Score"] = alerts_df["Average_Transaction_Value"] * (
        1 + alerts_df["Days_Delayed"] / denom
    )
    alerts_df["Raw_Score"].fillna(alerts_df["Average_Transaction_Value"], inplace=True)

    mn, mx = alerts_df["Raw_Score"].min(), alerts_df["Raw_Score"].max()
    if mx > mn:
        alerts_df["Nivel_de_Riesgo"] = (
            ((alerts_df["Raw_Score"] - mn) / (mx - mn)) * 99 + 1
        ).round().astype(int)
    else:
        alerts_df["Nivel_de_Riesgo"] = 50  # single alert → neutral score

    return alerts_df


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def risk_color(score: int) -> str:
    if score >= 70:
        return "#ff5252"
    elif score >= 40:
        return "#ffab40"
    return "#69f0ae"


def risk_label(score: int) -> str:
    if score >= 70:
        return "🔴 Alto"
    elif score >= 40:
        return "🟡 Medio"
    return "🟢 Bajo"


def format_currency(val: float) -> str:
    return f"€{val:,.2f}"


def build_progress_bar(score: int) -> str:
    color = risk_color(score)
    pct   = score  # already 1–100
    return (
        f'<div class="risk-bar-wrap">'
        f'<div class="risk-bar-fill" style="width:{pct}%;background:{color};"></div>'
        f'</div>'
        f'<span style="font-size:11px;color:{color};font-weight:700;">{score}</span>'
    )


# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def run_pipeline(filepath: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    df  = load_and_clean(filepath)
    df  = add_analytical_block(df)
    df  = add_loyalty_factor(df)
    agg = aggregate_and_days_between(df)
    agg = compute_statistics(agg)
    alerts = generate_alerts(agg)
    if not alerts.empty:
        alerts = compute_risk_score(alerts)
    return df, alerts


# ══════════════════════════════════════════════════════════════════════════════
#  DEMO DATA GENERATOR  (used when no CSV is uploaded)
# ══════════════════════════════════════════════════════════════════════════════
def generate_demo_csv() -> bytes:
    """
    Generate a plausible synthetic dataset that exercises all alert rules.
    Outputs bytes so it can be used with st.file_uploader mock or saved locally.
    """
    rng = np.random.default_rng(42)
    records = []
    clients = [f"C{str(i).zfill(3)}" for i in range(1, 31)]
    families = [
        "ANESTESIA LOCAL", "AGUJAS DENTALES", "DESINFECTANTE A",   # Commodities
        "IMPLANTES BONE",  "MEMBRANA GUIDED",  "MOTOR ENDODONCIA",  # Technical
        "COMPOSITE NANO",  "BRACKET CERAMIC",  "LASER DIODO",
    ]
    potentials = {c: rng.integers(2000, 15000) for c in clients}

    base_date = pd.Timestamp("2023-01-01")
    for client in clients:
        pot = potentials[client]
        for family in rng.choice(families, size=rng.integers(2, 6), replace=False):
            is_commodity = any(k in family for k in ["ANESTESIA", "AGUJAS", "DESINFEC"])
            n_purchases  = rng.integers(1, 12)
            purchase_date = base_date + pd.Timedelta(days=int(rng.integers(0, 30)))
            interval     = rng.integers(14, 45)
            base_qty     = rng.uniform(50, 500) if is_commodity else rng.uniform(1, 20)
            base_val     = rng.uniform(100, 800)

            for p in range(n_purchases):
                qty = round(base_qty * rng.uniform(0.7, 1.3), 2)
                val = round(base_val * rng.uniform(0.8, 1.2), 2)
                records.append({
                    "Id.Cliente":  client,
                    "Fecha":       purchase_date.strftime("%d/%m/%Y"),
                    "Familia_H":   family,
                    "Unidades":    str(qty).replace(".", ","),
                    "Valores_H":   str(val).replace(".", ","),
                    "Potencial_H": str(float(pot)).replace(".", ","),
                })
                # Introduce some "silent" clients (no recent purchase → triggers alerts)
                gap_multiplier = rng.choice([1, 1, 1, 2.5], p=[0.6, 0.2, 0.1, 0.1])
                purchase_date += pd.Timedelta(days=int(interval * gap_multiplier))

    demo_df = pd.DataFrame(records)
    return demo_df.to_csv(index=False).encode("utf-8")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APP LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
def main():

    # ── Header Banner ──
    st.markdown("""
    <div class="header-banner">
      <div>
        <p class="header-title">📡 Smart Demand Signals</p>
        <p class="header-subtitle">Inibsa · Commercial Intelligence Engine · 100% Rule-Based · Zero Black-Box</p>
      </div>
      <div>
        <span class="header-badge">⚡ HACKATHON LIVE</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    #  SIDEBAR
    # ════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
          <p class="sidebar-brand-title">🦷 Inibsa</p>
          <p class="sidebar-brand-sub">Smart Demand Signals v1.0</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📂 Data Source")
        upload_mode = st.radio(
            "Mode",
            ["Upload CSV", "Use Demo Data"],
            label_visibility="collapsed",
        )

        uploaded_file = None
        if upload_mode == "Upload CSV":
            uploaded_file = st.file_uploader(
                "Drop database_clean.csv here",
                type=["csv"],
                help="CSV with European comma-decimals is fully supported.",
            )
        else:
            st.info("Using synthetic demo dataset with 30 clients & 9 product families.", icon="ℹ️")
            demo_bytes = generate_demo_csv()
            st.download_button(
                "⬇️ Download Demo CSV",
                data=demo_bytes,
                file_name="database_clean_demo.csv",
                mime="text/csv",
            )

        st.markdown("---")
        st.markdown("### 🔎 Filters")

        block_filter = st.multiselect(
            "Analytical Block",
            ["Commodities", "Technical"],
            default=["Commodities", "Technical"],
        )

        min_risk = st.slider(
            "Minimum Risk Score (Nivel de Riesgo)",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
        )

        motivo_options = ["All", "Ventana de Captura", "Retraso anómalo en tiempo", "Caída drástica de volumen"]
        motivo_filter = st.selectbox("Alert Type (Motivo)", motivo_options)

        st.markdown("---")
        st.markdown("### 📊 Legend")
        st.markdown("""
        <div style="font-size:12px;color:#8892a4;line-height:1.8;">
        🔴 <b style="color:#ff5252">Alto</b> — Score ≥ 70<br>
        🟡 <b style="color:#ffab40">Medio</b> — Score 40–69<br>
        🟢 <b style="color:#69f0ae">Bajo</b> — Score < 40
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption(f"Engine clock: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ════════════════════════════════════════════════════════════════════════
    #  LOAD DATA & RUN PIPELINE
    # ════════════════════════════════════════════════════════════════════════
    raw_df     = None
    alerts_df  = None
    pipeline_ok = False

    with st.spinner("🔄 Running Smart Demand Signals pipeline…"):
        try:
            if upload_mode == "Upload CSV" and uploaded_file is not None:
                # Write to a temp path for caching
                import tempfile, os
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                raw_df, alerts_df = run_pipeline(tmp_path)
                os.unlink(tmp_path)
                pipeline_ok = True

            elif upload_mode == "Use Demo Data":
                import tempfile, os
                with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="wb") as tmp:
                    tmp.write(demo_bytes)
                    tmp_path = tmp.name
                raw_df, alerts_df = run_pipeline(tmp_path)
                os.unlink(tmp_path)
                pipeline_ok = True

            elif upload_mode == "Upload CSV" and uploaded_file is None:
                # Try local file as fallback
                import os
                if os.path.exists("database_clean.csv"):
                    raw_df, alerts_df = run_pipeline("database_clean.csv")
                    pipeline_ok = True

        except Exception as e:
            st.error(f"Pipeline error: {e}", icon="🚨")

    # ════════════════════════════════════════════════════════════════════════
    #  NO DATA STATE
    # ════════════════════════════════════════════════════════════════════════
    if not pipeline_ok:
        st.markdown("""
        <div class="empty-state">
          <div class="empty-state-icon">📂</div>
          <div class="empty-state-text">Upload your database_clean.csv or switch to Demo Data in the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
        _render_methodology()
        return

    # ════════════════════════════════════════════════════════════════════════
    #  APPLY FILTERS
    # ════════════════════════════════════════════════════════════════════════
    filtered = alerts_df.copy() if alerts_df is not None and not alerts_df.empty else pd.DataFrame()

    if not filtered.empty:
        if block_filter:
            filtered = filtered[filtered["Analytical_Block"].isin(block_filter)]
        filtered = filtered[filtered["Nivel_de_Riesgo"] >= min_risk]
        if motivo_filter != "All":
            filtered = filtered[filtered["Motivo"] == motivo_filter]
        filtered.sort_values("Nivel_de_Riesgo", ascending=False, inplace=True)
        filtered.reset_index(drop=True, inplace=True)

    # ════════════════════════════════════════════════════════════════════════
    #  KPI CARDS
    # ════════════════════════════════════════════════════════════════════════
    total_alerts    = len(filtered)
    clients_at_risk = filtered["Client_ID"].nunique() if not filtered.empty else 0
    high_risk       = int((filtered["Nivel_de_Riesgo"] >= 70).sum()) if not filtered.empty else 0
    total_opp       = filtered["Valor_Oportunidad"].sum() if not filtered.empty else 0.0

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card blue">
        <div class="kpi-icon">📡</div>
        <div class="kpi-label">Total Alerts</div>
        <div class="kpi-value">{total_alerts}</div>
        <div class="kpi-delta">Filtered result set</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-icon">👤</div>
        <div class="kpi-label">Clients at Risk</div>
        <div class="kpi-value">{clients_at_risk}</div>
        <div class="kpi-delta">Unique client accounts</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-icon">🔥</div>
        <div class="kpi-label">High Risk (≥70)</div>
        <div class="kpi-value">{high_risk}</div>
        <div class="kpi-delta">Immediate action needed</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-icon">💶</div>
        <div class="kpi-label">Total Opportunity</div>
        <div class="kpi-value">€{total_opp:,.0f}</div>
        <div class="kpi-delta">Recoverable revenue</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    #  TABS: Alerts Table | Analytics | Raw Data
    # ════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs(["🚨 Alert Dashboard", "📈 Analytics", "🗃️ Raw Data"])

    # ── TAB 1: ALERT DASHBOARD ──────────────────────────────────────────────
    with tab1:
        if filtered.empty:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-state-icon">✅</div>
              <div class="empty-state-text">No alerts match the current filters. Adjust the sidebar criteria.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="section-header">🚨 Live Alert Table <span style="font-size:12px;color:#64748b;font-weight:400;">— {total_alerts} signals detected · sorted by Nivel de Riesgo</span></div>',
                unsafe_allow_html=True,
            )

            # ── Prepare display dataframe ──
            display_cols = [
                "Client_ID", "Product_Family", "Analytical_Block", "Motivo",
                "Nivel_de_Riesgo", "Days_Since_Last", "Valor_Oportunidad",
                "Loyalty_Factor",
            ]
            display_df = filtered[display_cols].copy()
            display_df["Register_Action"] = ""

            # ── Column config ──
            col_cfg = {
                "Client_ID":         st.column_config.TextColumn("Client ID", width="small"),
                "Product_Family":    st.column_config.TextColumn("Product Family", width="medium"),
                "Analytical_Block":  st.column_config.TextColumn("Block", width="small"),
                "Motivo":            st.column_config.TextColumn("Motivo (Alert Reason)", width="large"),
                "Nivel_de_Riesgo":   st.column_config.ProgressColumn(
                    "Nivel de Riesgo",
                    help="Min-Max normalized score 1–100. Raw_Score = Avg_Value × (1 + Days_Delayed / Mean_Days)",
                    min_value=1,
                    max_value=100,
                    format="%d",
                    width="medium",
                ),
                "Days_Since_Last":   st.column_config.NumberColumn("Days Silent", format="%d d", width="small"),
                "Valor_Oportunidad": st.column_config.NumberColumn("Oportunidad €", format="€%.2f", width="medium"),
                "Loyalty_Factor":    st.column_config.TextColumn("Loyalty", width="small"),
                "Register_Action":   st.column_config.SelectboxColumn(
                    "Register Action",
                    help="Mock feedback loop — tag outcomes to improve future rules.",
                    options=["", "✅ Success", "❌ False Positive"],
                    width="medium",
                ),
            }

            edited = st.data_editor(
                display_df,
                column_config=col_cfg,
                use_container_width=True,
                hide_index=True,
                num_rows="fixed",
                key="alert_table",
            )

            # ── Feedback capture ──
            feedback = edited[edited["Register_Action"] != ""]
            if not feedback.empty:
                tagged_success = int((feedback["Register_Action"] == "✅ Success").sum())
                tagged_fp      = int((feedback["Register_Action"] == "❌ False Positive").sum())
                st.success(
                    f"📝 Feedback captured: **{tagged_success}** successes, **{tagged_fp}** false positives. "
                    "In production this would retrain the threshold parameters automatically.",
                    icon="🔁",
                )

            # ── Download ──
            col_dl1, col_dl2, _ = st.columns([1, 1, 4])
            with col_dl1:
                csv_export = filtered.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Export Alerts CSV",
                    data=csv_export,
                    file_name=f"smart_demand_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                )
            with col_dl2:
                st.caption(f"Last refresh: {datetime.now().strftime('%H:%M:%S')}")

    # ── TAB 2: ANALYTICS ────────────────────────────────────────────────────
    with tab2:
        if filtered.empty:
            st.info("No data to display for current filters.")
        else:
            col_a, col_b = st.columns(2)

            with col_a:
                st.markdown('<div class="section-header">🍰 Alerts by Analytical Block</div>', unsafe_allow_html=True)
                block_counts = filtered["Analytical_Block"].value_counts().reset_index()
                block_counts.columns = ["Block", "Count"]
                st.bar_chart(block_counts.set_index("Block"), color="#2196f3", use_container_width=True)

            with col_b:
                st.markdown('<div class="section-header">📊 Risk Score Distribution</div>', unsafe_allow_html=True)
                bins = pd.cut(filtered["Nivel_de_Riesgo"], bins=[0,39,69,100], labels=["Low","Medium","High"])
                risk_dist = bins.value_counts().reindex(["Low","Medium","High"]).reset_index()
                risk_dist.columns = ["Risk Level", "Count"]
                st.bar_chart(risk_dist.set_index("Risk Level"), color="#ff9800", use_container_width=True)

            col_c, col_d = st.columns(2)

            with col_c:
                st.markdown('<div class="section-header">🔔 Alerts by Motivo</div>', unsafe_allow_html=True)
                motivo_counts = filtered["Motivo"].value_counts().reset_index()
                motivo_counts.columns = ["Motivo", "Count"]
                st.bar_chart(motivo_counts.set_index("Motivo"), color="#4caf50", use_container_width=True)

            with col_d:
                st.markdown('<div class="section-header">💶 Top 10 Opportunity Clients</div>', unsafe_allow_html=True)
                top10 = (
                    filtered.groupby("Client_ID")["Valor_Oportunidad"]
                    .sum()
                    .nlargest(10)
                    .reset_index()
                )
                st.bar_chart(top10.set_index("Client_ID"), color="#e91e63", use_container_width=True)

            # ── Summary statistics table ──
            st.markdown('<div class="section-header">📋 Statistical Summary</div>', unsafe_allow_html=True)
            summary = filtered[["Nivel_de_Riesgo", "Days_Since_Last", "Valor_Oportunidad"]].describe().round(2)
            st.dataframe(summary, use_container_width=True)

    # ── TAB 3: RAW DATA ─────────────────────────────────────────────────────
    with tab3:
        if raw_df is not None:
            st.markdown(
                f'<div class="section-header">🗃️ Ingested Dataset — {len(raw_df):,} clean rows</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                raw_df.head(500),
                use_container_width=True,
                hide_index=True,
            )
            if len(raw_df) > 500:
                st.caption(f"Showing first 500 of {len(raw_df):,} rows.")
        else:
            st.info("Raw data not available.")

    # ════════════════════════════════════════════════════════════════════════
    #  METHODOLOGY EXPANDER
    # ════════════════════════════════════════════════════════════════════════
    _render_methodology()


# ──────────────────────────────────────────────────────────────────────────────
def _render_methodology():
    with st.expander("🔬 Methodology: Why This Is 100% Explainable (No Black Box)", expanded=False):
        st.markdown("""
        ## Smart Demand Signals — Full Algorithmic Transparency

        This engine is built **exclusively on Pandas arithmetic and deterministic business rules**.
        There are no neural networks, gradient boosting models, or probabilistic classifiers.
        Every output is the direct result of a named, auditable formula.

        ---

        ### 1 · Data Ingestion & Decimal Parsing
        ```python
        # European comma-decimals → Python floats (CRITICAL step)
        df[col] = df[col].str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")
        ```
        All three numeric columns (`Quantity`, `Transaction_Value`, `Client_Potential`) are parsed
        this way before any computation. Invalid strings become `NaN` and are dropped — no silent
        data corruption.

        ---

        ### 2 · Analytical Block Classification
        ```
        IF Product_Family.upper() CONTAINS ['ANESTE' | 'AGUJA' | 'DESINFEC']:
            → Commodities
        ELSE:
            → Technical
        ```
        Plain string matching — interpretable by any sales rep without ML knowledge.

        ---

        ### 3 · Loyalty Factor
        ```
        Average_Monthly_Spend = mean(monthly revenue per client)
        IF Average_Monthly_Spend >= 0.85 × Max_Client_Potential:
            → Loyal
        ELSE:
            → Promiscuous
        ```
        The 0.85 threshold is a business parameter, not a learned weight.

        ---

        ### 4 · Statistical Engine
        ```
        Mean_Qty  = mean(Quantity)   per Client × Product_Family
        Std_Qty   = std(Quantity)    per Client × Product_Family
        Mean_Days = mean(Days_Between) per Client × Product_Family
        Std_Days  = std(Days_Between)  per Client × Product_Family

        Cold-Start (<3 purchases): use global Product_Family mean/std instead
        ```

        ---

        ### 5 · Alert Rules

        **Rule A — Ventana de Captura (Commodities)**
        ```
        IF Analytical_Block == 'Commodities'
        AND Loyalty_Factor == 'Promiscuous'
        AND Days_Since_Last >= Mean_Days:
            FIRE ALERT
            Opportunity = max(0, Max_Client_Potential - Average_Monthly_Spend)
        ```

        **Rule B1 — Retraso anómalo en tiempo (Technical)**
        ```
        Expected_Days = Mean_Days × (Last_Qty / Mean_Qty)   # bulk-purchase correction
        IF Days_Since_Last > Expected_Days + 1.5 × Std_Days:
            FIRE ALERT
            Opportunity = Average_Monthly_Spend
        ```

        **Rule B2 — Caída drástica de volumen (Technical)**
        ```
        IF Last_Qty < Mean_Qty - 1.0 × Std_Qty:
            FIRE ALERT
            Opportunity = Average_Monthly_Spend
        ```

        ---

        ### 6 · Nivel de Riesgo (Prioritization Score)
        ```
        Raw_Score = Average_Transaction_Value × (1 + Days_Delayed / Mean_Days)

        Nivel_de_Riesgo = round(
            ((Raw_Score - min) / (max - min)) × 99 + 1
        )  →  integer in [1, 100]
        ```
        Min-Max normalization ensures scores are always comparable within the current
        filtered view. No model weights — just arithmetic.

        ---

        ### 7 · Why No ML?
        | Concern | Pandas Rule Engine | Black-Box ML |
        |---|---|---|
        | Auditability | ✅ Every output traceable to a formula | ❌ Opaque weights |
        | Regulatory compliance | ✅ GDPR-friendly, full explainability | ⚠️ Requires XAI layer |
        | Cold-start | ✅ Explicit fallback rules | ❌ Needs training data |
        | Sales team trust | ✅ "I understand this" | ❌ "Why did it flag me?" |
        | Hackathon demo | ✅ Zero training time | ❌ Risk of overfitting demo |

        > **Conclusion:** For a commercial dental supply context where sales reps must
        > *justify every call they make to a client*, rule-based explainability is not a
        > limitation — it is a competitive advantage.
        """)

        st.markdown("""
        ---
        <div style="text-align:center;color:#4a5568;font-size:12px;">
        Smart Demand Signals · Built for Inibsa Hackathon · 100% Pandas · Zero Black-Box
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
