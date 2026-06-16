import os
import logging
from langchain_community.vectorstores import FAISS
from modules.embeddings import get_embeddings
from modules.pdf_loader import validate_and_load_pdf
from modules.chunking import split_documents
from modules.database import list_documents

logger = logging.getLogger("CampusGPT.vector_store")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR = os.path.join(BASE_DIR, 'data', 'faiss_index')
INDEX_NAME = "campus_index"

def get_index_path():
    """Returns the absolute path to the FAISS index folder."""
    return os.path.join(INDEX_DIR, INDEX_NAME)

def load_vector_store():
    """Loads the persisted FAISS vector index.
    
    Returns:
        FAISS: Loaded FAISS vector store, or None if index doesn't exist.
    """
    path = get_index_path()
    # FAISS writes multiple files (e.g. index.faiss, index.pkl)
    if not os.path.exists(path) and not os.path.exists(f"{path}.faiss"):
        logger.warning(f"FAISS index not found at {path}")
        return None
    
    try:
        embeddings = get_embeddings()
        logger.info(f"Loading FAISS index from {INDEX_DIR}...")
        vector_store = FAISS.load_local(
            folder_path=INDEX_DIR,
            embeddings=embeddings,
            index_name=INDEX_NAME,
            allow_dangerous_deserialization=True
        )
        return vector_store
    except Exception as e:
        logger.error(f"Error loading FAISS index: {str(e)}")
        return None

def save_vector_store(vector_store):
    """Persists the FAISS vector index to disk."""
    os.makedirs(INDEX_DIR, exist_ok=True)
    path = get_index_path()
    try:
        logger.info(f"Saving FAISS index to {INDEX_DIR}...")
        vector_store.save_local(folder_path=INDEX_DIR, index_name=INDEX_NAME)
        logger.info("FAISS index saved successfully.")
        return True
    except Exception as e:
        logger.error(f"Error saving FAISS index: {str(e)}")
        return False

def add_chunks_to_store(chunks):
    """Appends new document chunks to the FAISS index, or creates a new index if none exists."""
    if not chunks:
        return False
        
    embeddings = get_embeddings()
    vector_store = load_vector_store()
    
    try:
        if vector_store is None:
            logger.info("Creating new FAISS index...")
            vector_store = FAISS.from_documents(chunks, embeddings)
        else:
            logger.info(f"Adding {len(chunks)} chunks to existing FAISS index...")
            vector_store.add_documents(chunks)
            
        return save_vector_store(vector_store)
    except Exception as e:
        logger.error(f"Error adding chunks to FAISS store: {str(e)}")
        return False

def rebuild_faiss_index():
    """Rebuilds the FAISS index from scratch using all documents registered in the database.
    
    This ensures the FAISS index matches the documents in the SQLite database (e.g. after deletion).
    """
    logger.info("Starting manual/automatic FAISS index rebuild...")
    
    # Clean up index directory first
    path = get_index_path()
    for ext in ['.faiss', '.pkl']:
        file_path = f"{path}{ext}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Could not remove old index file {file_path}: {e}")

    # Fetch all document records from SQLite
    db_docs = list_documents()
    if not db_docs:
        logger.info("No documents registered in the database. Index cleared.")
        return True

    all_chunks = []
    for doc in db_docs:
        file_path = doc['file_path']
        if os.path.exists(file_path):
            try:
                logger.info(f"Re-parsing {doc['name']} for rebuild...")
                pages = validate_and_load_pdf(file_path)
                chunks = split_documents(pages)
                
                # Make sure metadata is correctly tagged for each chunk
                for chunk in chunks:
                    chunk.metadata['source'] = doc['name']
                    # page number starts at 1 in pdf_loader
                    if 'page' not in chunk.metadata:
                        chunk.metadata['page'] = 1
                
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to process {doc['name']} during rebuild: {e}")
        else:
            logger.warning(f"File {file_path} registered in database but missing from disk.")

    if all_chunks:
        embeddings = get_embeddings()
        try:
            logger.info(f"Creating brand new FAISS index with {len(all_chunks)} chunks...")
            vector_store = FAISS.from_documents(all_chunks, embeddings)
            return save_vector_store(vector_store)
        except Exception as e:
            logger.error(f"Failed to create FAISS index during rebuild: {e}")
            return False
            
    return True
