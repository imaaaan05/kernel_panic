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
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN DE PÁGINA Y MEMORIA (SESSION STATE)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Demand Signals · Inibsa", page_icon="💊", layout="wide")

# Inicializar memoria para el feedback en tiempo real
if 'feedback_memory' not in st.session_state:
    st.session_state.feedback_memory = {}

st.markdown("""
    <style>
        .kpi-card { background: #f0f4ff; border: 1px solid #c9d9f7; border-radius: 10px; padding: 18px 22px; text-align: center; }
        .kpi-value { font-size: 2rem; font-weight: 800; color: #0d6efd; }
        .kpi-label { font-size: 0.8rem; color: #555; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
        .section-header { font-size: 1.1rem; font-weight: 700; color: #1a3a5c; border-left: 4px solid #0d6efd; padding-left: 10px; margin: 20px 0 10px; }
    </style>
""", unsafe_allow_html=True)

# Multiplicadores de contexto para la normalización
SCORE_CONTEXT_MULTIPLIER = {
    "Fugado a la competencia (>1 año)": 1.5,
    "Ventana de Captura": 1.2,
    "Retraso anómalo en tiempo": 1.0,
    "Caída drástica de volumen": 1.1
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. INGESTA Y LIMPIEZA DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando y limpiando datos...")
def load_and_clean_data(filepath) -> pd.DataFrame:
    df = pd.read_csv(filepath, dtype=str, sep=';', encoding='latin1')

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

    for col in ["Quantity", "Transaction_Value", "Client_Potential"]:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "Analytical_Block" in df.columns:
        df["Analytical_Block"] = df["Analytical_Block"].str.strip().replace({'Productos Técnicos': 'Technical', 'Productos TÃ©cnicos': 'Technical'})
    else:
        df["Analytical_Block"] = "Technical"

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
    df["YearMonth"] = df["Date"].dt.to_period("M")
    monthly = df.groupby(["Client_ID", "YearMonth"])["Transaction_Value"].sum().reset_index()
    avg_monthly = monthly.groupby("Client_ID")["Transaction_Value"].mean().reset_index().rename(columns={"Transaction_Value": "Average_Monthly_Spend"})
    max_pot = df.groupby("Client_ID")["Client_Potential"].max().reset_index().rename(columns={"Client_Potential": "Max_Client_Potential"})
    
    loyalty_df = avg_monthly.merge(max_pot, on="Client_ID", how="left")
    loyalty_df["Loyalty_Factor"] = np.where(loyalty_df["Average_Monthly_Spend"] >= 0.85 * loyalty_df["Max_Client_Potential"], "Loyal", "Promiscuous")
    
    df = df.merge(loyalty_df[["Client_ID", "Average_Monthly_Spend", "Max_Client_Potential", "Loyalty_Factor"]], on="Client_ID", how="left")

    agg = df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False).agg(
        Quantity=("Quantity", "sum"),
        Transaction_Value=("Transaction_Value", "sum"),
        Analytical_Block=("Analytical_Block", "first"),
        Loyalty_Factor=("Loyalty_Factor", "first")
    ).sort_values(["Client_ID", "Product_Family", "Date"]).reset_index(drop=True)

    agg["Days_Between"] = agg.groupby(["Client_ID", "Product_Family"])["Date"].diff().dt.days
    return agg

