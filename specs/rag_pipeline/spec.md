# Feature Spec: RAG Pipeline

## User Stories
- As a student, I want my questions to be answered using the uploaded university documents so that the answers are accurate and grounded.
- As a user, I want query execution to be cached so that repeated queries load instantly.

## Requirements
- [x] Requirement 1: Retrieve context chunks using similarity or MMR search from FAISS.
- [x] Requirement 2: Support similarity threshold filtering.
- [x] Requirement 3: Support hybrid execution (Google Gemini Cloud API / Local GGUF models).
- [x] Requirement 4: Cache queries and context settings in an SQLite database.
- [x] Requirement 5: Log performance and query metrics for dashboard audit.

## Acceptance Criteria
- Given a query already cached, when a user asks it again with same settings, then return the response instantly from cache.
- Given a query with similarity score below threshold, when executed, then filter out the irrelevant chunks.
