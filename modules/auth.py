import bcrypt
import streamlit as st
from modules.database import get_user_by_email, add_user

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(email, password):
    """Checks user credentials and returns the user Row if valid, else None."""
    user = get_user_by_email(email)
    if user:
        if verify_password(password, user['password_hash']):
            return user
    return None

def register_new_user(name, email, password, role='user'):
    """Registers a new user after hashing the password."""
    # Check if user already exists
    existing = get_user_by_email(email)
    if existing:
        return "exists"
    
    pw_hash = hash_password(password)
    user_id = add_user(name, email, pw_hash, role)
    if user_id:
        return "success"
    else:
        return "error"

def check_auth():
    """Streamlit auth guard. Put at the top of protected pages.
    
    Stops page execution and displays a styled warning if user is not logged in.
    """
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        # Inject custom styles for access denied container
        st.markdown("""
            <style>
            .access-denied-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px;
                background-color: rgba(220, 53, 69, 0.08);
                border: 1px solid rgba(220, 53, 69, 0.2);
                border-radius: 12px;
                text-align: center;
                margin-top: 50px;
            }
            .access-denied-title {
                color: #dc3545;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 15px;
            }
            .access-denied-text {
                font-size: 16px;
                color: #6c757d;
                margin-bottom: 25px;
            }
            .access-denied-btn {
                background: linear-gradient(135deg, #1b365d, #4b6b94);
                color: white !important;
                padding: 10px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 600;
                display: inline-block;
                transition: all 0.3s ease;
            }
            .access-denied-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(27, 54, 93, 0.3);
            }
            </style>
            <div class="access-denied-container">
                <div class="access-denied-title">🔐 Access Restricted</div>
                <p class="access-denied-text">You must be logged in to view this page. Please log in from the main portal.</p>
                <a href="/" target="_self" class="access-denied-btn">Go to Login Page</a>
            </div>
        """, unsafe_allow_html=True)
        st.stop()
