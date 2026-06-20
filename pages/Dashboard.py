import streamlit as st

from modules.auth import check_auth
from modules.database import get_kpis
from modules.ui import inject_custom_css, render_sidebar

# 1. Check Auth (redirects/stops if not logged in)
check_auth()

# 2. Page Configuration & Setup
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>📈 CampusGPT Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Overview of university documentation indexing status and system usage analytics.")

# 3. Load Metrics
kpis = get_kpis()

# 4. Render Metric Cards in custom styled layout
st.markdown(
    f"""
    <div class="metric-container">
        <div class="metric-card">
            <div class="metric-val">{kpis['total_docs']}</div>
            <div class="metric-label">Total Documents</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{kpis['total_pages']}</div>
            <div class="metric-label">Pages Processed</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{kpis['total_chunks']}</div>
            <div class="metric-label">Chunks Generated</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{kpis['total_questions']}</div>
            <div class="metric-label">Questions Asked</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">{kpis['total_users']}</div>
            <div class="metric-label">Registered Users</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# 5. Quick actions dashboard
st.markdown("### ⚡ Quick Insights")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "💡 **RAG Assistant Capabilities**\n\n"
        "- Fetches real-time answers using **Gemini 2.5 Flash**.\n"
        "- Connects query to local **FAISS Vector Index** of university policies.\n"
        "- Displays source files and exact page numbers for easy verification."
    )

with col2:
    st.success(
        "📊 **Data Freshness**\n\n"
        "All uploaded documents are instantly indexed. If files are deleted by administrators, "
        "the vector index is automatically rebuilt to keep queries accurate. Go to the **Upload** page to add files."
    )
