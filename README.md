# CampusGPT – AI-Powered University Knowledge Assistant

**CampusGPT** is a complete, production-ready Retrieval-Augmented Generation (RAG) application designed to help students, faculty, and university staff interact with university documentation through an AI-powered chat interface. 

Users can upload official university PDF documents (such as academic calendars, student handbooks, syllabi, and recruitment policies), search them semantically, query them using natural language, and retrieve responses grounded in retrieved context with source citations.

---

## 🛠️ Tech Stack

*   **Frontend & Layout**: Streamlit (with custom HSL university-branded styling)
*   **Vector Search & Indexing**: FAISS (persisted locally)
*   **LLM Engine**: Gemini 2.5 Flash (via LangChain Google GenAI API)
*   **Embedding Model**: HuggingFace BAAI/bge-small-en-v1.5
*   **Relational Database**: SQLite (local schema storage)
*   **PDF Processing**: PyPDFLoader (LangChain Community)
*   **Password Cryptography**: Bcrypt (SHA-256 equivalent hashing)
*   **Analytics Graphing**: Plotly Express & Graph Objects

---

## 📂 Project Directory Structure

```
CampusGPT/
│
├── app.py                     # Entry point & authentication form
├── requirements.txt           # Python application dependencies
├── README.md                  # Set up and user guide
├── .env.example               # Template for environment settings
│
├── database/
│   └── campusgpt.db           # Auto-generated SQLite database
│
├── data/
│   ├── uploads/               # Store uploaded PDF files
│   └── faiss_index/           # Persistent FAISS database indexes
│
├── assets/
│   └── styles.css             # Injectable global CSS styling
│
├── modules/                   # Backend modules & business logic
│   ├── auth.py                # bcrypt hashing, user login & auth guards
│   ├── database.py            # sqlite queries, user & doc schema, metrics
│   ├── pdf_loader.py          # PyPDFLoader wrappers with validations
│   ├── chunking.py            # RecursiveCharacterTextSplitter (1000/200)
│   ├── embeddings.py          # Cached HuggingFace BGE embeddings
│   ├── vector_store.py        # FAISS loading, saving, and index rebuilding
│   ├── retriever.py           # Similarity score computation (cosine conversions)
│   ├── rag_chain.py           # LangChain system prompt setup & Gemini executor
│   ├── summarizer.py          # Full-text document summary compiler via Gemini
│   ├── semantic_search.py     # Similarity querying and logging
│   ├── analytics.py           # Plotly graph formatter
│   └── feedback.py            # SQLite 👍/👎 feedback submissions helper
│
├── pages/                     # Streamlit multi-page dashboard views
│   ├── Dashboard.py           # Global system KPIs metric cards
│   ├── Chat.py                # Conversational RAG assistant with exports & rating
│   ├── Upload.py              # Drag-and-drop document upload and parsing logs
│   ├── Search.py              # Text similarity match tool with scoring
│   ├── Summarize.py           # Single-document key highlights and exports
│   ├── Analytics.py           # Charts monitoring searches, storage & feedback
│   └── Admin.py               # Manage files/users, rebuild indices, zip codebase
│
└── sample_documents/          # Auto-generated test PDFs
```

---

## 🚀 Quick Start & Installation

### 1. Clone or Extract the Project
Ensure the project structure is extracted into your working directory.

### 2. Install Python Dependencies
It is recommended to use a virtual environment:
```bash
python -m venv .venv
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Setup Configuration (`.env`)
Create a `.env` file in the root directory by copying the template:
```bash
copy .env.example .env
```
Open `.env` and fill in your Gemini API Key. You can get one for free at the [Google AI Studio](https://aistudio.google.com/).

```ini
GEMINI_API_KEY=AIzaSy...your_actual_key_here
ADMIN_EMAIL=admin@campusgpt.edu
ADMIN_PASSWORD=admin123
ADMIN_NAME=CampusGPT Admin
```

### 4. Create Sample Documents
Generate the professional university sample PDFs to use for indexing tests:
```bash
python create_samples.py
```
This will compile four university-style PDFs (Handbook, Calendar, Placement, Syllabus) under `sample_documents/`.

### 5. Launch CampusGPT
Start the Streamlit application:
```bash
streamlit run app.py
```

The application will launch in your browser (typically at `http://localhost:8501`).

---

## 🔑 Default Credentials

On database initialization, the system seeds a default admin account. You can log in using:
*   **Email**: `admin@campusgpt.edu`
*   **Password**: `admin123`

You can register new standard accounts via the registration form on the login portal. Standard accounts can access all features except for the **Admin Panel**.

---

## 💡 Important Design Notes

1.  **Index Rebuild on Deletion**: Since vector indexing relies on static distance matching, deleting a document from the system in the **Admin Panel** triggers a silent background FAISS rebuild from all remaining document files on disk. This guarantees search integrity.
2.  **Cosine Similarity Conversion**: HuggingFace BGE models perform best with normalized vectors. FAISS returns L2 distances. We map these distances using $\text{Similarity} = 1 - \frac{\text{L2\_Distance}^2}{2}$ to display accurate, human-readable match percentages.
3.  **LLM Temperature**: System prompts are structured with a low temperature (`0.1`) to ensure factual compliance and eliminate hallucinations. If a question is not found in the documents, the model yields: *"I'm sorry, but I couldn't find the answer to your question in the uploaded university documents."*
