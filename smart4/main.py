# =============================================================================
#  Smart Demand Signals — main.py (FastAPI Backend)
#  Author : Equipo Inibsa
#  Purpose: Statistical engine, data pipeline, and REST API
# =============================================================================

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import tempfile
import os
from datetime import date

app = FastAPI(title="Smart Demand Signals API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL IN-MEMORY STATE
# ─────────────────────────────────────────────────────────────────────────────
feedback_memory: dict[tuple[str, str], str] = {}

# Score multipliers — DO NOT MODIFY (core statistical logic)
SCORE_CONTEXT_MULTIPLIER = {
    "Fugado a la competencia (>1 año)": 1.5,
    "Ventana de Captura": 1.2,
    "Retraso anómalo en tiempo": 1.0,
    "Caída drástica de volumen": 1.1,
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA INGESTION & CLEANING
# ─────────────────────────────────────────────────────────────────────────────
def load_and_clean_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, dtype=str, sep=";", encoding="latin1")

    rename_map = {
        "Id.Cliente": "Client_ID",
        "Fecha": "Date",
        "Familia_H": "Product_Family",
        "Unidades": "Quantity",
        "Valores_H": "Transaction_Value",
        "Potencial_H": "Client_Potential",
        "Bloque analítico": "Analytical_Block",
    }
    df = df.rename(columns=rename_map)

    for col in ["Quantity", "Transaction_Value", "Client_Potential"]:
        if col in df.columns:
            df[col] = df[col].str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Analytical_Block" in df.columns:
        df["Analytical_Block"] = (
            df["Analytical_Block"]
            .str.strip()
            .replace({"Productos Técnicos": "Technical", "Productos TÃ©cnicos": "Technical"})
        )
    else:
        df["Analytical_Block"] = "Technical"

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Client_ID", "Date", "Product_Family", "Quantity", "Transaction_Value"])
    df = df[(df["Quantity"] > 0) & (df["Transaction_Value"] > 0)].copy()
    df["Client_Potential"] = df["Client_Potential"].fillna(0)
    df["Client_ID"] = df["Client_ID"].astype(str).str.strip()
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2. FEATURE ENGINEERING
# ─────────────────────────────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df["YearMonth"] = df["Date"].dt.to_period("M")
    monthly = df.groupby(["Client_ID", "YearMonth"])["Transaction_Value"].sum().reset_index()
    avg_monthly = (
        monthly.groupby("Client_ID")["Transaction_Value"]
        .mean()
        .reset_index()
        .rename(columns={"Transaction_Value": "Average_Monthly_Spend"})
    )
    max_pot = (
        df.groupby("Client_ID")["Client_Potential"]
        .max()
        .reset_index()
        .rename(columns={"Client_Potential": "Max_Client_Potential"})
    )

    loyalty_df = avg_monthly.merge(max_pot, on="Client_ID", how="left")
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

    agg = (
        df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False)
        .agg(
            Quantity=("Quantity", "sum"),
            Transaction_Value=("Transaction_Value", "sum"),
            Analytical_Block=("Analytical_Block", "first"),
            Loyalty_Factor=("Loyalty_Factor", "first"),
        )
        .sort_values(["Client_ID", "Product_Family", "Date"])
        .reset_index(drop=True)
    )

    agg["Days_Between"] = agg.groupby(["Client_ID", "Product_Family"])["Date"].diff().dt.days
    return agg


