# Technical Plan: Semantic Campus Search

## Architecture & Integration
- Search panel interface located in `pages/5_Search.py`.
- Retrieval logic utilizing `modules/retriever.py` and `modules/vector_store.py`.

## Proposed Changes
- [MODIFY] `pages/5_Search.py` to accept user keywords, trigger retrievals, and render formatted cards.
- [MODIFY] `modules/retriever.py` to calculate cosine similarity conversions.

## Security & Type Safety Checks
- Strictly enforce parameter type declarations on retrieval helper arguments.
