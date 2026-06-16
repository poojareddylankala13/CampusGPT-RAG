import streamlit as st
import os
import time
from datetime import datetime

from modules.auth import check_auth
from modules.ui import inject_custom_css, render_sidebar
from modules.database import list_documents, add_document, get_document_by_name
from modules.pdf_loader import validate_and_load_pdf
from modules.chunking import split_documents
from modules.vector_store import add_chunks_to_store

# 1. Auth Guard
check_auth()

# 2. Page Setup
inject_custom_css()
render_sidebar()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'data', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.markdown("<h1 class='gradient-header'>📂 Document Upload Module</h1>", unsafe_allow_html=True)
st.markdown("Upload official university PDF guidelines, calendars, and syllabus documents to feed the AI Knowledge Assistant.")

# 3. File Uploader Component
uploaded_files = st.file_uploader(
    "Select one or more PDF documents", 
    type=["pdf"], 
    accept_multiple_files=True,
    help="Upload official PDF documents (maximum 20MB per file)."
)

if uploaded_files:
    if st.button("🚀 Process & Index Documents", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_files = len(uploaded_files)
        success_count = 0
        
        for idx, uploaded_file in enumerate(uploaded_files):
            file_name = uploaded_file.name
            status_text.markdown(f"**Processing ({idx + 1}/{total_files}):** `{file_name}`...")
            
            # Save file to uploads folder
            file_path = os.path.join(UPLOAD_DIR, file_name)
            
            try:
                # Write file out
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Check if document already registered in SQLite
                existing_doc = get_document_by_name(file_name)
                if existing_doc:
                    st.warning(f"⚠️ Document `{file_name}` is already indexed. Re-processing will append details.")
                
                # Step 1: Load and parse PDF
                pages = validate_and_load_pdf(file_path)
                page_count = len(pages)
                
                # Step 2: Split text into chunks
                # Requirements: chunk_size=1000, chunk_overlap=200
                chunks = split_documents(pages, chunk_size=1000, chunk_overlap=200)
                chunk_count = len(chunks)
                
                # Inject file name metadata into chunks so citations know the exact source document
                for chunk in chunks:
                    chunk.metadata['source'] = file_name
                
                # Step 3: Embed and add to FAISS
                status_text.markdown(f"**Indexing chunks in FAISS ({idx + 1}/{total_files}):** `{file_name}`...")
                indexing_success = add_chunks_to_store(chunks)
                
                if not indexing_success:
                    raise Exception("Failed to save embeddings in FAISS index.")
                
                # Step 4: Register in SQLite database
                file_size = os.path.getsize(file_path)
                uploaded_by = st.session_state.user_id
                
                doc_id = add_document(
                    name=file_name,
                    file_path=file_path,
                    page_count=page_count,
                    file_size=file_size,
                    chunk_count=chunk_count,
                    uploaded_by=uploaded_by
                )
                
                if doc_id:
                    success_count += 1
                else:
                    st.warning(f"Indexed `{file_name}` but failed to write record to SQLite (duplicate entry?).")
                    
            except Exception as e:
                st.error(f"❌ Error processing `{file_name}`: {str(e)}")
                # Remove file if parsing failed to clean up disk
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                        
            # Update progress bar
            progress_bar.progress((idx + 1) / total_files)
            
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        if success_count > 0:
            st.success(f"🎉 Successfully parsed, indexed, and saved {success_count}/{total_files} documents!")
            time.sleep(1)
            st.rerun()

# 4. Display list of indexed documents
st.markdown("---")
st.markdown("### 📋 Currently Indexed Documents")

docs = list_documents()

if docs:
    # Convert database rows to formatted pandas DataFrame for interactive rendering
    table_data = []
    for doc in docs:
        # Format file size (e.g. KB, MB)
        size_bytes = doc['file_size']
        if size_bytes > 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / 1024:.2f} KB"
            
        table_data.append({
            "Document Name": doc['name'],
            "Upload Date": doc['upload_date'],
            "Pages": doc['page_count'],
            "Chunks": doc['chunk_count'],
            "File Size": size_str,
            "Uploaded By": doc['uploaded_by_name'] or "System"
        })
        
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No documents have been indexed yet. Upload and process a PDF file to begin.")