# ─────────────────────────────────────────────────────────────────────────────
# 3. STATISTICAL ENGINE & ALERT GENERATION — DO NOT MODIFY CORE LOGIC
# ─────────────────────────────────────────────────────────────────────────────
def generate_alerts(agg: pd.DataFrame, today_simulated) -> pd.DataFrame:
    pair_stats = agg.groupby(["Client_ID", "Product_Family"]).agg(
        Purchase_Count=("Quantity", "count"),
        Mean_Qty=("Quantity", "mean"),
        Std_Qty=("Quantity", "std"),
        Mean_Days=("Days_Between", "mean"),
        Std_Days=("Days_Between", "std"),
        Avg_Txn_Value=("Transaction_Value", "mean"),
    ).reset_index()

    global_stats = agg.groupby("Product_Family").agg(
        G_Mean_Qty=("Quantity", "mean"),
        G_Std_Qty=("Quantity", "std"),
        G_Mean_Days=("Days_Between", "mean"),
        G_Std_Days=("Days_Between", "std"),
    ).reset_index()

    stats = pair_stats.merge(global_stats, on="Product_Family", how="left")
    cold = stats["Purchase_Count"] < 3
    stats.loc[cold, "Std_Qty"] = stats.loc[cold, "G_Std_Qty"]
    stats.loc[cold, "Std_Days"] = stats.loc[cold, "G_Std_Days"]
    stats.loc[cold, "Mean_Qty"] = stats.loc[cold, "G_Mean_Qty"]
    stats.loc[cold, "Mean_Days"] = stats.loc[cold, "G_Mean_Days"]
    stats.fillna(0, inplace=True)

    last_purchase = (
        agg.sort_values("Date")
        .groupby(["Client_ID", "Product_Family"])
        .last()
        .reset_index()
    )
    last_purchase["Days_Since_Last"] = (
        pd.Timestamp(today_simulated) - last_purchase["Date"]
    ).dt.days

    df_eval = last_purchase.merge(stats, on=["Client_ID", "Product_Family"], how="left")
    alerts = []
    LIMITE_FUGA = 365

    for _, row in df_eval.iterrows():
        if row["Mean_Days"] <= 0:
            continue

        block, loyal = row["Analytical_Block"], row["Loyalty_Factor"]
        dsl, mean_days, std_days = row["Days_Since_Last"], row["Mean_Days"], row["Std_Days"]
        last_qty, mean_qty, std_qty = row["Quantity"], row["Mean_Qty"], row["Std_Qty"]

        reason, days_delayed = None, 0.0

        if block == "Commodities" and loyal == "Promiscuous":
            if dsl > LIMITE_FUGA:
                reason = "Fugado a la competencia (>1 año)"
                days_delayed = 0
            elif dsl >= mean_days:
                reason = "Ventana de Captura"
                days_delayed = dsl - mean_days

        elif block == "Technical":
            expected_days = mean_days * (last_qty / mean_qty) if mean_qty > 0 else mean_days
            if dsl > LIMITE_FUGA:
                reason = "Fugado a la competencia (>1 año)"
                days_delayed = 0
            elif dsl > expected_days + (1.5 * std_days):
                reason = "Retraso anómalo en tiempo"
                days_delayed = max(0, dsl - expected_days)
            elif last_qty < mean_qty - (1.0 * std_qty):
                reason = "Caída drástica de volumen"
                days_delayed = 0

        if reason:
            tipo_alerta = "Oportunidad" if reason == "Ventana de Captura" else "Riesgo"
            alerts.append({
                "Client_ID": row["Client_ID"],
                "Product_Family": row["Product_Family"],
                "Analytical_Block": block,
                "Tipo": tipo_alerta,
                "Motivo": reason,
                "Days_Since_Last": dsl,
                "Days_Delayed": days_delayed,
                "Mean_Days": mean_days,
                "Average_Transaction_Value": row["Avg_Txn_Value"],
            })

    if not alerts:
        return pd.DataFrame()

    alerts_df = pd.DataFrame(alerts)

    # --- ROBUST NORMALISATION: Log-scaling + P98 Cap — DO NOT MODIFY ---
    alerts_df["_mult"] = alerts_df["Motivo"].map(SCORE_CONTEXT_MULTIPLIER).fillna(1.0)
    raw_score = (
        alerts_df["Average_Transaction_Value"]
        * (1 + (alerts_df["Days_Delayed"] / alerts_df["Mean_Days"].replace(0, 1)))
        * alerts_df["_mult"]
    )
    cap_val = raw_score.quantile(0.98)
    raw_score = raw_score.clip(upper=cap_val)
    log_score = np.log1p(raw_score)

    l_min, l_max = log_score.min(), log_score.max()
    if l_max == l_min:
        alerts_df["Nivel de Riesgo"] = 50
    else:
        alerts_df["Nivel de Riesgo"] = (
            1 + 99 * (log_score - l_min) / (l_max - l_min + 1e-6)
        ).round(0).astype(int)

    # --- APPLY FEEDBACK PENALTY WEIGHTS ---
    for idx, r in alerts_df.iterrows():
        key = (r["Client_ID"], r["Product_Family"])
        if key in feedback_memory:
            action = feedback_memory[key]
            if action == "❌ Falso Positivo":
                alerts_df.at[idx, "Nivel de Riesgo"] = int(alerts_df.at[idx, "Nivel de Riesgo"] * 0.1)
            elif action == "✅ Venta Recuperada":
                alerts_df.at[idx, "Nivel de Riesgo"] = int(alerts_df.at[idx, "Nivel de Riesgo"] * 0.5)

    alerts_df = alerts_df.sort_values("Nivel de Riesgo", ascending=False)
    return alerts_df


