import streamlit as st
import os
import requests
from utils.i18n import init_i18n

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login from the main page.")
    st.stop()

init_i18n()
t = st.session_state.t

st.title(t["nav_reports"])
st.write("Generate and download system reports directly from the dashboard.")

API_URL = "http://localhost:8000/api/v1/reports"

col1, col2 = st.columns(2)

with col1:
    st.subheader("Generate Report")
    format_type = st.selectbox("Format", ["pdf", "excel", "word"])
    
    if st.button("Generate"):
        with st.spinner(f"Generating {format_type.upper()} report..."):
            try:
                # We assume no auth needed or we can pass a dummy for now since it's local test
                # In real scenario, we'd need JWT token in headers
                res = requests.post(f"{API_URL}?format={format_type}")
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Report generated successfully: {data.get('filename')}")
                    # Save filename in session state to allow downloading
                    if 'reports' not in st.session_state:
                        st.session_state.reports = []
                    st.session_state.reports.append(data.get('filename'))
                else:
                    st.error(f"Error: {res.status_code} - {res.text}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to backend.")

with col2:
    st.subheader("Available Reports")
    if 'reports' in st.session_state and st.session_state.reports:
        for filename in st.session_state.reports:
            st.write(f"📄 {filename}")
            download_url = f"{API_URL}/{filename}/download"
            st.markdown(f"[Download {filename}]({download_url})")
    else:
        st.info("No reports generated yet in this session.")
