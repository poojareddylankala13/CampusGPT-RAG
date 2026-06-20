import os

import streamlit as st
from dotenv import load_dotenv

# Set page config MUST be the first Streamlit command in the script
st.set_page_config(
    page_title="CampusGPT - University Knowledge Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load env variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from modules.auth import authenticate_user, register_new_user  # noqa: E402
from modules.database import init_db  # noqa: E402

# Initialize database
init_db()


# --- CSS Injection Helper ---
def inject_custom_css():
    """Reads assets/styles.css and injects it into the Streamlit app page."""
    css_path = os.path.join(BASE_DIR, "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# Inject CSS for consistent styling
inject_custom_css()

# Initialize Session States
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "user"
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

# Initialize RAG specific session settings
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

# --- Login & Registration Page ---
if not st.session_state.authenticated:
    # Center container style
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px;">
            <h1 class="gradient-header" style="font-size: 3rem;">🎓 CampusGPT</h1>
            <p style="color: #6c757d; font-size: 1.2rem; font-weight: 500;">
                AI-Powered University Knowledge & Document Assistant
            </p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

        with tab_login:
            st.markdown("<h3 style='margin-bottom: 20px;'>Welcome Back</h3>", unsafe_allow_html=True)
            login_email = st.text_input("University Email", key="login_email_input")
            login_password = st.text_input("Password", type="password", key="login_pass_input")

            # Inline API Key setup option for convenience if env is empty
            if not os.getenv("GEMINI_API_KEY"):
                st.info("💡 Protip: No Gemini API Key found in .env. You can set it below for this session.")
                custom_key = st.text_input(
                    "Gemini API Key (Optional)", type="password", value=st.session_state.gemini_api_key
                )
                if custom_key:
                    st.session_state.gemini_api_key = custom_key

            if st.button("Sign In", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please fill in all fields.")
                else:
                    user = authenticate_user(login_email, login_password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user["id"]
                        st.session_state.user_name = user["name"]
                        st.session_state.user_email = user["email"]
                        st.session_state.user_role = user["role"]
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with tab_register:
            st.markdown("<h3 style='margin-bottom: 20px;'>Create a New Account</h3>", unsafe_allow_html=True)
            reg_name = st.text_input("Full Name", key="reg_name_input")
            reg_email = st.text_input("University Email Address", key="reg_email_input")
            reg_password = st.text_input("Password", type="password", key="reg_pass_input")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm_input")

            # Simple registration validation
            if st.button("Register Account", use_container_width=True):
                if not reg_name or not reg_email or not reg_password or not reg_confirm:
                    st.error("Please fill in all fields.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif "@" not in reg_email or "." not in reg_email:
                    st.error("Please enter a valid email address.")
                else:
                    status = register_new_user(reg_name, reg_email, reg_password)
                    if status == "success":
                        st.success("Account created successfully! Please log in above.")
                    elif status == "exists":
                        st.error("An account with this email already exists.")
                    else:
                        st.error("An error occurred during registration. Please try again.")

else:
    # --- Authenticated User Welcome Page ---
    # Sidebar logout
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.user_name}")
        st.markdown(f"**Role**: `{st.session_state.user_role.upper()}`")
        st.markdown(f"**Email**: {st.session_state.user_email}")

        # Configure API Key dynamically in sidebar if needed
        st.markdown("---")
        st.markdown("#### ⚙️ Settings")
        api_key_input = st.text_input("Gemini API Key", type="password", value=st.session_state.gemini_api_key)
        if api_key_input != st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = api_key_input
            st.toast("API Key updated!", icon="🔑")

        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.session_state.user_role = "user"
            st.rerun()

    # Home Dashboard page content
    st.markdown(
        """
        <h1 class="gradient-header">🎓 Welcome to CampusGPT</h1>
        <p style="font-size: 1.1rem; color: #555555; margin-bottom: 30px;">
            Your intelligent assistant for traversing university policies, course details, calendars, and syllabus information.
        </p>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧭 Quick Navigation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div style="background-color: rgba(27, 54, 93, 0.05); padding: 25px; border-radius: 12px; border-left: 5px solid #1b365d; height: 100%;">
                <h4 style="margin-top: 0; color: #1b365d;">💬 RAG Assistant Chat</h4>
                <p style="font-size: 14px; color: #555555;">Ask questions about university policies, grades, attendance, exam dates, or syllabi and receive citations from original documents.</p>
                <p style="font-size: 12px; color: #888;">Go to <b>Chat</b> in the sidebar to start.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background-color: rgba(197, 160, 89, 0.08); padding: 25px; border-radius: 12px; border-left: 5px solid #c5a059; height: 100%;">
                <h4 style="margin-top: 0; color: #8c6828;">📄 Document Upload & Summaries</h4>
                <p style="font-size: 14px; color: #555555;">Upload new university guidelines in PDF format and generate executive summaries with action items using AI.</p>
                <p style="font-size: 12px; color: #888;">Go to <b>Upload</b> or <b>Summarize</b> in the sidebar.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div style="background-color: rgba(75, 107, 148, 0.06); padding: 25px; border-radius: 12px; border-left: 5px solid #4b6b94; height: 100%;">
                <h4 style="margin-top: 0; color: #4b6b94;">🔍 Semantic Search & Analytics</h4>
                <p style="font-size: 14px; color: #555555;">Perform direct vector search to locate specific clauses and review metrics charts tracking user interactions.</p>
                <p style="font-size: 12px; color: #888;">Go to <b>Search</b> or <b>Analytics</b> in the sidebar.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    # Render instructions warning if API Key is empty
    if not st.session_state.gemini_api_key:
        st.warning(
            "⚠️ Gemini API Key is missing. Please configure it in the sidebar on the left "
            "or set the GEMINI_API_KEY environment variable in a .env file to enable Chat and Summarization."
        )