# ─────────────────────────────────────────────────────────────────────────────
# PYDANTIC MODELS
# ─────────────────────────────────────────────────────────────────────────────
class FeedbackPayload(BaseModel):
    Client_ID: str
    Product_Family: str
    Action: str  # "", "✅ Venta Recuperada", or "❌ Falso Positivo"


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload_and_process(
    file: UploadFile = File(...),
    sim_date: str = Form(...),
):
    """
    Accepts a CSV file + simulated date string (YYYY-MM-DD).
    Runs the full pipeline and returns actionable alerts (Nivel de Riesgo >= 20).
    """
    try:
        today = pd.Timestamp(sim_date)
    except Exception:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {sim_date}")

    suffix = ".csv" if file.filename.endswith(".csv") else ".xlsx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        raw_df = load_and_clean_data(tmp_path)
    except Exception as e:
        os.unlink(tmp_path)
        raise HTTPException(status_code=422, detail=f"Data loading error: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    fecha_limite = today - pd.DateOffset(years=2)
    df_filtered = raw_df[(raw_df["Date"] >= fecha_limite) & (raw_df["Date"] <= today)].copy()

    if df_filtered.empty:
        return {"alerts": [], "meta": {"total": 0, "clients": 0, "critical": 0}}

    agg_df = build_features(df_filtered)
    alerts_df = generate_alerts(agg_df, today)

    if alerts_df.empty:
        return {"alerts": [], "meta": {"total": 0, "clients": 0, "critical": 0}}

    # Filter actionable alerts (Priority >= 20)
    actionable = alerts_df[alerts_df["Nivel de Riesgo"] >= 20].copy()

    meta = {
        "total": len(actionable),
        "clients": int(actionable["Client_ID"].nunique()),
        "critical": int((actionable["Nivel de Riesgo"] >= 70).sum()),
        "sim_date": sim_date,
    }

    # Serialize: convert non-JSON-native types
    actionable["Date_str"] = actionable["Days_Since_Last"].apply(lambda x: str(x))
    records = actionable[[
        "Nivel de Riesgo", "Tipo", "Client_ID", "Product_Family",
        "Motivo", "Days_Since_Last", "Analytical_Block",
        "Average_Transaction_Value", "Days_Delayed", "Mean_Days",
    ]].copy()
    records["Days_Since_Last"] = records["Days_Since_Last"].astype(int)
    records["Days_Delayed"] = records["Days_Delayed"].round(1)
    records["Average_Transaction_Value"] = records["Average_Transaction_Value"].round(2)
    records["Mean_Days"] = records["Mean_Days"].round(1)

    return {"alerts": records.to_dict(orient="records"), "meta": meta}


@app.post("/feedback")
def post_feedback(payload: FeedbackPayload):
    """
    Updates the in-memory feedback dictionary.
    Subsequent /upload calls will apply penalty weights accordingly.
    """
    key = (payload.Client_ID, payload.Product_Family)
    if payload.Action == "":
        feedback_memory.pop(key, None)
    else:
        feedback_memory[key] = payload.Action
    return {"status": "ok", "memory_size": len(feedback_memory)}


@app.post("/clear_feedback")
def clear_feedback():
    """Clears all feedback memory."""
    feedback_memory.clear()
    return {"status": "cleared"}


@app.get("/health")
def health():
    return {"status": "ok", "memory_entries": len(feedback_memory)}