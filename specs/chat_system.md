# Specification: Conversational Chat System

---

## 1. Purpose
Provides an interactive chat interface for users to run consecutive context-grounded queries, view retrieved document citations, leave helpfulness feedback, and export chat transcripts.

---

## 2. Functional Requirements
*   **Message Stream**: Render user and assistant chat bubbles chronologically in a conversational thread.
*   **Chat History**: Load and display previous chat entries from SQLite upon application load.
*   **Source Citations**: Render expandable sections beneath AI replies showing document names, 1-indexed pages, matching similarity scores, and context snippet previews.
*   **Feedback loops**: Allow users to rank the last AI response with thumbs up / thumbs down ratings.
*   **Transcripts Export**: Support compiling active conversations into download buttons as formatted PDF files or CSV data sheets.

---

## 3. Inputs
*   **Message input**: `user_query` (string) entered via Streamlit chat input.
*   **Feedback input**: `chat_id` (int), `user_id` (int), `rating` (string: `"helpful"` or `"not_helpful"`), optional `comments` (string).
*   **Transcript generation**: List of chat dictionary logs from SQLite.

---

## 4. Outputs
*   **Generation**: Streams token chunks to Streamlit UI in real-time.
*   **Feedback**: Inserts rating record into SQLite `feedback` table.
*   **Transcript**: Binary file stream (PDF/CSV) download triggers.

---

## 5. Dependencies
*   Streamlit UI library.
*   SQLite databases (`database/campusgpt.db`).
*   `fpdf2` for PDF transcription compilation.
*   `pandas` for CSV serialization.

---

## 6. Error Handling
*   If PDF compilation fails, display user-friendly warnings without truncating active chat screens.
*   If database logs fail, log errors to console and degrade gracefully to session-only storage.

---

## 7. Future Improvements
*   Add multi-conversation thread tracking (similar to ChatGPT sidebar history).
*   Implement speech-to-text voice questions.
*   Introduce smart citation overlays (clicking on references highlights text in source PDF previews).
