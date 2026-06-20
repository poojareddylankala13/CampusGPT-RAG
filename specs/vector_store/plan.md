# Technical Plan: Vector Store

## Architecture & Integration
- Core FAISS wrapper and directory logic located in `modules/vector_store.py`.
- Integrates with `modules/embedding_manager.py` for dimensions and distance calculations.

## Proposed Changes
- [MODIFY] `modules/vector_store.py` to manage directory validation, file deletion, and dangerous deserialization safety checks.

## Security & Type Safety Checks
- Parameter typing for FAISS initialization and search functions.
- Set `allow_dangerous_deserialization=True` but restrict paths strictly to the local workspace folder.
