# Technical Plan: PDF Upload

## Architecture & Integration
- Upload interface located in `pages/2_Upload.py`.
- Temporary storage management and loading methods in `modules/pdf_loader.py`.
- Chunking logic located in `modules/chunking.py`.
- Ingestion, parsing, and vector registration located in `modules/document_parser.py` and `modules/vector_store.py`.

## Proposed Changes
- [MODIFY] `modules/document_parser.py` to support layout-aware parsing and safe error rollbacks.
- [MODIFY] `pages/2_Upload.py` to display upload lists and manage actions.

## Security & Type Safety Checks
- Prevent directory traversal path vulnerabilities by sanitizing filenames using `os.path.basename`.
- Ensure strict type annotations for all PDF parser helpers.
