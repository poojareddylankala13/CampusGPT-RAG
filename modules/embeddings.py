import logging
import streamlit as st

# Safe import for Hugging Face embeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger("CampusGPT.embeddings")

@st.cache_resource
def get_embeddings():
    """Initializes and returns the HuggingFace embeddings model (BAAI/bge-small-en-v1.5).
    
    Uses st.cache_resource to load the model only once, sharing it across pages and sessions.
    """
    logger.info("Initializing BAAI/bge-small-en-v1.5 Embeddings...")
    model_name = "BAAI/bge-small-en-v1.5"
    
    # Configure BGE small settings (normalized embeddings are recommended for BGE cosine similarity)
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        logger.info("Embeddings model loaded successfully.")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embeddings model: {str(e)}")
        raise e
