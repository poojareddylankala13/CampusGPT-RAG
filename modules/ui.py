import os

import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def inject_custom_css():
    """Reads assets/styles.css and injects it into the page."""
    css_path = os.path.join(BASE_DIR, "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_sidebar():
    """Renders a consistent sidebar layout for all subpages."""
    # Initialize default settings variables
    if "ai_mode" not in st.session_state:
        st.session_state.ai_mode = "gemini"
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = "bge-small"
    if "retrieval_method" not in st.session_state:
        st.session_state.retrieval_method = "similarity"
    if "top_k" not in st.session_state:
        st.session_state.top_k = 5
    if "threshold" not in st.session_state:
        st.session_state.threshold = 0.6
    if "active_gguf_model" not in st.session_state:
        st.session_state.active_gguf_model = ""

    with st.sidebar:
        st.markdown("### 🎓 CampusGPT")
        if st.session_state.get("authenticated"):
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
