# Specification: Embedding Space and Vector Cache

---

## 1. Purpose
Manages Hugging Face local embeddings model execution and provides an SQLite-based vector caching layer to avoid duplicate CPU computations.

---

## 2. Functional Requirements
*   **Model Loading**: Lazy load and cache Hugging Face embedding models (`BAAI/bge-small-en-v1.5` or `sentence-transformers/all-MiniLM-L6-v2`) in memory using Streamlit resource caching.
*   **CPU Optimization**: Restrict embeddings execution to CPU safely.
*   **SQLite Caching**:
    *   Compare MD5 hashes of incoming text chunks with cached records.
    *   If found in cache, return cached vectors.
    *   If missing, compute vectors using Hugging Face and insert them into the SQLite `embedding_cache` database.

---

## 3. Inputs
*   `texts` (list of strings): Document chunks or user search queries.

---

## 4. Outputs
*   List of lists of floats (computed or cached embedding vectors matching the input texts).

---

## 5. Dependencies
*   LangChain HuggingFace integration (`HuggingFaceEmbeddings`).
*   SQLite databases (`cache/embeddings/embeddings_cache.db`).
*   `hashlib` and `json` libraries.

---

## 6. Error Handling
*   If models fail to download or load, raise helpful exceptions.
*   If SQLite cache reads fail, degrade gracefully to live calculation without interrupting the parsing workflow.

---

## 7. Future Improvements
*   Add multi-threading support for batch embedding computations.
*   Support GPU acceleration (CUDA/MPS) if hardware modules are present.
*   Implement quantization (e.g. FP16/INT8) to reduce model memory footprints.
