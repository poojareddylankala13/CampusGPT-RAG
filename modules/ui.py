import streamlit as st
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def inject_custom_css():
    """Reads assets/styles.css and injects it into the page."""
    css_path = os.path.join(BASE_DIR, 'assets', 'styles.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def render_sidebar():
    """Renders a consistent sidebar layout for all subpages."""
    with st.sidebar:
        st.markdown("### 🎓 CampusGPT")
        if st.session_state.get('authenticated'):
            st.markdown(f"**User**: {st.session_state.get('user_name')}")
            st.markdown(f"**Role**: `{st.session_state.get('user_role', 'user').upper()}`")
            
            st.markdown("---")
            st.markdown("#### ⚙️ Settings")
            api_key = st.text_input("Gemini API Key", type="password", value=st.session_state.get("gemini_api_key", ""))
            if api_key != st.session_state.get("gemini_api_key"):
                st.session_state.gemini_api_key = api_key
                st.toast("API Key updated!", icon="🔑")
                
            st.markdown("---")
            if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_signout"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.user_role = "user"
                st.rerun()
        else:
            st.info("Please sign in from the main portal.")
