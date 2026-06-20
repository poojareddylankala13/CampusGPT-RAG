# CampusGPT Feature Verification Checklist

This checklist documents the critical functional requirements of the CampusGPT RAG system and provides specific verification criteria for each component.

---

## 1. User Authentication & Authorization
*   **Sign-Up / Registration**
    *   [ ] Users can register with a name, unique email, and password.
    *   [ ] Passwords are automatically salted and hashed using `bcrypt` before storage.
    *   [ ] Input validation prevents registration of duplicate emails.
*   **Login & Session Guard**
    *   [ ] Authenticated users receive a signed session state.
    *   [ ] Unauthorized access to pages automatically redirects to the login screen.
*   **Role-Based Access Control (RBAC)**
    *   [ ] Regular users only have access to Search, Chat, Summarize, and Analytics.
    *   [ ] Administrators have access to the Admin panel to view user lists and delete uploaded documents.

---

## 2. Document Ingestion & Parser
*   **PyMuPDF4LLM Integration**
    *   [ ] PDF text is extracted as clean markdown rather than unformatted plain text.
    *   [ ] Section headings and structural elements are preserved.
    *   [ ] Page numbers and file names are tagged onto each chunk's metadata for proper citation sourcing.
*   **Recursive Chunking**
    *   [ ] Uploaded files are split using recursive character text splitters.
    *   [ ] Target parameters: `chunk_size = 1000` characters, `chunk_overlap = 200` characters.
*   **SQLite Document Registration**
    *   [ ] Successfully parsed documents are registered in the SQLite `documents` table with page counts, file sizes, and chunk counts.

---

## 3. Embedding Space & Caching
*   **Embedding Models**
    *   [ ] Supports BAAI/bge-small-en-v1.5 and sentence-transformers/all-MiniLM-L6-v2.
    *   [ ] Embedding execution falls back to CPU cleanly.
*   **Embedding SQLite Cache**
    *   [ ] Embedded text chunks are MD5-hashed and stored in `embedding_cache` database.
    *   [ ] Subsequent embedding calls for identical text chunks retrieve vectors from the cache, avoiding duplicate CPU computations.

---

## 4. FAISS Vector Database
*   **Index Partitioning**
    *   [ ] Vector indices are saved in model-specific subdirectories (e.g. `data/faiss_index/bge-small/`).
    *   [ ] FAISS indexes are serialized/deserialized with `allow_dangerous_deserialization=True` safely.
*   **Dynamic Rebuild**
    *   [ ] Administrators can trigger a database rebuild, which re-parses all registered PDFs and recreates the FAISS index from scratch.

---

## 5. Offline Local LLM (Optional / Hybrid)
*   **Graceful Degradation**
    *   [ ] System checks if `llama-cpp-python` is compiled. If missing, GGUF options degrade gracefully without crashing.
*   **GGUF Model Directory Scan**
    *   [ ] Scanning the `models/` directory dynamically populates installed GGUF models.
    *   [ ] Memory heuristics estimate RAM requirements based on file size.
*   **Local Token Streaming**
    *   [ ] Local model output is generated token-by-token using generator streams for low latency user interfaces.

---

## 6. Unified RAG Execution Pipeline
*   **Routing Logic**
    *   [ ] Queries are routed to either Gemini API or the selected offline GGUF model based on settings.
*   **Retrieval Methods**
    *   [ ] Supports standard Cosine Similarity Search.
    *   [ ] Supports Max Marginal Relevance (MMR) search.
*   **Similarity Threshold**
    *   [ ] Documents below the similarity score threshold are dynamically filtered out.
*   **RAG Query Cache**
    *   [ ] The exact answers for identical queries/settings combinations are cached to disk under `cache/queries/` to eliminate duplicate model API costs.
*   **Performance Metrics Tracking**
    *   [ ] RAG query metrics (retrieval time, generation time, chunk count, avg similarity, context length) are written into the SQLite `rag_evaluations` table for analytics reporting.
