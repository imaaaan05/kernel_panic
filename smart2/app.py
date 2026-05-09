# =============================================================================
#  Smart Demand Signals — app.py
#  Author : Lead Data Scientist / Python-Streamlit Architect
#  Client : Inibsa (Dental / Pharmaceutical)
#  Purpose: 24-h Hackathon — 100 % explainable, Pandas-only alert engine
#           + Streamlit dashboard with ML-feedback loop mock-up
# =============================================================================

# ── Dependencies ──────────────────────────────────────────────────────────────
# pip install streamlit pandas openpyxl xlrd
# Run: streamlit run app.py
# =============================================================================

import pandas as pd
import streamlit as st
import os

# ─────────────────────────────────────────────────────────────────────────────
# 0.  PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Demand Signals · Inibsa",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — polished look that works on both light and dark themes
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ── Global font ───────────────────────────────────────────────── */
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        /* ── Top banner ────────────────────────────────────────────────── */
        .banner {
            background: linear-gradient(135deg, #1a3a5c 0%, #0d6efd 100%);
            border-radius: 12px;
            padding: 24px 32px;
            margin-bottom: 24px;
            color: #fff;
        }
        .banner h1 { margin: 0; font-size: 2rem; font-weight: 700; }
        .banner p  { margin: 4px 0 0; font-size: 0.95rem; opacity: 0.85; }

        /* ── KPI cards ─────────────────────────────────────────────────── */
        .kpi-card {
            background: #f0f4ff;
            border: 1px solid #c9d9f7;
            border-radius: 10px;
            padding: 18px 22px;
            text-align: center;
        }
        .kpi-card .kpi-value {
            font-size: 2rem;
            font-weight: 800;
            color: #0d6efd;
        }
        .kpi-card .kpi-label {
            font-size: 0.8rem;
            color: #555;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ── Risk badge colours ─────────────────────────────────────────── */
        .badge-high   { color:#b91c1c; font-weight:700; }
        .badge-medium { color:#c2760a; font-weight:700; }
        .badge-low    { color:#166534; font-weight:700; }

        /* ── Section headers ────────────────────────────────────────────── */
        .section-header {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1a3a5c;
            border-left: 4px solid #0d6efd;
            padding-left: 10px;
            margin: 20px 0 10px;
        }

        /* ── Sidebar tweaks ─────────────────────────────────────────────── */
        section[data-testid="stSidebar"] { background: #f7f9ff; }
        .sidebar-logo {
            font-size: 1.4rem;
            font-weight: 800;
            color: #1a3a5c;
            margin-bottom: 4px;
        }
        .sidebar-sub {
            font-size: 0.75rem;
            color: #666;
            margin-bottom: 20px;
        }

        /* ── Data-editor container ──────────────────────────────────────── */
        .stDataFrame { border-radius: 8px; overflow: hidden; }

        /* ── Footer ─────────────────────────────────────────────────────── */
        .footer {
            text-align: center;
            font-size: 0.72rem;
            color: #aaa;
            margin-top: 40px;
            padding-top: 12px;
            border-top: 1px solid #eee;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 — DATA LOADING & PREPARATION
# ─────────────────────────────────────────────────────────────────────────────

# ── 1a. Locate the data file ──────────────────────────────────────────────────
@st.cache_data(show_spinner="📂  Loading dataset…")
def load_raw_data(path: str) -> pd.DataFrame:
    """
    Load database_clean.xlsx (preferred) or database_clean.csv.
    Renames Spanish column headers to English equivalents.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    else:
        # Try common separators for CSV files
        df = pd.read_csv(path, sep=None, engine="python")

    # ── Column rename map ────────────────────────────────────────────────────
    rename_map = {
        "Id.Cliente"  : "Client_ID",
        "Fecha"       : "Date",
        "Familia_H"   : "Product_Family",
        "Unidades"    : "Quantity",
        "Valores_H"   : "Transaction_Value",
        "Potencial_H" : "Client_Potential",
    }
    df = df.rename(columns=rename_map)

    # ── Type coercions ───────────────────────────────────────────────────────
    df["Date"]              = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    # Reemplazar comas por puntos ANTES de convertir a número
    df["Quantity"]          = pd.to_numeric(df["Quantity"].astype(str).str.replace(',', '.'), errors="coerce")
    df["Transaction_Value"] = pd.to_numeric(df["Transaction_Value"].astype(str).str.replace(',', '.'), errors="coerce")
    df["Client_Potential"]  = pd.to_numeric(df["Client_Potential"].astype(str).str.replace(',', '.'), errors="coerce")

    # Drop rows where critical fields are null
    df = df.dropna(subset=["Client_ID", "Date", "Product_Family",
                            "Quantity", "Transaction_Value"])
    return df


# ── 1b. Analytical Block classification ──────────────────────────────────────
def classify_block(product_family: str) -> str:
    """
    Rule-based classifier (100 % explainable — no ML):
      • Contains 'ANESTE', 'AGUJA', or 'DESINFEC' → 'Commodities'
      • Everything else                            → 'Technical'
    """
    pf_upper = str(product_family).upper()
    commodity_keywords = ("ANESTE", "AGUJA", "DESINFEC")
    if any(kw in pf_upper for kw in commodity_keywords):
        return "Commodities"
    return "Technical"


# ── 1c. Loyalty Factor ────────────────────────────────────────────────────────
def compute_loyalty(df: pd.DataFrame) -> pd.DataFrame:
    """
    Average_Monthly_Spend  = mean Transaction_Value per Client_ID.
    Loyal      → Average_Monthly_Spend >= 0.85 × Client_Potential
    Promiscuous → below that threshold  (likely buying from competitors)
    """
    avg_spend = (
        df.groupby("Client_ID")["Transaction_Value"]
        .mean()
        .rename("Average_Monthly_Spend")
        .reset_index()
    )
    df = df.merge(avg_spend, on="Client_ID", how="left")

    # Client_Potential may vary per row; use the max per client as the reference
    pot_ref = (
        df.groupby("Client_ID")["Client_Potential"]
        .max()
        .rename("Max_Potential")
        .reset_index()
    )
    df = df.merge(pot_ref, on="Client_ID", how="left")

    df["Loyalty_Factor"] = df.apply(
        lambda r: "Loyal"
        if r["Average_Monthly_Spend"] >= 0.85 * r["Max_Potential"]
        else "Promiscuous",
        axis=1,
    )
    return df


# ── 1d. Analytical Block column ───────────────────────────────────────────────
def add_analytical_block(df: pd.DataFrame) -> pd.DataFrame:
    df["Analytical_Block"] = df["Product_Family"].apply(classify_block)
    return df


# ── 1e. Aggregation at [Client_ID, Date, Product_Family] level ────────────────
def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse to the grain: Client_ID × Date × Product_Family.
    Sum Quantity and Transaction_Value.
    Carry forward the pre-computed loyalty columns.
    """
    agg = (
        df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False)
        .agg(
            Quantity             = ("Quantity",             "sum"),
            Transaction_Value    = ("Transaction_Value",    "sum"),
            Average_Monthly_Spend= ("Average_Monthly_Spend","first"),
            Max_Potential        = ("Max_Potential",        "first"),
            Loyalty_Factor       = ("Loyalty_Factor",       "first"),
            Analytical_Block     = ("Analytical_Block",     "first"),
        )
        .sort_values(["Client_ID", "Product_Family", "Date"])
        .reset_index(drop=True)
    )

    # ── Days_Between consecutive purchases (per Client/Family pair) ──────────
    agg["Days_Between"] = (
        agg.groupby(["Client_ID", "Product_Family"])["Date"]
        .diff()
        .dt.days
    )
    return agg


# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 — STATISTICAL BASELINES & COLD-START FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

def compute_baselines(agg: pd.DataFrame) -> pd.DataFrame:
    """
    For each Client × Family pair:
      - Mean_Qty, Std_Qty         (from Quantity)
      - Mean_Days, Std_Days       (from Days_Between)
    Cold-start rule: if a client has < 3 purchases for a family, NaN std
    → replaced with the GLOBAL mean/std of that Product_Family.
    """

    # ── Per-pair stats ────────────────────────────────────────────────────────
    pair_stats = (
        agg.groupby(["Client_ID", "Product_Family"])
        .agg(
            Purchase_Count  = ("Quantity",      "count"),
            Mean_Qty        = ("Quantity",      "mean"),
            Std_Qty         = ("Quantity",      "std"),
            Mean_Days       = ("Days_Between",  "mean"),
            Std_Days        = ("Days_Between",  "std"),
            Avg_Txn_Value   = ("Transaction_Value", "mean"),
        )
        .reset_index()
    )

    # ── Global (family-level) fallback stats ──────────────────────────────────
    global_stats = (
        agg.groupby("Product_Family")
        .agg(
            Global_Mean_Qty   = ("Quantity",     "mean"),
            Global_Std_Qty    = ("Quantity",     "std"),
            Global_Mean_Days  = ("Days_Between", "mean"),
            Global_Std_Days   = ("Days_Between", "std"),
        )
        .reset_index()
    )

    pair_stats = pair_stats.merge(global_stats, on="Product_Family", how="left")

    # ── Cold-start fill (< 3 purchases → use global fallback) ─────────────────
    cold = pair_stats["Purchase_Count"] < 3

    pair_stats.loc[cold, "Std_Qty"]   = pair_stats.loc[cold, "Global_Std_Qty"]
    pair_stats.loc[cold, "Std_Days"]  = pair_stats.loc[cold, "Global_Std_Days"]
    pair_stats.loc[cold, "Mean_Qty"]  = pair_stats.loc[cold, "Global_Mean_Qty"]
    pair_stats.loc[cold, "Mean_Days"] = pair_stats.loc[cold, "Global_Mean_Days"]

    # ── Safety: if Std is still NaN (family has < 2 records total) → 0 ────────
    pair_stats["Std_Qty"]  = pair_stats["Std_Qty"].fillna(0)
    pair_stats["Std_Days"] = pair_stats["Std_Days"].fillna(0)

    # ── Drop helper columns ───────────────────────────────────────────────────
    pair_stats = pair_stats.drop(
        columns=["Global_Mean_Qty", "Global_Std_Qty",
                 "Global_Mean_Days", "Global_Std_Days"],
    )
    return pair_stats


# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 — ALERT LOGIC
# ─────────────────────────────────────────────────────────────────────────────

def generate_alerts(agg: pd.DataFrame, pair_stats: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates Rule A (Commodities / Capture Window) and
    Rule B (Technical / Churn Risk) for every Client × Family pair.

    'Today' is defined as the maximum Date in the dataset
    (so the logic works on historical data without touching real-time APIs).
    """

    today = agg["Date"].max()

    # ── Last purchase snapshot per Client × Family ────────────────────────────
    last_purchase = (
        agg.sort_values("Date")
        .groupby(["Client_ID", "Product_Family"])
        .last()
        .reset_index()
        [["Client_ID", "Product_Family", "Date", "Quantity",
          "Transaction_Value", "Loyalty_Factor", "Analytical_Block",
          "Average_Monthly_Spend", "Max_Potential"]]
        .rename(columns={
            "Date"             : "Last_Purchase_Date",
            "Quantity"         : "Last_Qty",
            "Transaction_Value": "Last_Txn_Value",
        })
    )

    last_purchase["Days_Since_Last"] = (
        today - last_purchase["Last_Purchase_Date"]
    ).dt.days

    # ── Merge stats ───────────────────────────────────────────────────────────
    df_eval = last_purchase.merge(pair_stats, on=["Client_ID", "Product_Family"], how="left")

    alerts = []

    for _, row in df_eval.iterrows():

        cid   = row["Client_ID"]
        fam   = row["Product_Family"]
        block = row["Analytical_Block"]
        loyal = row["Loyalty_Factor"]
        dsl   = row["Days_Since_Last"]      # Days Since Last purchase

        mean_days = row["Mean_Days"]
        std_days  = row["Std_Days"]
        mean_qty  = row["Mean_Qty"]
        std_qty   = row["Std_Qty"]
        last_qty  = row["Last_Qty"]
        avg_spend = row["Average_Monthly_Spend"]
        max_pot   = row["Max_Potential"]
        avg_txn   = row["Avg_Txn_Value"]

        # Skip if baselines are not meaningful (single purchase, no recurrence)
        if pd.isna(mean_days) or mean_days <= 0:
            continue

        # ── RULE A — Commodities / Capture Window ─────────────────────────────
        if block == "Commodities" and loyal == "Promiscuous":
            if dsl >= mean_days:
                opportunity = max(0, max_pot - avg_spend)
                alerts.append(
                    {
                        "Client_ID"           : cid,
                        "Product_Family"      : fam,
                        "Analytical_Block"    : block,
                        "Loyalty_Factor"      : loyal,
                        "Alert_Reason"        : "Ventana de Captura",
                        "Days_Since_Last"     : dsl,
                        "Mean_Days"           : round(mean_days, 1),
                        "Days_Delayed"        : round(dsl - mean_days, 1),
                        "Last_Qty"            : last_qty,
                        "Mean_Qty"            : round(mean_qty, 2),
                        "Average_Transaction_Value": avg_txn,
                        "Average_Monthly_Spend"   : avg_spend,
                        "Opportunity_Value"   : round(opportunity, 2),
                    }
                )

        # ── RULE B — Technical Products / Churn Risk ──────────────────────────
        elif block == "Technical":

            # Expected Days: scale by bulk-purchase ratio
            mean_qty_safe   = mean_qty if mean_qty > 0 else 1
            expected_days   = mean_days * (last_qty / mean_qty_safe)

            time_condition  = dsl > expected_days + (1.5 * std_days)
            qty_condition   = last_qty < mean_qty - (1.0 * std_qty)

            reason = None
            if time_condition:
                reason = "Retraso anómalo en tiempo"
            elif qty_condition:
                reason = "Caída drástica de volumen"

            if reason:
                alerts.append(
                    {
                        "Client_ID"           : cid,
                        "Product_Family"      : fam,
                        "Analytical_Block"    : block,
                        "Loyalty_Factor"      : loyal,
                        "Alert_Reason"        : reason,
                        "Days_Since_Last"     : dsl,
                        "Mean_Days"           : round(mean_days, 1),
                        "Days_Delayed"        : round(dsl - expected_days, 1),
                        "Last_Qty"            : last_qty,
                        "Mean_Qty"            : round(mean_qty, 2),
                        "Average_Transaction_Value": avg_txn,
                        "Average_Monthly_Spend"   : avg_spend,
                        "Opportunity_Value"   : round(avg_spend, 2),
                    }
                )

    if not alerts:
        return pd.DataFrame()

    return pd.DataFrame(alerts)


# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 — PRIORITIZATION SCORE (1–100)
# ─────────────────────────────────────────────────────────────────────────────

def add_priority_score(alerts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Raw_Score = Average_Transaction_Value × (1 + Days_Delayed / Mean_Days)

    Min-Max normalised to [1, 100], rounded to 0 decimals.
    Column name: 'Nivel de Riesgo'
    """
    if alerts_df.empty:
        alerts_df["Nivel de Riesgo"] = pd.Series(dtype=float)
        return alerts_df

    # Guard against division by zero in Days_Delayed / Mean_Days
    mean_days_safe = alerts_df["Mean_Days"].replace(0, 1)
    days_delayed   = alerts_df["Days_Delayed"].clip(lower=0)

    raw = alerts_df["Average_Transaction_Value"] * (
        1 + days_delayed / mean_days_safe
    )

    r_min, r_max = raw.min(), raw.max()

    if r_max == r_min:
        # All scores identical → assign mid-range value
        alerts_df["Nivel de Riesgo"] = 50
    else:
        normalised = 1 + 99 * (raw - r_min) / (r_max - r_min)
        alerts_df["Nivel de Riesgo"] = normalised.round(0).astype(int)

    return alerts_df


# ─────────────────────────────────────────────────────────────────────────────
# MASTER PIPELINE — cached for performance
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="⚙️  Running alert engine…")
def run_pipeline(path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns:
        raw_df     — original renamed dataframe
        agg        — aggregated dataframe with loyalty / block columns
        alerts_df  — final alerts with priority scores
    """
    raw_df     = load_raw_data(path)
    df         = add_analytical_block(raw_df)
    df         = compute_loyalty(df)
    agg        = aggregate_data(df)
    pair_stats = compute_baselines(agg)
    alerts_df  = generate_alerts(agg, pair_stats)

    if not alerts_df.empty:
        alerts_df = add_priority_score(alerts_df)
        alerts_df = alerts_df.sort_values("Nivel de Riesgo", ascending=False).reset_index(drop=True)

    return raw_df, agg, alerts_df


# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 — STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">💊 Smart Demand Signals</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Inibsa · Dental & Pharma Analytics</div>', unsafe_allow_html=True)
    st.divider()

    # ── File uploader (primary) or fall-back to local file ───────────────────
    uploaded = st.file_uploader(
        "Upload dataset",
        type=["xlsx", "xls", "csv"],
        help="Upload database_clean.xlsx or .csv",
    )

    st.divider()

    # ── Analytical Block filter ───────────────────────────────────────────────
    block_filter = st.selectbox(
        "🔍 Analytical Block",
        options=["All", "Commodities", "Technical"],
        index=0,
    )

    # ── Risk level filter ─────────────────────────────────────────────────────
    risk_range = st.slider(
        "🎚️ Nivel de Riesgo (min)",
        min_value=1,
        max_value=100,
        value=1,
        step=1,
    )

    st.divider()
    st.markdown(
        """
        **Alert Logic Legend**
        - 🟠 **Ventana de Captura** — Commodities overdue; client likely buying from a competitor.
        - 🔴 **Retraso anómalo** — Technical product delay exceeds statistical threshold.
        - 🟡 **Caída de volumen** — Technical product quantity dropped sharply.

        ---
        **Feedback Loop**
        Use the *Register Action* column to label each alert outcome.
        These labels power future model refinement.
        """,
        unsafe_allow_html=False,
    )

# ── Top banner ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="banner">
        <h1>📡 Smart Demand Signals</h1>
        <p>Explainable, rule-based commercial alert engine &mdash; 100 % Pandas &bull; Zero black-box ML</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Resolve data path ─────────────────────────────────────────────────────────
data_path = None
if uploaded is not None:
    # Save uploaded file to a temp location so @st.cache_data can hash it
    import tempfile
    suffix = os.path.splitext(uploaded.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.read())
        data_path = tmp.name
else:
    # Fall back to local files in the same directory as app.py
    for candidate in ("database_clean.xlsx", "database_clean.xls", "database_clean.csv"):
        if os.path.exists(candidate):
            data_path = candidate
            break

if data_path is None:
    st.info(
        "👆  Please upload your **database_clean.xlsx** (or .csv) file using the sidebar, "
        "or place it in the same folder as app.py.",
        icon="📂",
    )
    st.stop()

# ── Run the pipeline ──────────────────────────────────────────────────────────
try:
    raw_df, agg, alerts_df = run_pipeline(data_path)
except Exception as exc:
    st.error(f"❌ Pipeline error: {exc}")
    with st.expander("Show traceback"):
        import traceback
        st.code(traceback.format_exc())
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_alerts     = len(alerts_df)
total_opportunity = alerts_df["Opportunity_Value"].sum() if not alerts_df.empty else 0
n_clients        = alerts_df["Client_ID"].nunique()  if not alerts_df.empty else 0
n_high_risk      = (alerts_df["Nivel de Riesgo"] >= 70).sum() if not alerts_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{total_alerts}</div>'
        f'<div class="kpi-label">Total Alerts</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{n_clients}</div>'
        f'<div class="kpi-label">Clients at Risk</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">{n_high_risk}</div>'
        f'<div class="kpi-label">High Risk (≥70)</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="kpi-card">'
        f'<div class="kpi-value">€{total_opportunity:,.0f}</div>'
        f'<div class="kpi-label">Total Opportunity (€)</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# APPLY SIDEBAR FILTERS
# ─────────────────────────────────────────────────────────────────────────────
if alerts_df.empty:
    st.warning("⚠️ No alerts generated. Check that your dataset has enough purchase history (≥ 2 purchases per Client/Family pair).")
    st.stop()

filtered_df = alerts_df.copy()

if block_filter != "All":
    filtered_df = filtered_df[filtered_df["Analytical_Block"] == block_filter]

filtered_df = filtered_df[filtered_df["Nivel de Riesgo"] >= risk_range]

# ─────────────────────────────────────────────────────────────────────────────
# ALERT TABLE (interactive st.data_editor)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚨 Commercial Alerts — Sales Action Board</div>', unsafe_allow_html=True)
st.caption(
    f"Showing **{len(filtered_df)}** of **{total_alerts}** alerts · "
    f"'Today' = **{agg['Date'].max().strftime('%d %b %Y')}** (max date in dataset)"
)

# ── Build display dataframe ───────────────────────────────────────────────────
DISPLAY_COLS = [
    "Client_ID",
    "Product_Family",
    "Analytical_Block",
    "Alert_Reason",
    "Nivel de Riesgo",
    "Days_Since_Last",
    "Opportunity_Value",
    "Register_Action",
]

# Add the feedback column (empty by default)
display_df = filtered_df.copy().reset_index(drop=True)
display_df["Register_Action"] = ""

# Rename for Spanish-friendly display
display_df = display_df.rename(
    columns={
        "Alert_Reason"     : "Motivo",
        "Opportunity_Value": "Valor_Oportunidad (€)",
    }
)

DISPLAY_COLS_RENAMED = [
    "Client_ID",
    "Product_Family",
    "Analytical_Block",
    "Motivo",
    "Nivel de Riesgo",
    "Days_Since_Last",
    "Valor_Oportunidad (€)",
    "Register_Action",
]

# ── Persist edited feedback in session state ──────────────────────────────────
if "feedback_df" not in st.session_state:
    st.session_state.feedback_df = display_df[DISPLAY_COLS_RENAMED].copy()
else:
    # If filter changed, rebuild but preserve prior feedback entries
    prev = st.session_state.feedback_df
    merged = display_df[DISPLAY_COLS_RENAMED].copy()
    # Match on Client_ID + Product_Family + Motivo to carry over saved actions
    key_cols = ["Client_ID", "Product_Family", "Motivo"]
    if all(c in prev.columns for c in key_cols):
        saved = prev[key_cols + ["Register_Action"]].rename(
            columns={"Register_Action": "Saved_Action"}
        )
        merged = merged.merge(saved, on=key_cols, how="left")
        merged["Register_Action"] = merged["Saved_Action"].where(
            merged["Saved_Action"].notna() & (merged["Saved_Action"] != ""),
            other=merged["Register_Action"],
        )
        merged = merged.drop(columns=["Saved_Action"])
    st.session_state.feedback_df = merged

# ── Render data editor ────────────────────────────────────────────────────────
edited = st.data_editor(
    st.session_state.feedback_df,
    use_container_width=True,
    hide_index=True,
    num_rows="fixed",
    column_config={
        "Client_ID": st.column_config.TextColumn(
            "Client ID", disabled=True, width="small"
        ),
        "Product_Family": st.column_config.TextColumn(
            "Product Family", disabled=True, width="medium"
        ),
        "Analytical_Block": st.column_config.TextColumn(
            "Block", disabled=True, width="small"
        ),
        "Motivo": st.column_config.TextColumn(
            "Alert Reason (Motivo)", disabled=True, width="large"
        ),
        "Nivel de Riesgo": st.column_config.ProgressColumn(
            "Nivel de Riesgo",
            help="Priority score 1–100 (higher = more urgent)",
            min_value=0,
            max_value=100,
            format="%d",
            width="medium",
        ),
        "Days_Since_Last": st.column_config.NumberColumn(
            "Days Since Last", disabled=True, width="small", format="%d days"
        ),
        "Valor_Oportunidad (€)": st.column_config.NumberColumn(
            "Oportunidad (€)",
            disabled=True,
            width="medium",
            format="€%.2f",
        ),
        "Register_Action": st.column_config.SelectboxColumn(
            "📝 Register Action",
            help="Log the outcome of this alert (ML Feedback Loop)",
            width="medium",
            options=["", "✅ Success", "❌ False Positive", "⏳ Pending Follow-up"],
            required=False,
            default="",
        ),
    },
    key="alert_editor",
)

# Persist edits back into session state
st.session_state.feedback_df = edited

# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK EXPORT
# ─────────────────────────────────────────────────────────────────────────────
labeled_mask = edited["Register_Action"].isin(
    ["✅ Success", "❌ False Positive", "⏳ Pending Follow-up"]
)
n_labeled = labeled_mask.sum()

if n_labeled > 0:
    st.success(f"✅ {n_labeled} alert(s) labeled — ready for feedback export.")
    csv_feedback = edited[labeled_mask].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Feedback CSV",
        data=csv_feedback,
        file_name="smart_demand_signals_feedback.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────────────────────────────────────
# EXPANDERS — detail / diagnostics
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

with st.expander("📊 Alert Distribution by Block & Reason"):
    if not filtered_df.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Alerts by Analytical Block**")
            block_counts = filtered_df["Analytical_Block"].value_counts().reset_index()
            block_counts.columns = ["Block", "Count"]
            st.dataframe(block_counts, hide_index=True, use_container_width=True)

        with col_b:
            st.markdown("**Alerts by Reason**")
            reason_counts = filtered_df["Alert_Reason"].value_counts().reset_index()
            reason_counts.columns = ["Alert Reason", "Count"]
            st.dataframe(reason_counts, hide_index=True, use_container_width=True)

        st.markdown("**Top 10 Opportunities by Client**")
        top_clients = (
            filtered_df.groupby("Client_ID")["Opportunity_Value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_clients.columns = ["Client_ID", "Total Opportunity (€)"]
        top_clients["Total Opportunity (€)"] = top_clients["Total Opportunity (€)"].map("€{:,.2f}".format)
        st.dataframe(top_clients, hide_index=True, use_container_width=True)

with st.expander("🔬 Raw Alert Data (full columns)"):
    st.dataframe(
        filtered_df.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("📋 Aggregated Transaction Data"):
    st.dataframe(agg, use_container_width=True, hide_index=True)

with st.expander("📌 Methodology & Rule Explainer"):
    st.markdown(
        """
        ### Alert Engine — Decision Rules

        All logic is **100 % rule-based** (no black-box ML). Every alert can be fully traced back to the formulas below.

        ---

        #### Analytical Block Classification
        | Keyword in Product Family | Block |
        |---------------------------|-------|
        | ANESTE, AGUJA, DESINFEC   | Commodities |
        | Anything else             | Technical |

        #### Loyalty Factor
        > `Loyal` if `Average_Monthly_Spend ≥ 0.85 × Client_Potential`

        #### Statistical Baselines
        - Computed per **Client × Product Family** pair.
        - **Cold-start fallback**: if < 3 purchases → use **global Product Family** mean & std.

        ---

        #### Rule A — Ventana de Captura (Commodities only)
        ```
        Condition : Block == 'Commodities'
                    AND Loyalty == 'Promiscuous'
                    AND Days_Since_Last >= Mean_Days

        Opportunity = Client_Potential − Average_Monthly_Spend
        ```

        #### Rule B — Technical Churn Risk
        ```
        Expected_Days = Mean_Days × (Last_Qty / Mean_Qty)

        Time  alert : Days_Since_Last > Expected_Days + 1.5 × Std_Days
                      → "Retraso anómalo en tiempo"

        Volume alert: Last_Qty < Mean_Qty − 1.0 × Std_Qty
                      → "Caída drástica de volumen"

        Opportunity = Average_Monthly_Spend  (revenue at risk)
        ```

        #### Priority Score — Nivel de Riesgo
        ```
        Raw_Score     = Avg_Transaction_Value × (1 + Days_Delayed / Mean_Days)
        Nivel_Riesgo  = Min-Max normalise Raw_Score → [1, 100]
        ```

        ---
        #### Feedback Loop (Mock-up)
        The **Register Action** column lets sales reps label each alert as:
        - ✅ **Success** — alert led to a recovered sale
        - ❌ **False Positive** — alert was incorrect
        - ⏳ **Pending Follow-up** — under investigation

        Exported feedback CSVs can be used to retrain future statistical thresholds or supervised models.
        """
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Smart Demand Signals v1.0 · Inibsa · Built for 24-h Hackathon · '
    'Powered by Pandas + Streamlit · No black-box ML</div>',
    unsafe_allow_html=True,
)
