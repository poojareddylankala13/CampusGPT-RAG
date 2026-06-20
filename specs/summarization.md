# Specification: Document Summarization

---

## 1. Purpose
Generates structured administrative summaries of uploaded university documents using cloud or local LLM models.

---

## 2. Functional Requirements
*   **Structured Outputs**: Compiles summaries under exact headings: Executive Summary, Key Highlights, Important Dates, Policies & Guidelines, and Action Items.
*   **Offline Support**: Prunes document text to the first 5000 characters to fit within the constraints of local model context windows.
*   **Streaming Support**: Streams local summaries token-by-token for responsive UI updates.

---

## 3. Inputs
*   `doc_name` (string): Display name of the target document.
*   `file_path` (string): Absolute path to the source PDF.

---

## 4. Outputs
*   Markdown formatted summary string, or error messages.

---

## 5. Dependencies
*   `pymupdf4llm` / pdf loader.
*   Google GenAI / local GGUF models.
*   Streamlit active session states.

---

## 6. Error Handling
*   If the PDF is empty or text extraction fails, return: `"❌ Could not extract text from the document. The PDF may be scanned or empty."`
*   If LLM configuration is missing, return friendly warnings like `"⚠️ Summarization Error: No local GGUF model is selected."`

---

## 7. Future Improvements
*   Implement map-reduce summary generation to support extremely long documents without context clipping.
*   Allow exporting summaries as PDF documents directly from the UI.
*   Add key-value metadata extraction (e.g. automatically extract version numbers and effective dates).
