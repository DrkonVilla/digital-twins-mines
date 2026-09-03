import streamlit as st
import os
from utils.i18n import init_i18n, change_lang
from PIL import Image

# Configuración de página
st.set_page_config(
    page_title="M-11 ML Dashboard",
    page_icon="⛏️",
    layout="wide"
)

# Inicializar i18n
init_i18n()
t = st.session_state.t

# Ruta base del frontend para las imágenes
IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "img")

# Mapeo de idiomas y banderas (con nombres exactos de los archivos dados)
FLAGS = {
    "es": {"file": "spain.png", "label": "Español"},
    "en": {"file": "united-states.png", "label": "English"},
    "pt": {"file": "brazil-.png", "label": "Português"},
    "zh": {"file": "china.png", "label": "中文"},
    "fr": {"file": "france.png", "label": "Français"},
}

def render_sidebar():
    st.sidebar.title("M-11 Dashboard")
    st.sidebar.markdown(f"**{t['sidebar_lang']}**")
    
    # Renderizar botones de banderas en columnas
    cols = st.sidebar.columns(5)
    for idx, (lang_code, info) in enumerate(FLAGS.items()):
        img_path = os.path.join(IMG_DIR, info["file"])
        with cols[idx]:
            # Usamos un botón para cambiar el idioma. 
            # Streamlit no soporta imagenes directamente cliqueables nativamente sin HTML,
            # pero podemos usar el label del botón o inyectar HTML. 
            # Para mayor interactividad, si st.button se presiona, cambiamos.
            try:
                img = Image.open(img_path)
                st.image(img, use_container_width=True)
            except Exception as e:
                pass
            if st.button("🌐", key=f"btn_{lang_code}", help=info["label"]):
                change_lang(lang_code)
                st.rerun()
                
    st.sidebar.divider()
    st.sidebar.info("M-11 Digital Twin AI System")

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Hide sidebar completely on login screen using CSS
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("Login - M-11 Dashboard")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            import requests
            auth_data = {"username": username, "password": password}
            try:
                res = requests.post("http://localhost:8000/api/v1/auth/login", data=auth_data)
                if res.status_code == 200:
                    st.session_state.token = res.json().get("access_token")
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Cannot connect to the backend: {e}")
        return

    render_sidebar()
    
    st.title(t["title"])
    st.markdown(f"### {t['welcome']}")
    st.markdown(t["desc"])
    
    st.divider()
    
    # Contenido Home
    st.info("👈 " + t["desc"])

if __name__ == "__main__":
    main()
