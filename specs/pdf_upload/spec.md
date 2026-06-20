# Feature Spec: PDF Upload

## User Stories
- As an admin or authorized user, I want to upload university PDFs so that the system can parse and index their contents.
- As a user, I want the system to preserve document structure (tables and headings) during parsing so that retrieved context is high quality.

## Requirements
- [x] Requirement 1: PDF validation and ingestion.
- [x] Requirement 2: Layout-aware text/markdown extraction using `pymupdf4llm`.
- [x] Requirement 3: Document chunking and page-tagging metadata injection.
- [x] Requirement 4: Save metadata records in the SQLite database.

## Acceptance Criteria
- Given a valid PDF file, when uploaded, then successfully parse, chunk, and index the document, and register it in SQLite.
- Given an invalid file type (non-PDF), when uploaded, then display a validation warning and reject it.
