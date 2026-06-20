# Specification: PDF Document Ingestion and Upload

---

## 1. Purpose
Handles file uploading, PDF validation, layout-aware markdown extraction, recursive chunking, and index registrations.

---

## 2. Functional Requirements
*   **Upload Limit**: Streamlit file uploader validates PDF format and size limits.
*   **Markdown Extraction**: Custom parser reads PDFs page-by-page, converting paragraphs and tables into formatted Markdown.
*   **Page Tagging**: Tags source file names and 0-indexed page offsets onto chunk metadata records.
*   **SQLite Registration**: Records document details (page counts, chunk counts, upload date, file size, user IDs) in SQL tables.

---

## 3. Inputs
*   `uploaded_files` (list of file buffers): Uploaded PDF files.

---

## 4. Outputs
*   Returns confirmation dialogs and renders interactive pandas DataFrames of successfully registered documents.

---

## 5. Dependencies
*   Streamlit file uploader module.
*   `pymupdf4llm` & `fitz` parser libraries.
*   `RecursiveCharacterTextSplitter`.
*   SQLite relational database.

---

## 6. Error Handling
*   If PDF parsing fails, the upload transaction is rolled back and the temporary file is deleted to clean up disk space.
*   If a duplicate document name is uploaded, warn the user and append to the active indexing records.

---

## 7. Future Improvements
*   Add OCR support using Tesseract for scanned PDF documents.
*   Implement drag-and-drop folders uploads.
*   Add document versioning support to track updates to existing documents.
