import streamlit as st
import requests
import json
import pandas as pd
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_twin"])
st.write("Real-time inference using the Digital Twin prediction backend.")

API_URL = "http://localhost:8000/api/v1/predict/"

with st.form("digital_twin_test_form"):
    st.subheader("Input Parameters")
    col1, col2 = st.columns(2)
    with col1:
        distance_3d = st.number_input("Distance 3D (m)", min_value=0.0, max_value=100.0, value=15.0)
        worker_speed = st.number_input("Worker Speed (m/s)", min_value=0.0, max_value=10.0, value=1.5)
        machine_speed = st.number_input("Machine Speed (m/s)", min_value=0.0, max_value=30.0, value=5.0)
        relative_speed = st.number_input("Relative Speed (m/s)", min_value=0.0, max_value=40.0, value=6.5)
    with col2:
        ttc = st.slider("Time to Collision (TTC - sec)", 0.0, 60.0, 5.0)
        in_restricted_zone = st.selectbox("In Restricted Zone?", [0, 1])
        machine_status = st.selectbox("Machine Status (0=Off, 1=Idle, 2=Active)", [0, 1, 2], index=2)
        
    submit = st.form_submit_button(t["btn_simulate"])

if submit:
    payload = {
        "worker_id": 1,
        "machine_id": 1,
        "worker_x": 0.0,
        "worker_y": 0.0,
        "worker_z": 0.0,
        "machine_x": distance_3d,
        "machine_y": 0.0,
        "machine_z": 0.0,
        "direction_worker": 90,
        "direction_machine": 270,
        "distance_3d": distance_3d,
        "ttc": ttc,
        "worker_speed": worker_speed,
        "machine_speed": machine_speed,
        "relative_speed": relative_speed,
        "in_restricted_zone": in_restricted_zone,
        "machine_status": machine_status
    }
    
    with st.spinner("Connecting to Digital Twin backend..."):
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {st.session_state.get('token', '')}"
            }
            response = requests.post(API_URL, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                risk = result.get("risk_level", "UNKNOWN")
                prob = result.get("probability", 0.0)
                
                if risk == "ALTO":
                    st.error(f"⚠️ HIGH RISK DETECTED (Probability: {prob*100:.1f}%)")
                elif risk == "MEDIO":
                    st.warning(f"⚠️ MEDIUM RISK DETECTED (Probability: {prob*100:.1f}%)")
                else:
                    st.success(f"✅ LOW RISK (Probability: {prob*100:.1f}%)")
                    
                st.json(result)
            else:
                st.error(f"API Error {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure the FastAPI server is running on localhost:8000")
