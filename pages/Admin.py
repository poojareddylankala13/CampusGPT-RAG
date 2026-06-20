import io
import os
import time
import zipfile

import streamlit as st

from modules.auth import check_auth
from modules.database import delete_document, delete_user, list_documents, list_users
from modules.ui import inject_custom_css, render_sidebar
from modules.vector_store import rebuild_faiss_index

# 1. Auth Guard (check if logged in)
check_auth()

# 2. Admin Role Guard
if st.session_state.get("user_role") != "admin":
    st.markdown(
        """
        <style>
        .admin-denied-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 45px;
            background-color: rgba(220, 53, 69, 0.08);
            border: 1px solid rgba(220, 53, 69, 0.2);
            border-radius: 12px;
            text-align: center;
            margin-top: 50px;
        }
        .admin-denied-title {
            color: #dc3545;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 15px;
        }
        </style>
        <div class="admin-denied-container">
            <div class="admin-denied-title">⛔ Unauthorized Access</div>
            <p style="color: #6c757d; font-size: 16px;">Only administrators are authorized to access this panel.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.stop()

# 3. Setup styling and sidebar
inject_custom_css()
render_sidebar()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ZIP export logic
def package_source_code_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(BASE_DIR):
            # Skip heavy runtime folders, indices, database files, and caches
            if any(part in root for part in ["data", "database", "logs", "__pycache__", ".git", ".venv"]):
                continue

            for file in files:
                # Exclude runtime-generated files
                if file.endswith((".db", ".log", ".pyc")):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                zip_file.write(file_path, rel_path)

    return zip_buffer.getvalue()


st.markdown("<h1 class='gradient-header'>⚙️ Administrative Control Panel</h1>", unsafe_allow_html=True)
st.markdown("Manage system resources, monitor accounts, maintain vector stores, and extract package bundles.")

# 4. Tab layouts
tab_docs, tab_users, tab_index, tab_export = st.tabs(
    ["📄 Manage Documents", "👥 Manage Users", "🔀 Vector Store Maintenance", "📦 Export Source Code"]
)

# --- Tab 1: Manage Documents ---
with tab_docs:
    st.markdown("### Document Index Management")
    docs = list_documents()

    if docs:
        for doc in docs:
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"""
                    **{doc['name']}**
                    *Pages*: {doc['page_count']} | *Chunks*: {doc['chunk_count']} | *Uploaded By*: {doc['uploaded_by_name'] or 'System'} | *Date*: {doc['upload_date']}
                """
                )
            with col_del:
                if st.button("🗑️ Delete", key=f"del_doc_{doc['id']}", use_container_width=True):
                    with st.spinner("Deleting document and rebuilding FAISS..."):
                        # Get details and remove from database
                        doc_rec = delete_document(doc["id"])

                        # Remove physical file from disk
                        if doc_rec and os.path.exists(doc_rec["file_path"]):
                            try:
                                os.remove(doc_rec["file_path"])
                            except Exception as e:
                                st.error(f"Failed to delete file from disk: {e}")

                        # Rebuild FAISS index
                        rebuild_faiss_index()

                        st.success(f"Deleted `{doc['name']}`. FAISS index rebuilt.")
                        time.sleep(1)
                        st.rerun()
            st.markdown("---")
    else:
        st.info("No documents are currently registered.")

# --- Tab 2: Manage Users ---
with tab_users:
    st.markdown("### User Account Management")
    users = list_users()

    for u in users:
        col_info, col_del = st.columns([5, 1])
        with col_info:
            st.markdown(
                f"""
                👤 **{u['name']}** ({u['email']})
                *Role*: `{u['role'].upper()}` | *Created*: {u['created_at']}
            """
            )
        with col_del:
            # Disable deleting oneself or deleting another admin for security
            if u["id"] == st.session_state.user_id:
                st.button("Current User", disabled=True, key=f"del_user_self_{u['id']}", use_container_width=True)
            elif u["role"] == "admin":
                st.button("Admin Acc", disabled=True, key=f"del_user_admin_{u['id']}", use_container_width=True)
            else:
                if st.button("🗑️ Delete", key=f"del_user_{u['id']}", use_container_width=True):
                    delete_user(u["id"])
                    st.success(f"Deleted user account: {u['email']}")
                    time.sleep(1)
                    st.rerun()
        st.markdown("---")

# --- Tab 3: Vector Store Maintenance ---
with tab_index:
    st.markdown("### FAISS Vector Index Maintenance")
    st.warning(
        "⚠️ Rebuilding the index reads all files in data/uploads/ and re-embeds them using BAAI/bge-small-en-v1.5. This can take some time if there are many pages."
    )

    if st.button("🔄 Trigger FAISS Rebuild", use_container_width=True):
        with st.spinner("Processing documents and generating fresh embeddings..."):
            success = rebuild_faiss_index()
            if success:
                st.success("FAISS index has been successfully rebuilt!")
            else:
                st.error("Failed to rebuild the FAISS index. Check application logs.")

# --- Tab 4: Export Source Code ---
with tab_export:
    st.markdown("### Package Codebase")
    st.write("Click below to compile all Python modules, pages, assets, and documentation into a single zip folder.")

    try:
        zip_bytes = package_source_code_zip()
        st.download_button(
            label="📥 Download CampusGPT.zip",
            data=zip_bytes,
            file_name="CampusGPT.zip",
            mime="application/zip",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Failed to generate codebase zip file: {e}")
