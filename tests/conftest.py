import os

import pytest
import streamlit as st


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Redirects the SQLite database to a temporary file for unit tests.

    Initializes Streamlit session states mock variables for compatibility during tests.
    """
    # 1. Initialize Streamlit Session Mock to prevent Streamlit Errors in backend tests
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "embedding_model" not in st.session_state:
        st.session_state.embedding_model = "bge-small"

    # 2. Redirect DB path to tests database
    import modules.database as db

    original_db_path = db.DB_PATH
    db.DB_PATH = os.path.join(db.DB_DIR, "test_campusgpt.db")

    # Clean up any leftover test db
    if os.path.exists(db.DB_PATH):
        try:
            os.remove(db.DB_PATH)
        except Exception:
            pass

    # Initialize schema
    db.init_db()

    yield

    # Teardown test db
    if os.path.exists(db.DB_PATH):
        try:
            os.remove(db.DB_PATH)
        except Exception:
            pass

    # Restore original db path just in case
    db.DB_PATH = original_db_path
