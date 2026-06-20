# Feature Spec: Semantic Campus Search

## User Stories
- As a student, I want to search for policy key phrases so that I can see the exact paragraphs in documents matching my query.
- As a user, I want search results to be sorted by relevance and formatted with score percentages.

## Requirements
- [x] Requirement 1: Retrieve matching document chunks from the active FAISS index.
- [x] Requirement 2: Convert L2 distance metrics to Cosine Similarity percentage values.
- [x] Requirement 3: Filter results using a minimum similarity threshold slider.
- [x] Requirement 4: Render search cards with document name, page number, similarity, and snippet.

## Acceptance Criteria
- Given a search query, when executed, then retrieve and render matching chunks that are above the chosen similarity threshold.
- Given a query with no matches above the threshold, when executed, then display a "No matches found" message.
