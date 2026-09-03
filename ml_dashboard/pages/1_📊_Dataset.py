import streamlit as st
import pandas as pd
import plotly.express as px
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_dataset"])

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("../data/raw/synthetic_interactions.csv")
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    st.write(f"### M-11 Synthetic Interactions Dataset")
    st.dataframe(df.head(100))
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Level Distribution")
        fig = px.pie(df, names='risk_level', title="Alerts by Risk Level", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Machine Status")
        fig2 = px.bar(df['machine_status'].value_counts().reset_index(), x='machine_status', y='count', title="Machine Status Frequency")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No data available.")