# ─────────────────────────────────────────────────────────────────────────────
# 3. MOTOR ESTADÍSTICO Y ALERTAS (LÓGICA CORE + NORMALIZACIÓN ROBUSTA)
# ─────────────────────────────────────────────────────────────────────────────
def generate_alerts(agg: pd.DataFrame, today_simulated) -> pd.DataFrame:
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

    stats = pair_stats.merge(global_stats, on="Product_Family", how="left")
    cold = stats["Purchase_Count"] < 3
    stats.loc[cold, "Std_Qty"] = stats.loc[cold, "G_Std_Qty"]
    stats.loc[cold, "Std_Days"] = stats.loc[cold, "G_Std_Days"]
    stats.loc[cold, "Mean_Qty"] = stats.loc[cold, "G_Mean_Qty"]
    stats.loc[cold, "Mean_Days"] = stats.loc[cold, "G_Mean_Days"]
    stats.fillna(0, inplace=True)

    last_purchase = agg.sort_values("Date").groupby(["Client_ID", "Product_Family"]).last().reset_index()
    # Usar la fecha simulada en lugar del max(Date) absoluto
    last_purchase["Days_Since_Last"] = (pd.Timestamp(today_simulated) - last_purchase["Date"]).dt.days
    
    df_eval = last_purchase.merge(stats, on=["Client_ID", "Product_Family"], how="left")
    alerts = []

    LIMITE_FUGA = 365

    for _, row in df_eval.iterrows():
        if row["Mean_Days"] <= 0: continue 

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
            # Clasificación simple: Riesgo vs Oportunidad
            tipo_alerta = "Oportunidad" if reason == "Ventana de Captura" else "Riesgo"

            alerts.append({
                "Client_ID": row["Client_ID"], "Product_Family": row["Product_Family"], 
                "Analytical_Block": block, "Tipo": tipo_alerta, "Motivo": reason, 
                "Days_Since_Last": dsl, "Days_Delayed": days_delayed, "Mean_Days": mean_days,
                "Average_Transaction_Value": row["Avg_Txn_Value"]
            })

    if not alerts: return pd.DataFrame()
    alerts_df = pd.DataFrame(alerts)
    
    # --- NORMALIZACIÓN ROBUSTA (Log + P98 Cap) ---
    alerts_df["_mult"] = alerts_df["Motivo"].map(SCORE_CONTEXT_MULTIPLIER).fillna(1.0)
    raw_score = (alerts_df["Average_Transaction_Value"] * (1 + (alerts_df["Days_Delayed"] / alerts_df["Mean_Days"].replace(0,1)))) * alerts_df["_mult"]
    
    cap_val = raw_score.quantile(0.98)
    raw_score = raw_score.clip(upper=cap_val)
    log_score = np.log1p(raw_score)
    
    l_min, l_max = log_score.min(), log_score.max()
    if l_max == l_min:
        alerts_df["Nivel de Riesgo"] = 50
    else:
        alerts_df["Nivel de Riesgo"] = (1 + 99 * (log_score - l_min) / (l_max - l_min + 1e-6)).round(0).astype(int)

    # --- APLICAR FEEDBACK MEMORY ---
    for idx, r in alerts_df.iterrows():
        key = (r["Client_ID"], r["Product_Family"])
        if key in st.session_state.feedback_memory:
            action = st.session_state.feedback_memory[key]
            if action == "❌ Falso Positivo": 
                alerts_df.at[idx, "Nivel de Riesgo"] = int(alerts_df.at[idx, "Nivel de Riesgo"] * 0.1)
            elif action == "✅ Venta Recuperada": 
                alerts_df.at[idx, "Nivel de Riesgo"] = int(alerts_df.at[idx, "Nivel de Riesgo"] * 0.5)

    alerts_df = alerts_df.sort_values("Nivel de Riesgo", ascending=False)
    return alerts_df

# ─────────────────────────────────────────────────────────────────────────────
# 4. DASHBOARD UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h1>📡 Smart Demand Signals <span style='font-size:1rem;color:gray'>by Hackathon Team</span></h1>", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Sube database_clean.csv", type=["csv", "xlsx"])
    
    st.divider()
    sim_date = st.date_input("Simular fecha actual:", value=datetime(2025, 12, 31))
    block_filter = st.selectbox("Bloque Analítico", ["Todos", "Commodities", "Technical"])
    
    # Filtro de ruido empieza en 20
    min_risk = st.slider("Riesgo Mínimo (Filtro Ruido)", 0, 100, 20)
    
    # ---> BOTÓN DE HISTORIAL <---
    mostrar_gestionadas = st.checkbox("👁️ Ver alertas gestionadas (Historial)", value=False)
    
    if st.button("🗑️ Limpiar Feedback"):
        st.session_state.feedback_memory = {}
        st.rerun()

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
        
        # Filtro Histórico: Eliminar ruido de hace más de 2 años
        fecha_limite = pd.Timestamp(sim_date) - pd.DateOffset(years=2)
        df_filtered = raw_df[(raw_df["Date"] >= fecha_limite) & (raw_df["Date"] <= pd.Timestamp(sim_date))].copy()
        
        if df_filtered.empty:
            st.warning("No hay datos en el rango seleccionado.")
            st.stop()
            
        agg_df = build_features(df_filtered)
        alerts_df = generate_alerts(agg_df, sim_date)
    except Exception as e:
        st.error(f"Error procesando los datos: {e}")
        st.stop()

