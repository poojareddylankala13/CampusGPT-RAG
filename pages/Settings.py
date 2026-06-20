import streamlit as st
from modules.auth import check_auth
from modules.ui import inject_custom_css, render_sidebar
from modules.rag_pipeline import clear_query_cache
from modules.embedding_manager import clear_embeddings_cache

# 1. Auth Guard
check_auth()

# 2. Page Configuration
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>⚙️ Application Settings</h1>", unsafe_allow_html=True)
st.markdown("Configure RAG execution parameters, AI modes, indexing frameworks, and caches.")

# Initialize session state variables with default values if not present
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
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Settings Form
with st.form("settings_form"):
    st.markdown("### 🤖 LLM Generation Modes")
    
    # Check if local model capability is available
    from modules.llm_local import is_llama_available
    llama_ok = is_llama_available()
    
    mode_options = ["Gemini API Mode", "Local Llama.cpp Mode"]
    default_mode_idx = 0 if st.session_state.ai_mode == "gemini" else 1
    
    ai_mode_selection = st.radio(
        "Active LLM Mode:",
        options=mode_options,
        index=default_mode_idx,
        help="Choose between cloud execution (Gemini 2.5 Flash) or running offline models locally via Llama.cpp."
    )
    
    # Soft warning if local LLM is selected but llama-cpp is not installed
    if ai_mode_selection == "Local Llama.cpp Mode" and not llama_ok:
        st.warning("⚠️ Llama.cpp is not compiled or installed in this environment. The system will fall back to Gemini mode unless you resolve the dependencies.")

    st.markdown("---")
    st.markdown("### 🔀 Retrieval & Embeddings Settings")
    
    col_emb, col_ret = st.columns(2)
    
    with col_emb:
        emb_options = {"BGE Small (BAAI/bge-small-en-v1.5)": "bge-small", "MiniLM (all-MiniLM-L6-v2)": "minilm"}
        active_emb_name = [k for k, v in emb_options.items() if v == st.session_state.embedding_model][0]
        selected_emb = st.selectbox(
            "Embedding Model:",
            options=list(emb_options.keys()),
            index=list(emb_options.keys()).index(active_emb_name),
            help="BGE Small provides higher accuracy. MiniLM is lightweight and runs faster on limited hardware."
        )
        
    with col_ret:
        ret_options = {"Similarity Vector Search": "similarity", "Max Marginal Relevance (MMR)": "mmr"}
        active_ret_name = [k for k, v in ret_options.items() if v == st.session_state.retrieval_method][0]
        selected_ret = st.selectbox(
            "Retrieval Search Method:",
            options=list(ret_options.keys()),
            index=list(ret_options.keys()).index(active_ret_name),
            help="MMR balances document relevance with diversity to avoid duplicate chunks in the LLM context."
        )
        
    col_k, col_t = st.columns(2)
    
    with col_k:
        selected_k = st.slider(
            "Top-K Chunks to Retrieve:",
            min_value=3,
            max_value=10,
            value=st.session_state.top_k,
            help="Number of text passages sent to the LLM for question answering."
        )
        
    with col_t:
        selected_t = st.slider(
            "Minimum Similarity Match Threshold (%):",
            min_value=50,
            max_value=90,
            value=int(st.session_state.threshold * 100),
            step=5,
            help="Filters out document fragments that do not meet this match percentage."
        )

    st.markdown("---")
    st.markdown("### 🎨 Aesthetics Theme")
    theme_options = ["Light Theme", "Dark Theme"]
    default_theme_idx = 0 if st.session_state.theme == "light" else 1
    selected_theme = st.selectbox(
        "Application Custom Style:",
        options=theme_options,
        index=default_theme_idx
    )

    # Submit form
    submit_btn = st.form_submit_button("💾 Save Settings", use_container_width=True)
    
    if submit_btn:
        # Update Session States
        st.session_state.ai_mode = "gemini" if ai_mode_selection == "Gemini API Mode" else "local"
        st.session_state.embedding_model = emb_options[selected_emb]
        st.session_state.retrieval_method = ret_options[selected_ret]
        st.session_state.top_k = selected_k
        st.session_state.threshold = selected_t / 100.0
        st.session_state.theme = "light" if selected_theme == "Light Theme" else "dark"
        
        st.success("🎉 Configuration updated successfully! Custom variables have been saved.")
        st.toast("Settings saved!", icon="💾")

# --- Cache Management Panel ---
st.markdown("---")
st.markdown("### 🧹 Cache Management")
st.write("Clear local cache structures to free up storage or force the RAG engine to regenerate vector search responses.")

col_cache1, col_cache2 = st.columns(2)

with col_cache1:
    if st.button("🧹 Clear Query Cache", use_container_width=True):
        if clear_query_cache():
            st.success("Successfully cleared query response caches.")
        else:
            st.error("Failed to clear query cache.")

with col_cache2:
    if st.button("🧹 Clear Embeddings Cache", use_container_width=True):
        if clear_embeddings_cache():
            st.success("Successfully cleared text chunk embedding caches.")
        else:
            st.error("Failed to clear embedding vector cache.")
