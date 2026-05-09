# =============================================================================
#  Smart Demand Signals — app.py (VERSIÓN FINAL HACKATHON)
#  Author : Equipo Inibsa 
#  Purpose: Motor Estadístico 100% Pandas + Dashboard Streamlit
# =============================================================================

import pandas as pd
import numpy as np
import streamlit as st
import os
import tempfile

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN DE PÁGINA Y CSS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Demand Signals · Inibsa", page_icon="💊", layout="wide")

st.markdown("""
    <style>
        .kpi-card { background: #f0f4ff; border: 1px solid #c9d9f7; border-radius: 10px; padding: 18px 22px; text-align: center; }
        .kpi-value { font-size: 2rem; font-weight: 800; color: #0d6efd; }
        .kpi-label { font-size: 0.8rem; color: #555; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
        .section-header { font-size: 1.1rem; font-weight: 700; color: #1a3a5c; border-left: 4px solid #0d6efd; padding-left: 10px; margin: 20px 0 10px; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. INGESTA Y LIMPIEZA DE DATOS (El Fix de los Decimales y CSV)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando y limpiando datos...")
def load_and_clean_data(filepath) -> pd.DataFrame:
    # Leer forzando punto y coma y latin1 para acentos españoles
    df = pd.read_csv(filepath, dtype=str, sep=';', encoding='latin1')

    # Renombrar columnas
    rename_map = {
        "Id.Cliente": "Client_ID",
        "Fecha": "Date",
        "Familia_H": "Product_Family",
        "Unidades": "Quantity",
        "Valores_H": "Transaction_Value",
        "Potencial_H": "Client_Potential",
        "Bloque analítico": "Analytical_Block"
    }
    df = df.rename(columns=rename_map)

    # CRÍTICO: Cambiar comas por puntos en los decimales ANTES de convertir a número
    for col in ["Quantity", "Transaction_Value", "Client_Potential"]:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Estandarizar Bloque Analítico para que funcione la lógica interna
    if "Analytical_Block" in df.columns:
        df["Analytical_Block"] = df["Analytical_Block"].str.strip().replace({'Productos Técnicos': 'Technical', 'Productos TÃ©cnicos': 'Technical'})
    else:
        df["Analytical_Block"] = "Technical" # Fallback

    # Fechas y limpieza de nulos/negativos
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Client_ID", "Date", "Product_Family", "Quantity", "Transaction_Value"])
    df = df[(df["Quantity"] > 0) & (df["Transaction_Value"] > 0)].copy()
    
    df["Client_Potential"] = df["Client_Potential"].fillna(0)
    df["Client_ID"] = df["Client_ID"].astype(str).str.strip()
    
    return df

# ─────────────────────────────────────────────────────────────────────────────
# 2. FEATURE ENGINEERING Y AGRUPACIÓN
# ─────────────────────────────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    # Factor de Lealtad: Gasto Mensual Medio vs Potencial
    df["YearMonth"] = df["Date"].dt.to_period("M")
    monthly = df.groupby(["Client_ID", "YearMonth"])["Transaction_Value"].sum().reset_index()
    avg_monthly = monthly.groupby("Client_ID")["Transaction_Value"].mean().reset_index().rename(columns={"Transaction_Value": "Average_Monthly_Spend"})
    max_pot = df.groupby("Client_ID")["Client_Potential"].max().reset_index().rename(columns={"Client_Potential": "Max_Client_Potential"})
    
    loyalty_df = avg_monthly.merge(max_pot, on="Client_ID", how="left")
    loyalty_df["Loyalty_Factor"] = np.where(loyalty_df["Average_Monthly_Spend"] >= 0.85 * loyalty_df["Max_Client_Potential"], "Loyal", "Promiscuous")
    
    df = df.merge(loyalty_df[["Client_ID", "Average_Monthly_Spend", "Max_Client_Potential", "Loyalty_Factor"]], on="Client_ID", how="left")

    # Agrupación por Cliente, Fecha y Familia
    agg = df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False).agg(
        Quantity=("Quantity", "sum"),
        Transaction_Value=("Transaction_Value", "sum"),
        Analytical_Block=("Analytical_Block", "first"),
        Loyalty_Factor=("Loyalty_Factor", "first"),
        Average_Monthly_Spend=("Average_Monthly_Spend", "first"),
        Max_Client_Potential=("Max_Client_Potential", "first")
    ).sort_values(["Client_ID", "Product_Family", "Date"]).reset_index(drop=True)

    # Días entre compras
    agg["Days_Between"] = agg.groupby(["Client_ID", "Product_Family"])["Date"].diff().dt.days
    return agg

# ─────────────────────────────────────────────────────────────────────────────
# 3. MOTOR ESTADÍSTICO Y ALERTAS (LA LÓGICA CORE)
# ─────────────────────────────────────────────────────────────────────────────
def generate_alerts(agg: pd.DataFrame) -> pd.DataFrame:
    # 1. Calcular Estadísticas (Media y Desviación)
    pair_stats = agg.groupby(["Client_ID", "Product_Family"]).agg(
        Purchase_Count=("Quantity", "count"),
        Mean_Qty=("Quantity", "mean"), Std_Qty=("Quantity", "std"),
        Mean_Days=("Days_Between", "mean"), Std_Days=("Days_Between", "std"),
        Avg_Txn_Value=("Transaction_Value", "mean")
    ).reset_index()

    global_stats = agg.groupby("Product_Family").agg(
        G_Mean_Qty=("Quantity", "mean"), G_Std_Qty=("Quantity", "std"),
        G_Mean_Days=("Days_Between", "mean"), G_Std_Days=("Days_Between", "std")
    ).reset_index()

    # Cold Start Fallback (<3 compras usan la media global de la familia)
    stats = pair_stats.merge(global_stats, on="Product_Family", how="left")
    cold = stats["Purchase_Count"] < 3
    stats.loc[cold, "Std_Qty"] = stats.loc[cold, "G_Std_Qty"]
    stats.loc[cold, "Std_Days"] = stats.loc[cold, "G_Std_Days"]
    stats.loc[cold, "Mean_Qty"] = stats.loc[cold, "G_Mean_Qty"]
    stats.loc[cold, "Mean_Days"] = stats.loc[cold, "G_Mean_Days"]
    stats.fillna(0, inplace=True)

    # 2. Evaluar Última Compra contra Estadísticas
    today = agg["Date"].max()
    last_purchase = agg.sort_values("Date").groupby(["Client_ID", "Product_Family"]).last().reset_index()
    last_purchase["Days_Since_Last"] = (today - last_purchase["Date"]).dt.days
    
    df_eval = last_purchase.merge(stats, on=["Client_ID", "Product_Family"], how="left")
    alerts = []

    for _, row in df_eval.iterrows():
        if row["Mean_Days"] <= 0: continue # Ignorar sin histórico

        block, loyal = row["Analytical_Block"], row["Loyalty_Factor"]
        dsl, mean_days, std_days = row["Days_Since_Last"], row["Mean_Days"], row["Std_Days"]
        last_qty, mean_qty, std_qty = row["Quantity"], row["Mean_Qty"], row["Std_Qty"]
        avg_spend, max_pot = row["Average_Monthly_Spend"], row["Max_Client_Potential"]

        reason, opportunity, days_delayed = None, 0.0, 0.0

        # REGLA A: Commodities
        if block == "Commodities" and loyal == "Promiscuous":
            if dsl >= mean_days:
                reason = "Ventana de Captura"
                opportunity = max(0, max_pot - avg_spend)
                days_delayed = dsl - mean_days

        # REGLA B: Técnicos
        elif block == "Technical":
            expected_days = mean_days * (last_qty / mean_qty) if mean_qty > 0 else mean_days
            if dsl > expected_days + (1.5 * std_days):
                reason = "Retraso anómalo en tiempo"
            elif last_qty < mean_qty - (1.0 * std_qty):
                reason = "Caída drástica de volumen"
            
            if reason:
                opportunity = avg_spend
                days_delayed = max(0, dsl - expected_days)

        if reason:
            alerts.append({
                "Client_ID": row["Client_ID"], "Product_Family": row["Product_Family"], "Analytical_Block": block,
                "Motivo": reason, "Days_Since_Last": dsl, "Days_Delayed": days_delayed, "Mean_Days": mean_days,
                "Average_Transaction_Value": row["Avg_Txn_Value"], "Valor_Oportunidad (€)": round(opportunity, 2)
            })

    alerts_df = pd.DataFrame(alerts)
    
    # 3. Nivel de Riesgo (1-100)
    if not alerts_df.empty:
        raw_score = alerts_df["Average_Transaction_Value"] * (1 + (alerts_df["Days_Delayed"] / alerts_df["Mean_Days"].replace(0,1)))
        r_min, r_max = raw_score.min(), raw_score.max()
        alerts_df["Nivel de Riesgo"] = 50 if r_max == r_min else (1 + 99 * (raw_score - r_min) / (r_max - r_min)).round(0).astype(int)
        alerts_df = alerts_df.sort_values("Nivel de Riesgo", ascending=False)
        
    return alerts_df

# ─────────────────────────────────────────────────────────────────────────────
# 4. DASHBOARD UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h1>📡 Smart Demand Signals <span style='font-size:1rem;color:gray'>by Hackathon Team</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Sube database_clean.csv", type=["csv", "xlsx"])
    block_filter = st.selectbox("Bloque Analítico", ["Todos", "Commodities", "Technical"])
    min_risk = st.slider("Riesgo Mínimo", 1, 100, 1)

data_path = None
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        data_path = tmp.name
elif os.path.exists("database_clean.csv"):
    data_path = "database_clean.csv"

if not data_path:
    st.info("👆 Por favor, sube el archivo 'database_clean.csv' en la barra lateral para comenzar.")
    st.stop()

# Ejecutar el Pipeline
with st.spinner("Procesando lógicas estadísticas..."):
    try:
        raw_df = load_and_clean_data(data_path)
        agg_df = build_features(raw_df)
        alerts_df = generate_alerts(agg_df)
    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
        st.stop()

if alerts_df.empty:
    st.success("No hay alertas activas en este momento.")
    st.stop()

# Filtros
if block_filter != "Todos":
    alerts_df = alerts_df[alerts_df["Analytical_Block"] == block_filter]
alerts_df = alerts_df[alerts_df["Nivel de Riesgo"] >= min_risk]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(alerts_df)}</div><div class="kpi-label">Alertas Totales</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><div class="kpi-value">{alerts_df["Client_ID"].nunique()}</div><div class="kpi-label">Clínicas en Riesgo</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(alerts_df[alerts_df["Nivel de Riesgo"]>=70])}</div><div class="kpi-label">Riesgo Alto (>70)</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><div class="kpi-value">€{alerts_df["Valor_Oportunidad (€)"].sum():,.0f}</div><div class="kpi-label">Oportunidad Económica</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabla Interactiva
st.markdown('<div class="section-header">🚨 Panel de Alertas Comerciales</div>', unsafe_allow_html=True)
display_df = alerts_df[["Client_ID", "Product_Family", "Analytical_Block", "Motivo", "Nivel de Riesgo", "Days_Since_Last", "Valor_Oportunidad (€)"]].copy()
display_df["Acción Comercial (Feedback)"] = ""

edited_df = st.data_editor(
    display_df,
    use_container_width=True, hide_index=True,
    column_config={
        "Nivel de Riesgo": st.column_config.ProgressColumn("Nivel de Riesgo", min_value=0, max_value=100, format="%d"),
        "Valor_Oportunidad (€)": st.column_config.NumberColumn("Valor (€)", format="€%.2f"),
        "Acción Comercial (Feedback)": st.column_config.SelectboxColumn("Registrar Acción", options=["", "✅ Venta Recuperada", "❌ Falso Positivo", "⏳ Pendiente"])
    }
)

with st.expander("📚 Metodología (100% Explicable)"):
    st.markdown("""
    **Motor basado en Pandas (Sin Cajas Negras):**
    - **Commodities:** Si un cliente 'Promiscuo' supera su media histórica de días entre compras, salta alerta de captura (probablemente ha comprado a la competencia).
    - **Técnicos:** Calculamos el tiempo de compra esperado ajustado al volumen. Si el retraso supera 1.5 Desviaciones Estándar, o la cantidad baja de 1 Desviación Estándar, salta alerta de fuga.
    - **Priorización:** Se cruza matemáticamente la urgencia de días con el valor medio del cliente para dar un score del 1 al 100.
    """)