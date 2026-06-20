import streamlit as st

from modules.auth import check_auth
from modules.llm_local import get_installed_gguf_models, is_llama_available
from modules.ui import inject_custom_css, render_sidebar

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>🤖 Local Model Registry</h1>", unsafe_allow_html=True)
st.markdown(
    "Monitor offline GGUF language models, inspect hardware footprints, and configure the active local generator."
)

# Check llama availability
llama_ok = is_llama_available()
if not llama_ok:
    st.error(
        "⚠️ Local LLM compilation (`llama-cpp-python`) is not installed or failed to load. "
        "To run offline GGUF models, please compile llama-cpp-python in your environment. "
        "The system will run in cloud Gemini mode in the meantime."
    )

# Scan models/ folder
gguf_models = get_installed_gguf_models()

# Ensure session state for active GGUF model exists
if "active_gguf_model" not in st.session_state:
    st.session_state.active_gguf_model = ""

if not gguf_models:
    st.warning("📂 No GGUF models were found inside the `models/` folder.")

    st.markdown(
        """
        ### 📥 Download GGUF Models Guide
        To run CampusGPT fully offline, you need to place a GGUF model inside the **`models/`** folder of this project.

        We recommend downloading one of the following lightweight instruct models from Hugging Face:

        1. **Qwen2.5 3B / 7B Instruct GGUF** (Highly Recommended)
           * *Download link*: [Hugging Face Qwen2.5 GGUF](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF)
           * *Recommended file*: `qwen2.5-3b-instruct-q4_k_m.gguf` (~2.2 GB)

        2. **Gemma 2 2B / 9B IT GGUF**
           * *Download link*: [Hugging Face Gemma-2-2B GGUF](https://huggingface.co/bartowski/gemma-2-2b-it-GGUF)
           * *Recommended file*: `gemma-2-2b-it-Q4_K_M.gguf` (~1.6 GB)

        3. **Phi-4 Mini 3.8B GGUF**
           * *Download link*: [Hugging Face Phi-4 Mini GGUF](https://huggingface.co/bartowski/phi-4-mini-GGUF)
           * *Recommended file*: `phi-4-mini-Q4_K_M.gguf` (~2.4 GB)

        #### Setup Instructions:
        * Create a folder named `models` in the root of the project (if it doesn't already exist).
        * Download the `.gguf` file of your choice.
        * Place the downloaded file directly into `models/`.
        * Refresh this page to select and activate the model.
    """
    )
else:
    st.markdown("### 📋 Installed GGUF Models")
    st.write(f"Found {len(gguf_models)} model file(s) in `models/`:")

    # Selection Box
    model_filenames = [m["filename"] for m in gguf_models]

    # Match default from session state
    default_idx = 0
    if st.session_state.active_gguf_model in model_filenames:
        default_idx = model_filenames.index(st.session_state.active_gguf_model)

    selected_model_file = st.selectbox(
        "Select Active Local GGUF Model:",
        options=model_filenames,
        index=default_idx,
        help="Select the model weights to load for Llama.cpp inference.",
    )

    # Save selection
    st.session_state.active_gguf_model = selected_model_file

    # Display selected model details
    selected_model = [m for m in gguf_models if m["filename"] == selected_model_file][0]

    st.markdown("---")
    st.markdown(f"#### 📊 Active Model Properties: `{selected_model['display_name']}`")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="background-color: rgba(27, 54, 93, 0.04); padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 20px; font-weight: 700; color: #1b365d;">{selected_model["size_gb"]}</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #666; font-weight: 600; margin-top: 5px;">File Size</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color: rgba(27, 54, 93, 0.04); padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 20px; font-weight: 700; color: #1b365d;">{selected_model["context_len"]} tokens</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #666; font-weight: 600; margin-top: 5px;">Context Length Limit</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="background-color: rgba(197, 160, 89, 0.08); padding: 15px; border-radius: 8px; text-align: center;">
                <div style="font-size: 20px; font-weight: 700; color: #8c6828;">~ {selected_model["ram_estimate"]}</div>
                <div style="font-size: 11px; text-transform: uppercase; color: #666; font-weight: 600; margin-top: 5px;">Est. RAM Needed</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.info(
        "💡 **Performance Tip**: GGUF models are loaded dynamically when you submit your first query. "
        "Keep other memory-intensive applications closed to avoid hitting the paging file on your disk."
    )
