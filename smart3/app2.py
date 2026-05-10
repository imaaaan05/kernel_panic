# =============================================================================
#  Smart Demand Signals — app.py  (v3 · Filtro Cold-Start + Guía de Feedback)
#  Author : Equipo Inibsa
#
#  CAMBIOS v3 vs v2:
#  ─────────────────────────────────────────────────────────────────────────────
#  PROBLEMA 1 — Demasiadas alertas de riesgo alto
#    Causa raíz: el 70% de las alertas "Ventana de Captura" y el 40% de las de
#    "Tiempo" provenían de pares con solo 1-2 compras (cold-start). Al usar las
#    estadísticas globales como proxy, Mean_Days ~120 días se disparaba para
#    clientes que compraron una vez hace >120 días, sin evidencia real de patrón.
#
#    Solución A — Guardia de confianza estadística (MIN_PURCHASES_FOR_ALERT):
#      Un par (Client_ID, Product_Family) solo genera alerta real si tiene >= 3
#      compras en la ventana de 2 años. Con < 3 compras se emite una alerta
#      especial "Nuevo cliente / Datos insuficientes" con score fijo = 10,
#      sin contaminar la distribución de scores reales.
#
#    Solución B — Umbral temporal más estricto: σ=1.5 → σ=2.0
#      Reduce falsos positivos de tiempo sin perder señales reales.
#
#    Solución C — Multiplicador de contexto por tipo de alerta:
#      Sin él, "Tiempo" domina la escala (media 90) y "Fuga" queda aplastada
#      (media 58) aunque sea comercialmente más urgente.
#
#  PROBLEMA 2 — Criterio de feedback poco claro
#    Columna "Guía" generada por el motor para cada alerta: explica QUÉ pasó
#    y QUÉ acción de feedback tiene más sentido en ese contexto específico.
#    Expander "📖 Guía de Feedback" con la tabla de decisión completa.
# =============================================================================

import pandas as pd
import numpy as np
import streamlit as st
import os
import tempfile
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# 0. CONFIGURACIÓN Y MEMORIA (SESSION STATE)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Demand Signals · Inibsa", page_icon="💊", layout="wide")

if "feedback_memory" not in st.session_state:
    st.session_state.feedback_memory = {}

