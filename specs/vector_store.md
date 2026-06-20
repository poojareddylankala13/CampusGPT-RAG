# Specification: FAISS Vector Database Management

---

## 1. Purpose
Provides index persistence and directory partitioning for multi-model FAISS vector stores, preventing dimension space mismatches.

---

## 2. Functional Requirements
*   **Directory Partitioning**: Save FAISS indexes in model-specific paths (e.g. `data/faiss_index/bge-small/` and `data/faiss_index/minilm/`).
*   **Dynamic Loading**: Load specific local FAISS index based on active Streamlit session variables.
*   **Incremental Additions**: Append newly uploaded document chunks to active indexes and save them to disk.
*   **Index Rebuilding**:
    *   Delete current model-specific files (`.faiss`, `.pkl`).
    *   Fetch all documents from SQLite, re-parse PDFs, and re-create FAISS index from scratch.

---

## 3. Inputs
*   `chunks` (list of Document objects): New chunks to index.
*   `vector_store` (FAISS instance): Vector store to serialize.

---

## 4. Outputs
*   Status boolean (`True` on successful persistence/loading, `False` on errors).
*   Loaded FAISS instance (or `None`).

---

## 5. Dependencies
*   LangChain community FAISS vector store.
*   `CachedLocalEmbeddings` wrapper.
*   SQLite metadata tables (to retrieve paths during rebuild).

---

## 6. Error Handling
*   Deserialization uses `allow_dangerous_deserialization=True` but is restricted to local path structures.
*   If files are missing or index loading fails, log warning metrics and return `None` to allow index reconstruction.

---

## 7. Future Improvements
*   Implement auto-saving backups before index rebuilding.
*   Support remote vector databases (e.g. Pinecone, Qdrant, Chroma) for distributed setups.
*   Add metadata-based index filtering directly in FAISS.