if alerts_df.empty:
    st.success("No hay alertas activas en este momento.")
    st.stop()

# Filtros UI (Se aplican antes de contar los KPIs)
if block_filter != "Todos":
    alerts_df = alerts_df[alerts_df["Analytical_Block"] == block_filter]

# ---> LÓGICA DE FILTRADO CON HISTORIAL <---
if mostrar_gestionadas:
    # Si el historial está ON, mostramos las de riesgo ALTO + las que tengan feedback
    mask_feedback = alerts_df.apply(lambda r: (r["Client_ID"], r["Product_Family"]) in st.session_state.feedback_memory, axis=1)
    alerts_df = alerts_df[(alerts_df["Nivel de Riesgo"] >= min_risk) | mask_feedback]
else:
    # Si el historial está OFF, solo mostramos las de riesgo alto (las gestionadas se ocultan)
    alerts_df = alerts_df[alerts_df["Nivel de Riesgo"] >= min_risk]

# KPIs Modificados (Sin Oportunidad Económica)
col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(alerts_df)}</div><div class="kpi-label">Alertas Accionables</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><div class="kpi-value">{alerts_df["Client_ID"].nunique()}</div><div class="kpi-label">Clínicas en Radar</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(alerts_df[alerts_df["Nivel de Riesgo"]>=70])}</div><div class="kpi-label">Prioridad Crítica (>70)</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><div class="kpi-value">{sim_date.strftime("%d/%m/%Y")}</div><div class="kpi-label">Fecha del Sistema</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabla Interactiva
st.markdown('<div class="section-header">🚨 Panel de Intervención Comercial</div>', unsafe_allow_html=True)

# Selección limpia de columnas
display_df = alerts_df[["Nivel de Riesgo", "Tipo", "Client_ID", "Product_Family", "Motivo", "Days_Since_Last"]].copy()
display_df = display_df.rename(columns={"Days_Since_Last": "Días Últ. Compra"})

# ---> RECUPERAR EL FEEDBACK PARA MOSTRARLO EN PANTALLA <---
def get_accion_previa(cliente, familia):
    return st.session_state.feedback_memory.get((cliente, familia), "")

display_df["Acción Comercial"] = display_df.apply(lambda r: get_accion_previa(r["Client_ID"], r["Product_Family"]), axis=1)

edited_df = st.data_editor(
    display_df,
    use_container_width=True, hide_index=True,
    column_config={
        "Nivel de Riesgo": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
        "Tipo": st.column_config.TextColumn("Categoría"),
        "Acción Comercial": st.column_config.SelectboxColumn("Feedback", options=["", "✅ Venta Recuperada", "❌ Falso Positivo"])
    }
)

# ---> CAPTURAR FEEDBACK SIN BUCLES INFINITOS <---
cambios = False
for index, row in edited_df.iterrows():
    accion_nueva = row["Acción Comercial"]
    llave = (row["Client_ID"], row["Product_Family"])
    accion_previa = st.session_state.feedback_memory.get(llave, "")
    
    # Solo actualizamos si el usuario ha cambiado el desplegable
    if accion_nueva != accion_previa:
        if accion_nueva == "":
            del st.session_state.feedback_memory[llave] # Si lo borra, lo quitamos
        else:
            st.session_state.feedback_memory[llave] = accion_nueva # Guardamos nuevo
        cambios = True

if cambios:
    st.rerun()

with st.expander("📚 Metodología (100% Explicable)"):
    st.markdown("""
    **Motor de Decisión Inteligente:**
    - **Filtro de Ruido:** Evaluamos solo transacciones de los últimos 24 meses (ventana móvil) e ignoramos las alertas con score bajo (<20).
    - **Señales:** Diferenciamos entre **Oportunidad** (captura de ventas frente a la competencia) y **Riesgo** (retrasos anómalos ajustados al volumen).
    - **Priorización Robusta:** Los scores se calculan cruzando el impacto económico histórico con la urgencia temporal, limitando los valores atípicos (Cap P98) y usando escala logarítmica para que ninguna clínica pequeña quede invisible.
    - **Aprendizaje:** Si el comercial reporta un Falso Positivo o una Venta, el sistema recalibra dinámicamente la prioridad en tiempo real.
    """)