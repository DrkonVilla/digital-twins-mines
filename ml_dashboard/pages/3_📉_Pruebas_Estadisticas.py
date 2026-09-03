import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import scipy.stats as stats
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_stats"])
st.write("Robust statistical tests and distribution analysis (ANOVA, T-Test, Chi-Square).")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("../data/raw/synthetic_interactions.csv")
    except Exception:
        return None

df = load_data()

if df is not None and not df.empty:
    st.subheader("1. Violin Plots (Distance vs Risk Level)")
    fig = px.violin(df, y="distance_3d", x="risk_level", color="risk_level", box=True, points="all")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("2. Correlation Matrix")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    fig2 = px.imshow(corr, text_auto=True, aspect="auto")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("3. ANOVA Test: Distance across Risk Levels")
    # Perform one-way ANOVA
    groups = df.groupby("risk_level")["distance_3d"].apply(list)
    f_val, p_val = stats.f_oneway(*groups)
    st.info(f"F-Statistic: {f_val:.4f} | P-Value: {p_val:.4e}")
    if p_val < 0.05:
        st.success("Significant difference found in 'distance_3d' across different risk levels.")
    else:
        st.warning("No significant difference found in 'distance_3d' across risk levels.")

else:
    st.warning("No data available.")
