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

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

from utils.translations import get_text, get_current_lang, init_language

def render_sidebar():
    init_language()
    st.sidebar.title(get_text("sidebar_title"))
    
    current_l = get_current_lang()
    lang_choice = st.sidebar.selectbox(
        get_text("sidebar_lang"),
        options=["es", "en"],
        format_func=lambda x: "🇪🇸 Español" if x == "es" else "🇺🇸 English",
        index=0 if current_l == "es" else 1,
        key="global_lang_selectbox"
    )
    if lang_choice != current_l:
        change_lang(lang_choice)
        safe_rerun()
        
    st.sidebar.divider()
    st.sidebar.info(get_text("app_title"))

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "pass_input" not in st.session_state:
        st.session_state.pass_input = ""

    if not st.session_state.authenticated:
        # Hide sidebar completely on login screen using CSS
        st.markdown("""
            <style>
                [data-testid="stSidebar"] {
                    display: none;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.title("🔑 Login - M-11 ML Dashboard")
        st.caption("Sistema de Alerta Temprana de Riesgo Humano — Gemelo Digital")

        col_cfg1, col_cfg2 = st.columns([2, 1])
        with col_cfg1:
            backend_mode = st.radio(
                "Servidor de Autenticación:",
                ["🌐 Nube (Render)", "💻 Local (localhost:8000)", "🛡️ Modo Offline / Demostración"],
                index=0,
                horizontal=True
            )
        
        if backend_mode == "🌐 Nube (Render)":
            BACKEND_URL = os.getenv("BACKEND_URL", "https://m11-backend-ub10.onrender.com").rstrip("/")
        elif backend_mode == "💻 Local (localhost:8000)":
            BACKEND_URL = "http://localhost:8000"
        else:
            BACKEND_URL = None

        login_url = f"{BACKEND_URL}/api/v1/auth/login" if BACKEND_URL else None

        # Botón de relleno rápido y demo
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("📝 Rellenar Credenciales Admin", use_container_width=True):
                st.session_state.user_input = "admin@example.com"
                st.session_state.pass_input = "admin123"
                safe_rerun()

        with col_btn2:
            if st.button("⚡ Login Directo (Nube o Demo)", use_container_width=True):
                if not login_url:
                    st.session_state.token = "demo-offline-access-token"
                    st.session_state.authenticated = True
                    safe_rerun()
                else:
                    import requests
                    try:
                        with st.spinner("Conectando con el backend (esperando respuesta de Render)..."):
                            res = requests.post(login_url, data={"username": "admin@example.com", "password": "admin123"}, timeout=45)
                        if res.status_code == 200:
                            st.session_state.token = res.json().get("access_token")
                            st.session_state.authenticated = True
                            safe_rerun()
                        else:
                            st.warning(f"Backend devolvió estado {res.status_code}. Activando acceso local seguro de demostración.")
                            st.session_state.token = "demo-offline-access-token"
                            st.session_state.authenticated = True
                            safe_rerun()
                    except Exception as e:
                        st.info("💡 El servidor de Render estaba en reposo o no respondió a tiempo. Accediendo automáticamente con sesión local de contingencia.")
                        st.session_state.token = "demo-offline-access-token"
                        st.session_state.authenticated = True
                        safe_rerun()

        st.divider()

        username = st.text_input("Username / Email", value=st.session_state.user_input, key="input_user")
        password = st.text_input("Password", value=st.session_state.pass_input, type="password", key="input_pass")

        if st.button("Iniciar Sesión", type="primary", use_container_width=True):
            if not login_url:
                if username == "admin@example.com" and password == "admin123":
                    st.session_state.token = "demo-offline-access-token"
                    st.session_state.authenticated = True
                    safe_rerun()
                else:
                    st.error("Credenciales inválidas para modo demostración.")
            else:
                import requests
                auth_data = {"username": username, "password": password}
                try:
                    with st.spinner("Autenticando con el servidor..."):
                        res = requests.post(login_url, data=auth_data, timeout=45)
                    if res.status_code == 200:
                        st.session_state.token = res.json().get("access_token")
                        st.session_state.authenticated = True
                        safe_rerun()
                    else:
                        st.error(f"Credenciales inválidas o error {res.status_code}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Tiempo de espera agotado (Render en cold-start). Puedes seleccionar '🛡️ Modo Offline / Demostración' arriba para ingresar inmediatamente.")
                except Exception as e:
                    st.error(f"Error de conexión con el backend: {e}")
        return

    render_sidebar()
    
    st.title(get_text("title", "Panel Científico — Gemelo Digital y Prevención de Riesgos (M-11)"))
    st.markdown(f"### {get_text('welcome', 'Bienvenido al Dashboard Científico de IA M-11')}")
    st.markdown(get_text("desc", "Utilice la barra lateral para navegar entre las secciones."))
    
    st.divider()
    
    # Contenido Home
    st.info("👈 " + get_text("desc", "Utilice la barra lateral para navegar entre las secciones."))

if __name__ == "__main__":
    main()
