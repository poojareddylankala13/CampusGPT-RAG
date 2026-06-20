# Technical Plan: RAG Pipeline

## Architecture & Integration
- RAG pipeline orchestrator located in `modules/rag_pipeline.py`.
- Integrates with `modules/vector_store.py` for retrieval.
- Routes generation calls to `modules/rag_chain.py` (Gemini API) or `modules/llm_local.py` (local GGUF models).
- Query caching and analytics log methods stored in `modules/database.py` and `modules/analytics.py`.

## Proposed Changes
- [MODIFY] `modules/rag_pipeline.py` to route queries, handle context thresholding, and implement SQLite caching.
- [MODIFY] `modules/rag_chain.py` to support Gemini execution prompts.

## Security & Type Safety Checks
- Strict type annotations for configurations and query inputs.
- Safe parsing of SQLite logs.
