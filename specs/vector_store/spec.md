# Feature Spec: Vector Store

## User Stories
- As an administrator, I want to store document vectors in partitioned directories so that different embedding models do not cause dimension mismatches.
- As a user, I want the system to dynamically load the vector database on demand so that search is responsive.

## Requirements
- [x] Requirement 1: Directory partitioning for multi-model FAISS vector stores.
- [x] Requirement 2: Incremental document additions and serialization to disk.
- [x] Requirement 3: Support full index rebuilding from SQLite metadata.

## Acceptance Criteria
- Given FAISS index files on disk, when loaded, then allow querying them with the corresponding embedding model.
- Given new document chunks, when indexed, then save them persistently to their model-specific folder.
