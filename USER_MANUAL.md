# CampusGPT User Manual

CampusGPT is an intelligent assistant designed to help university members navigate academic handbooks, guidelines, schedules, and course policies using artificial intelligence. 

This manual provides detailed guidelines on using and administering CampusGPT.

---

## 🧭 Interface Navigation

The interface is built using Streamlit and features a sidebar navigation layout:
- **👋 Dashboard**: Initial workspace with welcome text, feature summaries, and quick navigation modules.
- **💬 Chat**: The main Retrieval-Augmented Generation interface.
- **📄 Upload**: The ingestion portal for uploading PDF guidelines.
- **📝 Summarize**: A utility to generate executive summaries and action items.
- **📊 Analytics**: A dashboard showing performance statistics and database records.
- **🔍 Search**: A pure vector similarity search tool to retrieve document chunks.
- **⚙️ Administrative Control Panel**: Restricted dashboard (Admin role only) to manage uploaded documents, user registrations, vector indexes, and exports.

---

## 🔐 Sign In & Registration

When launching the application for the first time, you will see a login layout:
1. **Create Account**:
   - Provide your full name, university email address, and password.
   - Click "Register Account".
2. **Sign In**:
   - Enter your registered email address and password.
   - If no Gemini API Key is stored in the environment `.env`, you can type an optional API key in the login screen for the duration of your session.

*Note: Default administrator accounts can be pre-seeded in the database on startup using environment variables (`ADMIN_EMAIL`, `ADMIN_PASSWORD`).*

---

## 📄 Ingesting Documents (Upload)

To insert academic handbooks or syllabi into the semantic retrieval index:
1. Navigate to the **Upload** page in the sidebar.
2. Select a PDF file from your local machine.
3. Click "Upload & Process".
4. The system will:
   - Extract the pages layout-aware using `pymupdf4llm`.
   - Fragment the text into overlapping tokens.
   - Run embedding computations locally (caching them to prevent CPU overload).
   - Save the vectors in the partitioned FAISS vector database.

---

## 💬 Retrieval-Augmented Chat (RAG)

Use the **Chat** page to ask questions about university procedures (e.g. "What is the condonation limit for exams?"):
1. **Query Options**:
   - **AI Mode**: Select `Gemini` (requires cloud API key) or `Local` (runs offline using GGUF models stored in `models/`).
   - **Retrieval Method**: Standard `similarity` or `MMR` (Maximum Marginal Relevance, to ensure diversity in results).
   - **Top K**: The number of relevant chunks retrieved to contextually prompt the LLM.
   - **Similarity Threshold**: Min score to filter out irrelevant text.
2. **Citations list**:
   - The RAG system displays the answer along with matching citations. 
   - Click the citation expandable dropdowns to view the original page contents, matching page number, and similarity confidence score.

---

## 📝 Document Summarizer

Generate concise breakdowns of long academic guides:
1. Navigate to the **Summarize** page.
2. Choose a previously uploaded document.
3. Click "Generate Summary".
4. View the structured output:
   - **📋 Executive Summary**: Brief overview of the handbook.
   - **✅ Action Items**: Task list for students and admins.
   - **📅 Key Dates and Deadlines**: Extracted scheduling milestones.
5. Export: Click "📥 Download Summary PDF" to save the summary on your computer.

---

## ⚙️ Administrative Control Panel

Accessible only to accounts registered under the `admin` role:
- **Manage Documents**: Lists all indexed PDFs. Click "Delete" to wipe a document from SQLite database records and automatically update the FAISS vector indices.
- **Manage Users**: View active users and registration dates.
- **Vector Store Maintenance**: Manually trigger a rebuild of all vectors from raw uploads in the directory.
- **Export Source Code**: Compiles a submission zip archive bundle (`CampusGPT.zip`) excluding caches and binaries.
