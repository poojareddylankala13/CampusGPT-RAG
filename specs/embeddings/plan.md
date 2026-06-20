# Technical Plan: Embeddings

## Architecture & Integration
- Embeddings loading, calculation, and cache orchestration are located in `modules/embedding_manager.py`.
- Integrates with SQLite cache located under `cache/embeddings/` via raw SQL operations.

## Proposed Changes
- [MODIFY] `modules/embedding_manager.py` to support fallback embeddings execution and lazy initialization.

## Security & Type Safety Checks
- Explicit type annotations for parameter lists and return values.
- Verify hashing integrity with hashlib MD5 checks.
