import json
import os
import streamlit as st

def load_translation(lang_code):
    locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
    file_path = os.path.join(locales_dir, f"{lang_code}.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to English
        with open(os.path.join(locales_dir, 'en.json'), 'r', encoding='utf-8') as f:
            return json.load(f)

def init_i18n():
    if 'lang' not in st.session_state:
        st.session_state.lang = 'es' # Default to Spanish
    if 't' not in st.session_state:
        st.session_state.t = load_translation(st.session_state.lang)

def change_lang(lang_code):
    st.session_state.lang = lang_code
    st.session_state.t = load_translation(lang_code)
