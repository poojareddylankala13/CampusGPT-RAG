# Feature Spec: Embeddings

## User Stories
- As a user, I want the system to generate embeddings for my documents and queries so that semantic search works.
- As a system administrator, I want computed embeddings to be cached in SQLite so that system CPU load is minimized.

## Requirements
- [x] Requirement 1: Load SentenceTransformers embedding models locally.
- [x] Requirement 2: Compute vector representation for text strings.
- [x] Requirement 3: Cache computed embeddings in SQLite mapped by the MD5 hash of their text content.

## Acceptance Criteria
- Given a text, when its embedding is computed, then return the vector coordinates.
- Given a text already cached, when requested, then load the coordinates from SQLite database without executing the neural network model.
