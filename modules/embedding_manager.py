import hashlib
import json
import logging
import os
import sqlite3

import streamlit as st
from langchain_core.embeddings import Embeddings

# Safe import for Hugging Face embeddings
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger("CampusGPT.embedding_manager")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "cache", "embeddings")
CACHE_DB_PATH = os.path.join(CACHE_DIR, "embeddings_cache.db")

# Models Mapping
SUPPORTED_MODELS = {"bge-small": "BAAI/bge-small-en-v1.5", "minilm": "sentence-transformers/all-MiniLM-L6-v2"}


def init_cache_db() -> None:
    """Initializes the local embedding cache SQLite database."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS embedding_cache (
            text_hash TEXT NOT NULL,
            model_name TEXT NOT NULL,
            vector TEXT NOT NULL,
            PRIMARY KEY (text_hash, model_name)
        )
    """
    )
    conn.commit()
    conn.close()


# Initialize cache database on module load
init_cache_db()


@st.cache_resource
def get_cached_embedding_model(model_key: str) -> HuggingFaceEmbeddings:
    """Loads and caches the HuggingFace embeddings model locally.

    Args:
        model_key (str): 'bge-small' or 'minilm'.

    Returns:
        HuggingFaceEmbeddings: The initialized model.
    """
    model_name = SUPPORTED_MODELS.get(model_key, SUPPORTED_MODELS["bge-small"])
    logger.info(f"Loading embedding model: {model_name}...")

    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": True}

    try:
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
        )
        logger.info(f"Embedding model {model_key} loaded successfully.")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embedding model {model_name}: {str(e)}")
        raise e


def clear_embeddings_cache() -> bool:
    """Clears the SQLite cache database for embeddings."""
    if os.path.exists(CACHE_DB_PATH):
        try:
            conn = sqlite3.connect(CACHE_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM embedding_cache")
            conn.commit()
            conn.close()
            logger.info("Embeddings cache successfully cleared.")
            return True
        except Exception as e:
            logger.error(f"Error clearing embeddings cache: {e}")
            return False
    return True


# --- Local Cached Embeddings Wrapper ---


class CachedLocalEmbeddings(Embeddings):
    """A wrapper for LangChain Embeddings that checks and writes to an SQLite cache."""

    def __init__(self, model_key: str = "bge-small") -> None:
        self.model_key: str = model_key
        self.model_name: str = SUPPORTED_MODELS.get(model_key, SUPPORTED_MODELS["bge-small"])
        self.underlying_embeddings: HuggingFaceEmbeddings = get_cached_embedding_model(model_key)

    def _get_hash(self, text: str) -> str:
        """Returns the MD5 hash of a text string."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _lookup_cache(self, text_hash: str) -> list[float] | None:
        """Checks if the embedding for a hash and model exists in cache."""
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT vector FROM embedding_cache WHERE text_hash = ? AND model_name = ?", (text_hash, self.model_key)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            val: list[float] = json.loads(row[0])
            return val
        return None

    def _write_cache(self, text_hash: str, vector: list[float]) -> None:
        """Saves a generated embedding vector into the cache database."""
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO embedding_cache (text_hash, model_name, vector) VALUES (?, ?, ?)",
                (text_hash, self.model_key, json.dumps(vector)),
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to write cache entry: {e}")
        finally:
            conn.close()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generates embeddings for a batch of documents, utilizing the local SQLite cache."""
        embeddings: list[tuple[int, list[float]]] = []
        uncached_texts: list[str] = []
        uncached_indices: list[int] = []

        # 1. Lookup cached items
        for i, text in enumerate(texts):
            text_hash = self._get_hash(text)
            cached_vector = self._lookup_cache(text_hash)

            if cached_vector is not None:
                embeddings.append((i, cached_vector))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # 2. Compute uncached items
        if uncached_texts:
            logger.info(
                f"Computing local embeddings for {len(uncached_texts)} uncached chunks using {self.model_key}..."
            )
            uncached_vectors = self.underlying_embeddings.embed_documents(uncached_texts)

            # 3. Write uncached to cache and aggregate results
            for idx, vector in zip(uncached_indices, uncached_vectors):
                text_hash = self._get_hash(texts[idx])
                self._write_cache(text_hash, vector)
                embeddings.append((idx, vector))

        # Sort back to original order
        embeddings.sort(key=lambda x: x[0])
        return [vector for _, vector in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Generates embedding for a query, utilizing the local SQLite cache."""
        text_hash = self._get_hash(text)
        cached_vector = self._lookup_cache(text_hash)

        if cached_vector is not None:
            return cached_vector

        vector = self.underlying_embeddings.embed_query(text)
        self._write_cache(text_hash, vector)
        return vector
