import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar
from utils.data_generator import generate_mining_telemetry_dataset

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page1_title"))
st.caption(get_text("page1_caption"))

@st.cache_data
def load_data():
    df = None
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "public_mining_equipment_dataset.csv",
        Path("data/raw/public_mining_equipment_dataset.csv"),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p)
                break
            except Exception:
                pass
    if df is None or df.empty:
        df = generate_mining_telemetry_dataset(n_samples=1200, random_state=42)
    else:
        np.random.seed(42)
        n = len(df)
        if "fatigue_index" not in df.columns:
            df["fatigue_index"] = np.random.uniform(0.1, 0.85, size=n).round(2)
        if "worker_bpm" not in df.columns:
            df["worker_bpm"] = (70 + df["fatigue_index"] * 50 + np.random.normal(0, 5, size=n)).round(1)
        if "gas_co_ppm" not in df.columns:
            df["gas_co_ppm"] = np.random.exponential(12.0, size=n).clip(0, 100).round(1)
        if "dust_density_mg_m3" not in df.columns:
            df["dust_density_mg_m3"] = np.random.exponential(1.5, size=n).clip(0.1, 8.0).round(2)
        if "ambient_light_lux" not in df.columns:
            df["ambient_light_lux"] = np.random.normal(60.0, 20.0, size=n).clip(5, 120).round(1)
    return df

df = load_data()

risk_map = {0: get_text("label_low"), 1: get_text("label_medium"), 2: get_text("label_high")}
if df["risk_level"].dtype == object:
    df["risk_label"] = df["risk_level"]
    df["risk_level"] = df["risk_level"].map({"BAJO": 0, "MEDIO": 1, "ALTO": 2, "LOW": 0, "MEDIUM": 1, "HIGH": 2}).fillna(0).astype(int)
else:
    df["risk_label"] = df["risk_level"].map(risk_map)

# Métricas Top
m1, m2, m3, m4 = st.columns(4)
m1.metric(get_text("metric_total_telemetry"), f"{len(df):,}")
m2.metric(get_text("metric_high_risk_level"), f"{(df['risk_level']==2).sum()} ({(df['risk_level']==2).mean()*100:.1f}%)")
m3.metric(get_text("metric_avg_dist"), f"{df['distance_3d'].mean():.2f} m")
m4.metric(get_text("metric_avg_ttc"), f"{df['ttc'].mean():.2f} s")

st.divider()

st.subheader(get_text("sample_multimodal"))
st.dataframe(df.head(50), use_container_width=True)

st.divider()

# Gráficos Principales
c1, c2 = st.columns(2)

with c1:
    st.subheader(get_text("fig1_title"))
    risk_counts = df['risk_label'].value_counts().reset_index()
    risk_counts.columns = ['Nivel_Riesgo', 'Cantidad']
    fig1 = px.pie(
        risk_counts,
        values='Cantidad',
        names='Nivel_Riesgo',
        hole=0.4,
        color='Nivel_Riesgo',
        color_discrete_map={get_text('label_low'): '#22c55e', get_text('label_medium'): '#eab308', get_text('label_high'): '#ef4444'}
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader(get_text("fig2_title"))
    fig2 = px.histogram(
        df,
        x="distance_3d",
        color="risk_label",
        nbins=35,
        barmode="overlay",
        color_discrete_map={get_text('label_low'): '#22c55e', get_text('label_medium'): '#eab308', get_text('label_high'): '#ef4444'}
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

c3, c4 = st.columns(2)

with c3:
    st.subheader(get_text("fig3_title"))
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()
    fig3 = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        aspect="auto"
    )
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader(get_text("fig4_title"))
    fig4 = px.scatter(
        df,
        x="fatigue_index",
        y="worker_bpm",
        color="risk_label",
        size=np.maximum(df["gas_co_ppm"], 0.1),
        color_discrete_map={get_text('label_low'): '#22c55e', get_text('label_medium'): '#eab308', get_text('label_high'): '#ef4444'}
    )
    st.plotly_chart(fig4, use_container_width=True)

st.subheader(get_text("table1_title"))
st.dataframe(df.describe().T.round(3), use_container_width=True)
