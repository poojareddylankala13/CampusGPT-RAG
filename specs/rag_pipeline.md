# Specification: Unified RAG Execution Pipeline

---

## 1. Purpose
Orchestrates RAG retrieval, similarity filtering, model inference routing, performance metrics logging, and query caching.

---

## 2. Functional Requirements
*   **Retrieval Routing**: Query the active FAISS index based on chosen embedding spaces.
*   **Retrieval Methods**:
    *   *Similarity*: Cosine similarity nearest neighbors search.
    *   *MMR (Max Marginal Relevance)*: Maximizes relevance while minimizing redundancy.
*   **Threshold Filtering**: Filter out chunks with cosine similarity scores below the user-specified threshold.
*   **Inference Routing**:
    *   *Gemini*: Run queries via Google GenAI APIs.
    *   *Local Mode*: Route prompts to local GGUF models.
*   **Query Cache**: Hash configuration settings and queries; on match, return cached responses instantly without LLM calls.
*   **Evaluation Logs**: Audit execution metrics (retrieval times, generation times, chunks counts, similarity averages, context lengths) to SQLite.

---

## 3. Inputs
*   `query` (string): User's natural language question.
*   `settings` (dictionary): Settings containing `ai_mode`, `embedding_model`, `retrieval_method`, `top_k`, `threshold`, `active_gguf_model`, and `context_len`.

---

## 4. Outputs
*   Dictionary containing:
    *   `answer` (string): Grounded response or error fallback.
    *   `sources` (list of dictionaries): Citation metadata records.
    *   `retrieved_chunks` (list of Document objects): Source documents matching.
    *   `retrieval_time` (string formatted time).
    *   `generation_time` (string formatted time).

---

## 5. Dependencies
*   LangChain community FAISS vector store.
*   Google GenAI / LangChain Gemini integration.
*   Local Llama CPP bindings (if local execution is toggled).
*   SQLite cache and analytics tables.

---

## 6. Error Handling
*   If vector index is empty or missing, return friendly warning rather than raising runtime errors.
*   If LLM calls fail, return error messages (e.g. "❌ Gemini API Error...") and skip caching to allow retries.

---

## 7. Future Improvements
*   Implement hybrid search (combining dense vector retrieval with BM25 keyword matching).
*   Add auto-recovery retry mechanisms for rate-limited API calls (HTTP 429).
*   Integrate LLM-as-a-Judge evaluators to automatically compute faithfulness and relevance.
