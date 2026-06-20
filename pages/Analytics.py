import streamlit as st

from modules.analytics import (
    create_activity_chart,
    create_feedback_chart,
    create_storage_chart,
    create_user_activity_chart,
)
from modules.auth import check_auth
from modules.database import get_analytics_metrics, get_kpis
from modules.ui import inject_custom_css, render_sidebar

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>📊 CampusGPT System Analytics</h1>", unsafe_allow_html=True)
st.markdown("Visual reports displaying document metrics, user query trends, search activity, and helpfulness feedback.")

# 3. Load Metrics & Analytics Data
kpis = get_kpis()
data = get_analytics_metrics()

# 4. Display high-level stats cards
col1, col2, col3, col4 = st.columns(4)

# Calculate storage size in MB
total_bytes = sum(doc["file_size"] for doc in data["docs_storage"]) if data["docs_storage"] else 0
total_mb = total_bytes / (1024 * 1024)

with col1:
    st.metric("Total Documents", kpis["total_docs"])
with col2:
    st.metric("Total Users Registered", kpis["total_users"])
with col3:
    st.metric("Total RAG Questions", kpis["total_questions"])
with col4:
    st.metric("Disk Storage Used", f"{total_mb:.2f} MB")

st.markdown("---")

# 5. Render charts
# Storage and Feedback charts side-by-side
col_left, col_right = st.columns(2)

with col_left:
    fig_storage = create_storage_chart(data["docs_storage"])
    if fig_storage:
        st.plotly_chart(fig_storage, use_container_width=True)
    else:
        st.info("No storage metrics available. Upload PDFs to view charts.")

with col_right:
    fig_feedback = create_feedback_chart(data["feedback_scores"])
    if fig_feedback:
        st.plotly_chart(fig_feedback, use_container_width=True)
    else:
        st.info("No feedback ratings submitted yet. Vote on AI answers to view metrics.")

# Activity line chart
st.markdown("### 📈 Activity & Search Trends")
fig_activity = create_activity_chart(data["questions_by_day"], data["searches_by_day"])
if fig_activity:
    st.plotly_chart(fig_activity, use_container_width=True)
else:
    st.info("No activity logged yet. Submit queries or searches to view trends.")

# User ranking bar chart
st.markdown("### 🏆 User Engagement")
fig_users = create_user_activity_chart(data["user_activity"])
if fig_users:
    st.plotly_chart(fig_users, use_container_width=True)
else:
    st.info("No query logs registered to rank user activity.")
