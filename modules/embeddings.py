import logging
import streamlit as st

# Safe import for Hugging Face embeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger("CampusGPT.embeddings")

from modules.embedding_manager import get_cached_embedding_model

def get_embeddings():
    """Returns the cached BAAI/bge-small-en-v1.5 embeddings model.
    
    Provided for backward compatibility.
    """
    return get_cached_embedding_model("bge-small")
