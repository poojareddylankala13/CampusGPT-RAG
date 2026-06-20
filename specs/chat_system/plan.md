# Technical Plan: Chat System

## Architecture & Integration
- Chat interface located in `pages/1_Chat.py`.
- Integrates with `modules/rag_pipeline.py` for response generation and context retrieval.
- Logs chat records and ratings to SQLite via `modules/database.py`.

## Proposed Changes
- [MODIFY] `pages/1_Chat.py` to support real-time token streaming and formatted citation layout.
- [MODIFY] `modules/database.py` to create and update the `feedback` table.

## Security & Type Safety Checks
- Parameter typing for database write functions.
- Guard against SQL injection via parameterized SQLite queries.
