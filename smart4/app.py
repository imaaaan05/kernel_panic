# =============================================================================
#  Smart Demand Signals — app.py (Streamlit Frontend)
#  Author : Equipo Inibsa
#  Purpose: Corporate-grade UI — communicates with FastAPI backend only.
#           Zero Pandas / statistical logic in this file.
# =============================================================================

import streamlit as st
import requests
from datetime import datetime
from visual_components import render_visual_dashboard

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Smart Demand Signals · Inibsa",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — modern corporate design
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & fonts ─────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Page background ─────────────────────────────────────────────────── */
.stApp {
    background: #f0f4f9;
}

/* ── Sidebar ─────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2e 0%, #12263f 100%);
    border-right: 1px solid #1e3a5f;
}
section[data-testid="stSidebar"] * {
    color: #c9d8ea !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #e8f0fb !important;
    font-weight: 700;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    color: #c9d8ea !important;
    border-radius: 8px;
    font-weight: 500;
    transition: background 0.2s;
    width: 100%;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12);
    border-color: rgba(255,255,255,0.22);
}

/* ── Page header ─────────────────────────────────────────────────────── */
.page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 28px 32px 20px;
    background: linear-gradient(135deg, #0a1628 0%, #0d3264 50%, #0f4299 100%);
    border-radius: 16px;
    margin-bottom: 28px;
    box-shadow: 0 4px 24px rgba(13,50,100,0.25);
}
.page-header-icon {
    font-size: 2.6rem;
    line-height: 1;
}
.page-header-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1.15;
}
.page-header-sub {
    font-size: 0.82rem;
    color: #7eb3e8;
    font-weight: 400;
    margin-top: 3px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* ── KPI cards ───────────────────────────────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 28px;
}
.kpi-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 22px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.05);
    border-top: 4px solid transparent;
    transition: transform 0.18s, box-shadow 0.18s;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 24px rgba(0,0,0,0.11);
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--accent, #0d6efd);
    border-radius: 14px 14px 0 0;
}
.kpi-card.blue   { --accent: #0d6efd; }
.kpi-card.indigo { --accent: #6366f1; }
.kpi-card.red    { --accent: #ef4444; }
.kpi-card.teal   { --accent: #0d9488; }

.kpi-icon {
    font-size: 1.4rem;
    margin-bottom: 8px;
    display: block;
}
.kpi-value {
    font-size: 2.1rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1;
    letter-spacing: -0.03em;
}
.kpi-label {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}

/* ── Section header ──────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    border-left: 4px solid #0d6efd;
    padding-left: 14px;
    margin: 24px 0 14px;
    letter-spacing: -0.01em;
}
.section-badge {
    font-size: 0.7rem;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
    border-radius: 20px;
    padding: 2px 10px;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── Info / warning banners ──────────────────────────────────────────── */
.banner {
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.88rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
}
.banner.info    { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
.banner.success { background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; }
.banner.error   { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

/* ── Spinner overlay tweak ───────────────────────────────────────────── */
.stSpinner > div { border-top-color: #0d6efd !important; }

/* ── Data editor container ───────────────────────────────────────────── */
[data-testid="stDataEditor"] {
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

/* ── Expander ────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    font-weight: 600;
    font-size: 0.88rem;
    color: #334155;
}

/* ── Divider ─────────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.08) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-header-icon">📡</div>
  <div>
    <div class="page-header-title">Smart Demand Signals</div>
    <div class="page-header-sub">Motor estadístico predictivo · Inibsa Hackathon</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")

    uploaded_file = st.file_uploader(
        "📂 Sube database_clean.csv",
        type=["csv", "xlsx"],
        help="Archivo con los datos transaccionales de clientes.",
    )

    st.markdown("---")
    sim_date = st.date_input(
        "📅 Simular fecha actual",
        value=datetime(2025, 12, 31),
        help="La fecha desde la que se evalúa el scoring.",
    )

    block_filter = st.selectbox(
        "🔬 Bloque Analítico",
        ["Todos", "Commodities", "Technical"],
    )

    min_risk = st.slider(
        "🎚️ Riesgo Mínimo (Filtro de Ruido)",
        min_value=0,
        max_value=100,
        value=20,
        help="Oculta alertas con score por debajo de este umbral.",
    )

    st.markdown("---")
    mostrar_gestionadas = st.checkbox(
        "👁️ Ver alertas gestionadas (Historial)",
        value=False,
    )

    st.markdown("")
    if st.button("🗑️ Limpiar Feedback"):
        try:
            r = requests.post(f"{BACKEND_URL}/clear_feedback", timeout=10)
            r.raise_for_status()
            st.success("Memoria limpiada.", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(f"Error al limpiar: {e}")

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.72rem;color:#4a6a8a;text-align:center;padding-top:4px;'>"
        "Backend: <code style='background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;'>"
        f"{BACKEND_URL}</code></div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# MAIN LOGIC: nothing happens until a file is uploaded
# ─────────────────────────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("""
    <div class="banner info">
      <span style="font-size:1.3rem">👆</span>
      <span>Sube el archivo <strong>database_clean.csv</strong> en la barra lateral para activar el motor estadístico.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CALL BACKEND /upload
# ─────────────────────────────────────────────────────────────────────────────
with st.spinner("⚙️ Ejecutando motor estadístico…"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/upload",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
            data={"sim_date": sim_date.strftime("%Y-%m-%d")},
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.exceptions.ConnectionError:
        st.markdown("""
        <div class="banner error">
          <span style="font-size:1.3rem">🔌</span>
          <span>No se pudo conectar con el backend FastAPI. Asegúrate de que está corriendo en
          <strong>http://localhost:8000</strong>.<br>
          Ejecuta: <code>uvicorn main:app --reload --port 8000</code></span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        st.markdown(f"""
        <div class="banner error">
          <span style="font-size:1.3rem">❌</span>
          <span>Error del backend: <strong>{e}</strong></span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

alerts_raw = payload.get("alerts", [])
meta = payload.get("meta", {})

# ─────────────────────────────────────────────────────────────────────────────
# CLIENT-SIDE FILTERING (block filter + history toggle — no Pandas logic)
# ─────────────────────────────────────────────────────────────────────────────
# We get alerts pre-filtered at >=20 from the backend.
# Additional UI filters are applied here purely for display.
if not alerts_raw:
    st.markdown("""
    <div class="banner success">
      <span style="font-size:1.3rem">🎉</span>
      <span>Sin alertas accionables en este periodo. ¡Todo en orden!</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

import pandas as pd  # Only for display-layer DataFrame construction — no statistical logic

alerts_df = pd.DataFrame(alerts_raw)

if block_filter != "Todos":
    alerts_df = alerts_df[alerts_df["Analytical_Block"] == block_filter]

# History toggle: get feedback keys from session state (mirrored from backend responses)
if "feedback_keys" not in st.session_state:
    st.session_state.feedback_keys = {}

if mostrar_gestionadas:
    mask = alerts_df.apply(
        lambda r: (r["Client_ID"], r["Product_Family"]) in st.session_state.feedback_keys, axis=1
    )
    alerts_df = alerts_df[(alerts_df["Nivel de Riesgo"] >= min_risk) | mask]
else:
    alerts_df = alerts_df[alerts_df["Nivel de Riesgo"] >= min_risk]

if alerts_df.empty:
    st.markdown("""
    <div class="banner info">
      <span style="font-size:1.3rem">🔎</span>
      <span>No hay alertas para los filtros seleccionados. Ajusta el umbral de riesgo o el bloque analítico.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
total_alerts  = len(alerts_df)
total_clients = alerts_df["Client_ID"].nunique()
critical      = int((alerts_df["Nivel de Riesgo"] >= 70).sum())
date_label    = sim_date.strftime("%d/%m/%Y")

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card blue">
    <span class="kpi-icon">🚨</span>
    <div class="kpi-value">{total_alerts}</div>
    <div class="kpi-label">Alertas Accionables</div>
  </div>
  <div class="kpi-card indigo">
    <span class="kpi-icon">🏥</span>
    <div class="kpi-value">{total_clients}</div>
    <div class="kpi-label">Clínicas en Radar</div>
  </div>
  <div class="kpi-card red">
    <span class="kpi-icon">🔴</span>
    <div class="kpi-value">{critical}</div>
    <div class="kpi-label">Prioridad Crítica (&gt;70)</div>
  </div>
  <div class="kpi-card teal">
    <span class="kpi-icon">📅</span>
    <div class="kpi-value">{date_label}</div>
    <div class="kpi-label">Fecha del Sistema</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INTERVENTION TABLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="section-header">
  🚨 Panel de Intervención Comercial
  <span class="section-badge">{total_alerts} ALERTAS</span>
</div>
""", unsafe_allow_html=True)

display_df = alerts_df[[
    "Nivel de Riesgo", "Tipo", "Client_ID", "Product_Family",
    "Motivo", "Days_Since_Last",
]].copy().rename(columns={"Days_Since_Last": "Días Últ. Compra"})

# Restore any previously recorded feedback for display
display_df["Acción Comercial"] = display_df.apply(
    lambda r: st.session_state.feedback_keys.get((r["Client_ID"], r["Product_Family"]), ""),
    axis=1,
)

edited_df = st.data_editor(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Nivel de Riesgo": st.column_config.ProgressColumn(
            "Score", min_value=0, max_value=100, format="%d"
        ),
        "Tipo": st.column_config.TextColumn("Categoría", width="small"),
        "Client_ID": st.column_config.TextColumn("Cliente", width="medium"),
        "Product_Family": st.column_config.TextColumn("Familia", width="medium"),
        "Motivo": st.column_config.TextColumn("Motivo de Alerta", width="large"),
        "Días Últ. Compra": st.column_config.NumberColumn("Días Últ. Compra", format="%d d"),
        "Acción Comercial": st.column_config.SelectboxColumn(
            "Feedback",
            options=["", "✅ Venta Recuperada", "❌ Falso Positivo"],
            width="medium",
        ),
    },
)

# ─────────────────────────────────────────────────────────────────────────────
# FEEDBACK CAPTURE: detect changes → POST /feedback → rerun
# ─────────────────────────────────────────────────────────────────────────────
changed = False
for _, row in edited_df.iterrows():
    new_action = row["Acción Comercial"]
    key = (row["Client_ID"], row["Product_Family"])
    prev_action = st.session_state.feedback_keys.get(key, "")

    if new_action != prev_action:
        try:
            r = requests.post(
                f"{BACKEND_URL}/feedback",
                json={
                    "Client_ID": row["Client_ID"],
                    "Product_Family": row["Product_Family"],
                    "Action": new_action,
                },
                timeout=10,
            )
            r.raise_for_status()
            # Mirror state locally so the toggle works while the file isn't re-uploaded
            if new_action == "":
                st.session_state.feedback_keys.pop(key, None)
            else:
                st.session_state.feedback_keys[key] = new_action
            changed = True
        except Exception as e:
            st.warning(f"No se pudo enviar feedback al backend: {e}")

if changed:
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# METHODOLOGY EXPANDER
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📚 Metodología del Motor Estadístico"):
    st.markdown("""
    **Motor de Decisión Inteligente — Lógica 100% Explicable**

    - **Filtro de Ruido:** Evaluamos únicamente transacciones de los últimos 24 meses (ventana móvil) e ignoramos alertas con score < 20.
    - **Señales detectadas:** Diferenciamos entre **Oportunidad** (ventana de captura frente a competencia) y **Riesgo** (retrasos anómalos ajustados al volumen comprado).
    - **Normalización Robusta:** Los scores se calculan cruzando el impacto económico histórico con la urgencia temporal, limitando outliers con *Cap P98* y aplicando escala logarítmica (*Log1p*) para que ninguna clínica pequeña quede invisible.
    - **Multiplicadores de Contexto:** Cada tipo de señal tiene un peso diferencial (`Fugado >1 año` ×1.5, `Ventana de Captura` ×1.2, `Caída de Volumen` ×1.1).
    - **Aprendizaje en Tiempo Real:** El comercial puede reportar un **Falso Positivo** (penalización ×0.1) o una **Venta Recuperada** (penalización ×0.5), recalibrando la prioridad de forma dinámica sin necesidad de reentrenar ningún modelo.
    """)

# ─────────────────────────────────────────────────────────────
# ADVANCED VISUAL ANALYTICS
# ─────────────────────────────────────────────────────────────
render_visual_dashboard(alerts_df)