import logging

from modules.embedding_manager import get_cached_embedding_model

logger = logging.getLogger("CampusGPT.embeddings")


def get_embeddings():
    """Returns the cached BAAI/bge-small-en-v1.5 embeddings model.

    Provided for backward compatibility.
    """
    return get_cached_embedding_model("bge-small")
