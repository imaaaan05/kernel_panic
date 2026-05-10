
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_visual_dashboard(alerts_df):

    # =====================================================
    # AUTO DETECT COLUMNS
    # =====================================================
    category_col = None
    family_col = None

    possible_category_cols = [
        "Categoria",
        "Categoría",
        "Category",
        "Tipo"
    ]

    possible_family_cols = [
        "Familia",
        "Family",
        "Product_Family"
    ]

    for col in possible_category_cols:
        if col in alerts_df.columns:
            category_col = col
            break

    for col in possible_family_cols:
        if col in alerts_df.columns:
            family_col = col
            break

    if category_col is None:
        st.error("Category column not found.")
        return

    if family_col is None:
        st.error("Family column not found.")
        return

    # =====================================================
    # STYLING
    # =====================================================
    st.markdown("""
    <style>

    .main-title {
        font-size: 36px;
        font-weight: 800;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #4b5563;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #111827;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .insight-box {
        background: linear-gradient(135deg, #1e3a8a, #2563eb);
        padding: 24px;
        border-radius: 18px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    }

    .insight-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .insight-text {
        font-size: 16px;
        line-height: 1.8;
        color: #e0e7ff;
    }

    </style>
    """, unsafe_allow_html=True)

    # =====================================================
    # HEADER
    # =====================================================
    st.markdown(
        '<div class="main-title">📊 Advanced Commercial Intelligence</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Interactive predictive analytics and commercial risk monitoring.</div>',
        unsafe_allow_html=True
    )

    # =====================================================
    # FILTERS
    # =====================================================
    filter1, filter2 = st.columns(2)

    with filter1:

        categories = st.multiselect(
            "Filter Category",
            options=alerts_df[category_col].unique(),
            default=alerts_df[category_col].unique()
        )

    with filter2:

        families = st.multiselect(
            "Filter Product Family",
            options=alerts_df[family_col].unique(),
            default=alerts_df[family_col].unique()
        )

    # =====================================================
    # FILTER DATA
    # =====================================================
    filtered_df = alerts_df[
        (alerts_df[category_col].isin(categories)) &
        (alerts_df[family_col].isin(families))
    ]

    # =====================================================
    # METRICS
    # =====================================================
    total_alerts = len(filtered_df)

    critical = len(
        filtered_df[
            filtered_df["Nivel de Riesgo"] >= 70
        ]
    )

    avg_delay = round(
        filtered_df["Days_Since_Last"].mean(),
        1
    )

    avg_risk = round(
        filtered_df["Nivel de Riesgo"].mean(),
        1
    )

    # =====================================================
    # AI INSIGHT PANEL
    # =====================================================
    st.info( f""" AI Commercial Insight

• {critical} critical-risk accounts require immediate attention.

• Average inactivity: {avg_delay} days

• Portfolio average risk score: {avg_risk}
"""
)

    # =====================================================
    # RISK LEVELS
    # =====================================================
    risk_bins = pd.cut(
        filtered_df["Nivel de Riesgo"],
        bins=[0, 40, 70, 100],
        labels=["Low", "Medium", "Critical"]
    )

    risk_counts = risk_bins.value_counts().reset_index()
    risk_counts.columns = ["Risk", "Count"]

    # =====================================================
    # TOP CLIENTS
    # =====================================================
    top_clients = (
        filtered_df
        .sort_values("Nivel de Riesgo", ascending=False)
        .head(10)
    )

    # =====================================================
    # CHARTS
    # =====================================================
    left, right = st.columns([1, 1.5])

    # =====================================================
    # DONUT CHART
    # =====================================================
    with left:

        st.markdown(
            '<div class="section-title">Risk Severity Overview</div>',
            unsafe_allow_html=True
        )

        fig1 = px.pie(
            risk_counts,
            names="Risk",
            values="Count",
            hole=0.65,
            color="Risk",
            color_discrete_map={
                "Low": "#22c55e",
                "Medium": "#f59e0b",
                "Critical": "#ef4444"
            }
        )

        fig1.update_traces(
            textfont_size=16,
            textfont_color="black",
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}"
        )

        fig1.update_layout(
            template="plotly_dark",
            height=450,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",

            font=dict(
                color="white",
                size=15
            ),

            legend=dict(
                font=dict(
                    color="white",
                    size=14
                ),
                orientation="h",
                y=-0.15,
                x=0.5,
                xanchor="center"
            ),

            margin=dict(
                t=20,
                b=20,
                l=20,
                r=20
            )
        )

        st.plotly_chart(
            fig1,
            use_container_width=True,
            theme=None
        )

    # =====================================================
    # TOP CLIENTS
    # =====================================================
    with right:

        st.markdown(
            '<div class="section-title">Highest Risk Clients</div>',
            unsafe_allow_html=True
        )

        fig2 = px.bar(
            top_clients,
            x="Nivel de Riesgo",
            y="Client_ID",
            orientation="h",
            text="Nivel de Riesgo",
            color="Nivel de Riesgo",
            color_continuous_scale="Reds"
        )

        fig2.update_traces(
            textfont_color="black",
            hovertemplate="<b>Client:</b> %{y}<br><b>Risk:</b> %{x}"
        )

        fig2.update_layout(
            template="plotly_dark",
            height=450,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",

            font=dict(
                color="white",
                size=14
            ),

            xaxis=dict(
                title="Risk Score",
                tickfont=dict(color="white"),
                title_font=dict(color="white")
            ),

            yaxis=dict(
                title="Client ID",
                tickfont=dict(color="white"),
                title_font=dict(color="white")
            ),

            coloraxis_showscale=False,

            margin=dict(
                t=20,
                b=20,
                l=20,
                r=20
            )
        )

        fig2.update_yaxes(
            autorange="reversed"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True,
            theme=None
        )

    # =====================================================
    # HISTOGRAM
    # =====================================================
    st.markdown(
        '<div class="section-title">Purchase Delay Distribution</div>',
        unsafe_allow_html=True
    )

    fig3 = px.histogram(
        filtered_df,
        x="Days_Since_Last",
        nbins=25,
        color_discrete_sequence=["#2563eb"]
    )

    fig3.update_traces(
        hovertemplate="<b>Days:</b> %{x}<br><b>Clients:</b> %{y}"
    )

    fig3.update_layout(
        template="plotly_dark",
        height=450,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",

        font=dict(
            color="white",
            size=14
        ),

        xaxis=dict(
            title="Days Since Last Purchase",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),

        yaxis=dict(
            title="Client Count",
            tickfont=dict(color="white"),
            title_font=dict(color="white")
        ),

        margin=dict(
            t=20,
            b=20,
            l=20,
            r=20
        )
    )

    st.plotly_chart(
        fig3,
        use_container_width=True,
        theme=None
    )

    # =====================================================
    # SCATTER PLOT
    # =====================================================
    st.markdown(
        '<div class="section-title">Risk vs Purchase Delay</div>',
        unsafe_allow_html=True
    )

    fig4 = px.scatter(
        filtered_df,
        x="Days_Since_Last",
        y="Nivel de Riesgo",
        color=category_col,
        size="Nivel de Riesgo",
        hover_data=["Client_ID", family_col]
    )

    fig4.update_layout(
        template="plotly_dark",
        height=500,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",

        font=dict(
            color="white",
            size=14
        ),

        legend=dict(
            font=dict(color="white")
        ),

        xaxis=dict(
            title="Days Since Last Purchase",
            tickfont=dict(color="white")
        ),

        yaxis=dict(
            title="Risk Score",
            tickfont=dict(color="white")
        )
    )

    st.plotly_chart(
        fig4,
        use_container_width=True,
        theme=None
    )

    

