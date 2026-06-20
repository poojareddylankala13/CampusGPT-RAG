import streamlit as st

from modules.auth import check_auth
from modules.semantic_search import perform_semantic_search
from modules.ui import inject_custom_css, render_sidebar

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()

st.markdown("<h1 class='gradient-header'>🔍 Semantic Similarity Search</h1>", unsafe_allow_html=True)
st.markdown("Locate exact sentences or clauses within university documents using AI-powered semantic search.")

# 3. Search Inputs
user_id = st.session_state.user_id

col_query, col_btn = st.columns([5, 1])

with col_query:
    search_query = st.text_input(
        "Enter keywords, phrases, or specific questions:", placeholder="e.g., Attendance condonation guidelines"
    )

# Advanced filters in expander
with st.expander("🛠️ Search Options & Filters"):
    col_k, col_thresh = st.columns(2)
    with col_k:
        top_k = st.slider(
            "Number of results to retrieve (k)", min_value=1, max_value=15, value=st.session_state.get("top_k", 5)
        )
    with col_thresh:
        threshold = st.slider(
            "Minimum similarity match (%)",
            min_value=0,
            max_value=100,
            value=int(st.session_state.get("threshold", 0.6) * 100),
            step=5,
        )

# Execute Search
if search_query:
    with st.spinner("Searching vector index..."):
        results = perform_semantic_search(user_id, search_query, k=top_k)

        # Filter by threshold
        thresh_decimal = threshold / 100.0
        filtered_results = [r for r in results if r["score"] >= thresh_decimal]

        st.markdown(f'### 🎯 Results for: *"{search_query}"*')

        if not filtered_results:
            st.warning(
                "No matches found meeting the minimum similarity threshold. Try lowering the threshold or changing your keywords."
            )
        else:
            st.write(f"Showing {len(filtered_results)} matching chunks out of {len(results)} retrieved:")

            for idx, match in enumerate(filtered_results):
                source_doc = match["metadata"].get("source", "Unknown Document")
                # 1-indexed page conversion
                page_num = match["metadata"].get("page", 0)
                display_page = page_num + 1 if isinstance(page_num, int) else page_num

                score_pct = match["score"] * 100

                # Render matching chunk card
                st.markdown(
                    f"""
                    <div style="background-color: rgba(255, 255, 255, 0.9); padding: 18px; border: 1px solid rgba(27, 54, 93, 0.1); border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 10px;">
                            <span style="font-weight: 700; color: #1b365d; font-size: 14px;">Match #{idx + 1}</span>
                            <div>
                                <span style="background-color: rgba(27, 54, 93, 0.08); padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; color: #1b365d; margin-right: 5px;">
                                    📄 {source_doc} (Page {display_page})
                                </span>
                                <span style="background-color: rgba(46, 196, 182, 0.15); padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 700; color: #197269;">
                                    🎯 {score_pct:.1f}% Match
                                </span>
                            </div>
                        </div>
                        <div style="font-size: 14px; line-height: 1.6; color: #444; background-color: #fafafa; padding: 12px; border-radius: 6px; border-left: 3px solid #c5a059; white-space: pre-wrap;">{match["content"]}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
else:
    st.info("Please enter a search phrase above and press Enter.")