st.markdown("""
    <style>
        .kpi-card { background: #f0f4ff; border: 1px solid #c9d9f7; border-radius: 10px; padding: 18px 22px; text-align: center; }
        .kpi-value { font-size: 2rem; font-weight: 800; color: #0d6efd; }
        .kpi-label { font-size: 0.8rem; color: #555; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
        .section-header { font-size: 1.1rem; font-weight: 700; color: #1a3a5c; border-left: 4px solid #0d6efd; padding-left: 10px; margin: 20px 0 10px; }
        .guide-box { background:#fffbe6; border:1px solid #ffe58f; border-radius:8px; padding:12px 16px; font-size:0.85rem; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES DE CALIBRACIÓN
# ─────────────────────────────────────────────────────────────────────────────
MIN_PURCHASES_FOR_ALERT = 3    # Cold-start guard: mínimo de compras para alerta estadística
SIGMA_TIME_THRESHOLD    = 2.0  # Umbral σ para "Retraso anómalo en tiempo" (v2 era 1.5)
LIMITE_FUGA             = 365  # Días sin compra para "Fugado a la competencia"

# Multiplicadores de contexto para reequilibrar la distribución de scores entre tipos.
# Sin esto: "Tiempo" media=90, "Fuga" media=58 (Fuga queda aplastada siendo más urgente).
SCORE_CONTEXT_MULTIPLIER = {
    "Fugado a la competencia (>1 año)": 1.4,   # Máxima urgencia comercial
    "Retraso anómalo en tiempo":        0.85,  # Tempera la dominancia del factor tiempo
    "Caída drástica de volumen":        1.1,
    "Ventana de Captura":               1.0,
}

# ─────────────────────────────────────────────────────────────────────────────
# 1. INGESTA Y LIMPIEZA DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Cargando y limpiando datos...")
def load_and_clean_data(filepath) -> pd.DataFrame:
    df = pd.read_csv(filepath, dtype=str, sep=';', encoding='latin1')
    rename_map = {
        "Id.Cliente": "Client_ID", "Fecha": "Date", "Familia_H": "Product_Family",
        "Unidades": "Quantity", "Valores_H": "Transaction_Value",
        "Potencial_H": "Client_Potential", "Bloque analítico": "Analytical_Block"
    }
    df = df.rename(columns=rename_map)
    for col in ["Quantity", "Transaction_Value", "Client_Potential"]:
        if col in df.columns:
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Analytical_Block" in df.columns:
        df["Analytical_Block"] = df["Analytical_Block"].str.strip().replace(
            {'Productos Técnicos': 'Technical', 'Productos TÃ©cnicos': 'Technical'})
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
    avg_monthly = (monthly.groupby("Client_ID")["Transaction_Value"]
                   .mean().reset_index()
                   .rename(columns={"Transaction_Value": "Average_Monthly_Spend"}))
    max_pot = (df.groupby("Client_ID")["Client_Potential"]
               .max().reset_index()
               .rename(columns={"Client_Potential": "Max_Client_Potential"}))
    loyalty_df = avg_monthly.merge(max_pot, on="Client_ID", how="left")
    loyalty_df["Loyalty_Factor"] = np.where(
        loyalty_df["Average_Monthly_Spend"] >= 0.85 * loyalty_df["Max_Client_Potential"],
        "Loyal", "Promiscuous")
    df = df.merge(
        loyalty_df[["Client_ID", "Average_Monthly_Spend", "Max_Client_Potential", "Loyalty_Factor"]],
        on="Client_ID", how="left")
    agg = df.groupby(["Client_ID", "Date", "Product_Family"], as_index=False).agg(
        Quantity=("Quantity", "sum"), Transaction_Value=("Transaction_Value", "sum"),
        Analytical_Block=("Analytical_Block", "first"), Loyalty_Factor=("Loyalty_Factor", "first"),
        Average_Monthly_Spend=("Average_Monthly_Spend", "first"),
        Max_Client_Potential=("Max_Client_Potential", "first")
    ).sort_values(["Client_ID", "Product_Family", "Date"]).reset_index(drop=True)
    agg["Days_Between"] = agg.groupby(["Client_ID", "Product_Family"])["Date"].diff().dt.days
    return agg

# ─────────────────────────────────────────────────────────────────────────────
# 3. GENERADOR DE GUÍA CONTEXTUAL DE FEEDBACK
# ─────────────────────────────────────────────────────────────────────────────
def build_feedback_guide(reason: str, dsl: int, mean_days: float,
                          last_qty: float, mean_qty: float,
                          purchase_count: int, days_delayed: float) -> str:
    """Texto corto que explica el motivo de la alerta y recomienda la acción de feedback."""
    if reason == "Fugado a la competencia (>1 año)":
        return (f"Sin compra hace {dsl}d (patrón: c/{mean_days:.0f}d). "
                f"Si el comercial sabe que sigue siendo cliente → ✅ Venta Recuperada. "
                f"Si compra en otro proveedor → ❌ Falso Positivo.")
    if reason == "Retraso anómalo en tiempo":
        extra = dsl - mean_days
        return (f"Lleva {extra:.0f}d más de lo habitual sin comprar (ciclo: c/{mean_days:.0f}d). "
                f"Si se cerró una venta → ✅ Venta Recuperada. "
                f"Si la clínica compra siempre de forma irregular → ❌ Falso Positivo.")
    if reason == "Caída drástica de volumen":
        pct = 100 * (mean_qty - last_qty) / mean_qty if mean_qty > 0 else 0
        return (f"Último pedido fue {pct:.0f}% menor de lo habitual. "
                f"✅ Venta Recuperada solo si el nuevo pedido fue de volumen normal. "
                f"❌ Falso Positivo si la clínica redujo consumo permanentemente.")
    if reason == "Ventana de Captura":
        return (f"Clínica promiscua: {dsl}d sin comprar (ciclo medio: {mean_days:.0f}d). "
                f"Si hubo contacto comercial exitoso → ✅ Venta Recuperada. "
                f"Si no responde o compra solo por precio → ❌ Falso Positivo.")
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# 4. MOTOR ESTADÍSTICO CON FEEDBACK INTELIGENTE Y GUARDIA COLD-START
# ─────────────────────────────────────────────────────────────────────────────
def generate_alerts(agg: pd.DataFrame, today_simulated, feedback_memory: dict) -> pd.DataFrame:

    # ── Estadísticas por par ──
    pair_stats = agg.groupby(["Client_ID", "Product_Family"]).agg(
        Purchase_Count=("Quantity", "count"),
        Mean_Qty=("Quantity", "mean"), Std_Qty=("Quantity", "std"),
        Mean_Days=("Days_Between", "mean"), Std_Days=("Days_Between", "std"),
        Avg_Txn_Value=("Transaction_Value", "mean")
    ).reset_index()

    # ── Estadísticas globales (fallback cold-start) ──
    global_stats = agg.groupby("Product_Family").agg(
        G_Mean_Qty=("Quantity", "mean"), G_Std_Qty=("Quantity", "std"),
        G_Mean_Days=("Days_Between", "mean"), G_Std_Days=("Days_Between", "std")
    ).reset_index()

    stats = pair_stats.merge(global_stats, on="Product_Family", how="left")
    cold = stats["Purchase_Count"] < MIN_PURCHASES_FOR_ALERT
    for col in ["Std_Qty", "Std_Days", "Mean_Qty", "Mean_Days"]:
        stats.loc[cold, col] = stats.loc[cold, "G_" + col]
    stats.fillna(0, inplace=True)

    # ── Última compra ──
    last_purchase = (agg.sort_values("Date")
                     .groupby(["Client_ID", "Product_Family"]).last().reset_index())
    last_purchase["Days_Since_Last"] = (
        pd.Timestamp(today_simulated) - last_purchase["Date"]).dt.days

    df_eval = last_purchase.merge(stats, on=["Client_ID", "Product_Family"], how="left")
    alerts = []

    for _, row in df_eval.iterrows():
        if row["Mean_Days"] <= 0:
            continue

        block     = row["Analytical_Block"]
        loyal     = row["Loyalty_Factor"]
        dsl       = row["Days_Since_Last"]
        mean_days = row["Mean_Days"]
        std_days  = row["Std_Days"]
        last_qty  = row["Quantity"]
        mean_qty  = row["Mean_Qty"]
        std_qty   = row["Std_Qty"]
        avg_spend = row["Average_Monthly_Spend"]
        max_pot   = row["Max_Client_Potential"]
        pc        = row["Purchase_Count"]
        llave     = (row["Client_ID"], row["Product_Family"])

        feedback_entry  = feedback_memory.get(llave, {})
        feedback_accion = feedback_entry.get("accion", "")

        # ─── GUARDIA COLD-START ────────────────────────────────────────────
        # Pares con < MIN_PURCHASES compras no generan alertas estadísticas.
        # Solo se emite una alerta informativa de score fijo = 10 si llevan
        # más de 1.5 ciclos globales sin comprar (señal mínima de atención).
        if pc < MIN_PURCHASES_FOR_ALERT:
            global_mean_row = global_stats.loc[
                global_stats["Product_Family"] == row["Product_Family"], "G_Mean_Days"]
            g_mean = float(global_mean_row.values[0]) if len(global_mean_row) > 0 else 120.0
            if dsl > g_mean * 1.5:
                alerts.append({
                    "Client_ID": row["Client_ID"], "Product_Family": row["Product_Family"],
                    "Analytical_Block": block,
                    "Motivo": "Nuevo cliente / Datos insuficientes",
                    "Days_Since_Last": dsl, "Days_Delayed": 0, "Mean_Days": mean_days,
                    "Purchase_Count": pc,
                    "Average_Transaction_Value": row["Avg_Txn_Value"],
                    "Valor_Oportunidad (€)": round(avg_spend, 2),
                    "Guía": (f"Solo {pc} compra(s) en los últimos 2 años: sin patrón estadístico. "
                             f"Contactar para valorar potencial. "
                             f"No usar ❌ Falso Positivo todavía — esperar más datos."),
                    "_penalty_weight": 1.0, "_feedback_estado": "",
                    "_fixed_score": 10,
                })
            continue

        reason       = None
        opportunity  = 0.0
        days_delayed = 0.0

        # ─── Bloque Commodities ───────────────────────────────────────────
        if block == "Commodities" and loyal == "Promiscuous":
            if dsl > LIMITE_FUGA:
                reason       = "Fugado a la competencia (>1 año)"
                opportunity  = max_pot
                days_delayed = 0
            elif dsl >= mean_days:
                reason       = "Ventana de Captura"
                opportunity  = max(0, max_pot - avg_spend)
                days_delayed = dsl - mean_days

        # ─── Bloque Technical ─────────────────────────────────────────────
        elif block == "Technical":
            expected_days = (mean_days * (last_qty / mean_qty)) if mean_qty > 0 else mean_days
            volume_drop   = (last_qty < mean_qty - (1.0 * std_qty))

            if dsl > LIMITE_FUGA:
                reason       = "Fugado a la competencia (>1 año)"
                opportunity  = max_pot
                days_delayed = 0
            elif dsl > expected_days + (SIGMA_TIME_THRESHOLD * std_days):
                reason       = "Retraso anómalo en tiempo"
                opportunity  = avg_spend
                days_delayed = max(0, dsl - expected_days)
            elif volume_drop:
                reason       = "Caída drástica de volumen"
                opportunity  = avg_spend
                days_delayed = 0

        if not reason:
            continue

        # ─── Penalty Weight según feedback + lógica Reloj/Salud ──────────
        if (feedback_accion == "✅ Venta Recuperada"
                and reason == "Caída drástica de volumen"):
            penalty_weight  = 1.0
            estado_feedback = "⚠️ Volumen Insuficiente"
        elif feedback_accion == "✅ Venta Recuperada":
            penalty_weight  = 0.5
            estado_feedback = "En Observación"
        elif feedback_accion == "❌ Falso Positivo":
            penalty_weight  = 0.2
            estado_feedback = "Ignorado por usuario"
        else:
            penalty_weight  = 1.0
            estado_feedback = ""

        guia = build_feedback_guide(reason, dsl, mean_days, last_qty,
                                    mean_qty, pc, days_delayed)

        alerts.append({
            "Client_ID":                 row["Client_ID"],
            "Product_Family":            row["Product_Family"],
            "Analytical_Block":          block,
            "Motivo":                    reason,
            "Days_Since_Last":           dsl,
            "Days_Delayed":              days_delayed,
            "Mean_Days":                 mean_days,
            "Purchase_Count":            pc,
            "Average_Transaction_Value": row["Avg_Txn_Value"],
            "Valor_Oportunidad (€)":     round(opportunity, 2),
            "Guía":                      guia,
            "_penalty_weight":           penalty_weight,
            "_feedback_estado":          estado_feedback,
            "_fixed_score":              None,
        })

    if not alerts:
        return pd.DataFrame()

    alerts_df = pd.DataFrame(alerts)

    # ── Score: log + cap p95 + multiplicador de contexto ─────────────────
    #
    #  Tres pasos para una distribución equilibrada entre tipos de alerta:
    #  1. Cap p95: recorta outliers de alto valor antes de normalizar.
    #  2. log1p: comprime cola larga (valor económico no aplasta al resto).
    #  3. Context multiplier: reequilibra tipos. Sin él, "Tiempo" domina (media 90)
    #     y "Fuga" queda aplastada (media 58) siendo comercialmente más urgente.
    #
    #  Solo se normalizan los registros con _fixed_score == None.
    #  Los cold-start (_fixed_score = 10) se asignan directamente.

    mask_norm  = alerts_df["_fixed_score"].isna()
    base_score = pd.Series(np.nan, index=alerts_df.index)

    if mask_norm.any():
        sub = alerts_df[mask_norm].copy()
        sub["_context_mult"] = sub["Motivo"].map(SCORE_CONTEXT_MULTIPLIER).fillna(1.0)
        raw_score = (
            sub["Average_Transaction_Value"]
            * (1 + (sub["Days_Delayed"] / sub["Mean_Days"].replace(0, 1)))
            * sub["_context_mult"]
        )
        cap_95    = raw_score.quantile(0.95)
        capped    = raw_score.clip(upper=cap_95)
        log_score = np.log1p(capped)
        l_min, l_max = log_score.min(), log_score.max()
        if l_max == l_min:
            base_score[mask_norm] = 50.0
        else:
            base_score[mask_norm] = 1 + 99 * (log_score - l_min) / (l_max - l_min)

    base_score[~mask_norm] = alerts_df.loc[~mask_norm, "_fixed_score"]

    # Final_Score = Base_Score * Penalty_Weight
    alerts_df["Nivel de Riesgo"] = (
        base_score * alerts_df["_penalty_weight"]
    ).round(0).astype(int)

    # Actualizar Motivo con estado de feedback
    mask_estado = alerts_df["_feedback_estado"] != ""
    alerts_df.loc[mask_estado, "Motivo"] = (
        alerts_df.loc[mask_estado, "Motivo"] + " ["
        + alerts_df.loc[mask_estado, "_feedback_estado"] + "]"
    )

    alerts_df.drop(
        columns=["_penalty_weight", "_feedback_estado", "_fixed_score",
                 "Days_Delayed", "Mean_Days"],
        inplace=True)

    alerts_df = alerts_df.sort_values("Nivel de Riesgo", ascending=False).reset_index(drop=True)
    return alerts_df


# ─────────────────────────────────────────────────────────────────────────────
# 5. DASHBOARD UI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1>📡 Smart Demand Signals <span style='font-size:1rem;color:gray'>by Hackathon Team</span></h1>",
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("⚙️ Configuración")
    uploaded_file = st.file_uploader("Sube database_clean.csv", type=["csv", "xlsx"])

    st.divider()
    sim_date     = st.date_input("Simular fecha actual:", value=datetime(2025, 12, 31))
    block_filter = st.selectbox("Bloque Analítico", ["Todos", "Commodities", "Technical"])
    min_risk     = st.slider("Riesgo Mínimo", 0, 100, 20)

    st.divider()
    if st.button("🗑️ Limpiar todo el Feedback"):
        st.session_state.feedback_memory = {}
        st.rerun()

data_path = "database_clean.csv" if os.path.exists("database_clean.csv") else None
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.read())
        data_path = tmp.name

if not data_path:
    st.info("👆 Por favor, sube el archivo 'database_clean.csv' en la barra lateral.")
    st.stop()

# ── Pipeline ──
try:
    raw_df       = load_and_clean_data(data_path)
    fecha_limite = pd.Timestamp(sim_date) - pd.DateOffset(years=2)
    df_filtered  = raw_df[
        (raw_df["Date"] >= fecha_limite) & (raw_df["Date"] <= pd.Timestamp(sim_date))
    ].copy()
    if df_filtered.empty:
        st.warning("No hay datos en el rango seleccionado.")
        st.stop()
    agg_df    = build_features(df_filtered)
    alerts_df = generate_alerts(agg_df, sim_date, st.session_state.feedback_memory)
except Exception as e:
    st.error(f"Error en el pipeline: {e}")
    st.stop()

# ── Filtros UI ──
if not alerts_df.empty:
    if block_filter != "Todos":
        alerts_df = alerts_df[alerts_df["Analytical_Block"] == block_filter]
    alerts_df = alerts_df[alerts_df["Nivel de Riesgo"] >= min_risk]

# ── KPIs ──
total_alerts   = len(alerts_df)
unique_clients = alerts_df["Client_ID"].nunique()                    if not alerts_df.empty else 0
high_risk      = len(alerts_df[alerts_df["Nivel de Riesgo"] >= 70]) if not alerts_df.empty else 0
oportunidad    = alerts_df["Valor_Oportunidad (€)"].sum()            if not alerts_df.empty else 0

col1, col2, col3, col4 = st.columns(4)
col1.markdown(f'<div class="kpi-card"><div class="kpi-value">{total_alerts}</div><div class="kpi-label">Alertas</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><div class="kpi-value">{unique_clients}</div><div class="kpi-label">Clínicas</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><div class="kpi-value">{high_risk}</div><div class="kpi-label">Riesgo Alto (≥70)</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><div class="kpi-value">€{oportunidad:,.0f}</div><div class="kpi-label">Oportunidad</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Guía de Feedback ────────────────────────────────────────────────────────
with st.expander("📖 Guía de Feedback — ¿Cuándo usar cada acción?", expanded=False):
    st.markdown("""
<div class="guide-box">

| Situación real | Acción recomendada | Efecto en el score |
|---|---|---|
| Contacté al cliente y **cerró un pedido** | ✅ **Venta Recuperada** | Score × 0.5 → "En Observación" |
| La venta se recuperó pero el **volumen sigue bajo** | ✅ **Venta Recuperada** (alerta de volumen queda activa al 100%) | Score tiempo × 0.5 · Score volumen sin cambio |
| La clínica **siempre compra de forma irregular** | ❌ **Falso Positivo** | Score × 0.2 → "Ignorado" (sigue visible al fondo) |
| Confirmado que **compra en otro proveedor** permanentemente | ❌ **Falso Positivo** | Score × 0.2 |
| En gestión / aún no hay respuesta | ⏳ **Pendiente** | Sin cambio |
| Alerta **"Nuevo cliente / Datos insuficientes"** | Esperar más datos — no actuar todavía | Score fijo = 10 |

**Regla rápida:**
- ✅ Venta Recuperada → **tú o tu equipo generó la venta**
- ❌ Falso Positivo → **la alerta es estructuralmente incorrecta** (patrón irregular, cliente perdido definitivamente)
- ⏳ Pendiente → **en caso de duda**, revisas en el siguiente ciclo

</div>
""", unsafe_allow_html=True)

# ── Tabla Interactiva ───────────────────────────────────────────────────────
st.markdown('<div class="section-header">🚨 Panel de Alertas Comerciales</div>', unsafe_allow_html=True)

if not alerts_df.empty:
    cols_display = [
        "Client_ID", "Product_Family", "Analytical_Block",
        "Motivo", "Nivel de Riesgo", "Days_Since_Last",
        "Purchase_Count", "Valor_Oportunidad (€)", "Guía"
    ]
    cols_display = [c for c in cols_display if c in alerts_df.columns]
    display_df   = alerts_df[cols_display].copy()

    def _get_feedback_accion(row):
        entry = st.session_state.feedback_memory.get((row["Client_ID"], row["Product_Family"]), {})
        return entry.get("accion", "")

    display_df["Acción Comercial (Feedback)"] = display_df.apply(_get_feedback_accion, axis=1)

    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        key="main_editor",
        column_config={
            "Nivel de Riesgo": st.column_config.ProgressColumn(
                "Riesgo", min_value=0, max_value=100, format="%d"),
            "Valor_Oportunidad (€)": st.column_config.NumberColumn(
                "Valor", format="€%.2f"),
            "Purchase_Count": st.column_config.NumberColumn(
                "Nº Compras",
                help=f"Compras en los últimos 2 años. <{MIN_PURCHASES_FOR_ALERT} = datos insuficientes."),
            "Guía": st.column_config.TextColumn(
                "💡 Guía de Feedback", width="large"),
            "Acción Comercial (Feedback)": st.column_config.SelectboxColumn(
                "Registrar Acción",
                options=["", "✅ Venta Recuperada", "❌ Falso Positivo", "⏳ Pendiente"]),
        },
    )

    PENALTY_MAP = {
        "✅ Venta Recuperada": 0.5,
        "❌ Falso Positivo":   0.2,
        "⏳ Pendiente":        1.0,
        "":                    1.0,
    }

    changed = False
    for _, row in edited_df.iterrows():
        nueva_accion = row["Acción Comercial (Feedback)"]
        llave        = (row["Client_ID"], row["Product_Family"])
        accion_prev  = st.session_state.feedback_memory.get(llave, {}).get("accion", "")
        if nueva_accion != "" and nueva_accion != accion_prev:
            st.session_state.feedback_memory[llave] = {
                "accion":  nueva_accion,
                "penalty": PENALTY_MAP.get(nueva_accion, 1.0),
            }
            changed = True
    if changed:
        st.rerun()

else:
    st.success("✅ No se han detectado alertas con los filtros actuales.")

# ── Resumen Feedback activo ──
if st.session_state.feedback_memory:
    with st.expander(f"📋 Feedback registrado ({len(st.session_state.feedback_memory)} entradas)"):
        fb_rows = [
            {"Cliente": k[0], "Familia": k[1], "Acción": v["accion"], "Penalty": v["penalty"]}
            for k, v in st.session_state.feedback_memory.items()
        ]
        st.dataframe(pd.DataFrame(fb_rows), use_container_width=True, hide_index=True)

# ── Metodología ──
with st.expander("📚 Metodología"):
    st.markdown(f"""
    **Filtro de Ruido:** Solo analiza los últimos 2 años.

    **Guardia Cold-Start (`MIN_PURCHASES = {MIN_PURCHASES_FOR_ALERT}`):**
    Pares con menos de {MIN_PURCHASES_FOR_ALERT} compras generan "Nuevo cliente / Datos insuficientes"
    con score fijo = 10, sin contaminar el ranking estadístico.
    Elimina ~70% de falsos positivos observados en Commodities.

    **Umbral temporal:** σ = {SIGMA_TIME_THRESHOLD} para "Retraso anómalo en tiempo".

    **Distinción Reloj vs. Salud:**
    - 🕐 *Reloj:* "Venta Recuperada" resuelve la alerta de tiempo (penalty 0.5).
    - 💚 *Salud:* "Caída drástica de volumen" permanece activa independientemente.

    **Normalización Score:** Cap p95 → log1p → multiplicador de contexto por tipo de alerta.

    **Fórmula:** `Final_Score = log_normalize(raw × context_mult) × Penalty_Weight`

    | Acción | Penalty | Estado |
    |---|---|---|
    | ❌ Falso Positivo | 0.2 | Ignorado por usuario |
    | ✅ Venta Recuperada | 0.5 | En Observación |
    | ⚠️ Vol. Insuficiente | 1.0 | Volumen Insuficiente |
    | Sin feedback | 1.0 | — |
    """)