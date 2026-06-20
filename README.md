# CampusGPT – Local-First AI-Powered University Knowledge Assistant

**CampusGPT** is a production-ready Retrieval-Augmented Generation (RAG) application that supports both cloud-based (Gemini API) and fully offline (Llama.cpp + Local Embeddings) document question answering. 

Users can upload official university PDF documents (such as academic calendars, student handbooks, syllabi, and recruitment policies), search them semantically, query them using natural language, and retrieve answers grounded in context with detailed source citations, similarity scores, and document previews.

---

## 🛠️ Tech Stack & local Architecture

*   **Frontend**: Streamlit (with HSL university-branded styling)
*   **Markdown Extraction**: `pymupdf4llm` (PyMuPDF) for clean table and structural parsing
*   **Vector Search & Indexing**: FAISS partitioned by embedding dimension space
*   **LLM Options**:
    *   *Cloud Mode*: Gemini 2.5 Flash (via LangChain Google GenAI API)
    *   *Local Mode*: GGUF Local Models via Llama.cpp (`llama-cpp-python`)
*   **Embedding Options**:
    *   *BGE Small*: `BAAI/bge-small-en-v1.5`
    *   *MiniLM*: `sentence-transformers/all-MiniLM-L6-v2`
*   **Relational Database**: SQLite (local schema storage)
*   **Performance Cache**:
    *   *Embedding Cache*: Local SQLite-based vector cache (`cache/embeddings/`)
    *   *Query Cache*: Hash-mapped JSON-based query response cache (`cache/queries/`)
*   **Analytics & Evaluation**: Plotly Express dashboards comparing latencies and feedback

---

## 📂 Project Directory Structure

```
CampusGPT/
│
├── app.py                     # Entry point & authentication form
├── requirements.txt           # Python application dependencies
├── README.md                  # Setup and operations guide
├── .env.example               # Template for environment settings
│
├── database/
│   └── campusgpt.db           # SQLite database (history, users, metrics)
│
├── models/                    # Store GGUF local model weight files
│   └── (e.g. qwen3.gguf)
│
├── data/
│   ├── uploads/               # Uploaded PDF files
│   └── faiss_index/
│       ├── bge-small/         # FAISS index for BGE-small embeddings
│       └── minilm/            # FAISS index for MiniLM embeddings
│
├── cache/
│   ├── embeddings/            # SQLite embedding vector cache db
│   └── queries/               # JSON query response cache logs
│
├── assets/
│   └── styles.css             # Injectable global CSS styling
│
├── modules/                   # Backend modules & business logic
│   ├── document_parser.py     # PyMuPDF4LLM markdown page parser
│   ├── embedding_manager.py   # Embedding loader and caching wrappers
│   ├── llm_local.py           # Llama-cpp loader, streaming generator
│   ├── rag_pipeline.py        # MMR/Similarity retrievals & query cache
│   ├── auth.py                # bcrypt hashing, user login & auth guards
│   ├── database.py            # sqlite queries, evaluations table
│   ├── pdf_loader.py          # Redirects loading to document_parser
│   ├── chunking.py            # Text splitter logic (1000/200)
│   ├── vector_store.py        # Model-partitioned FAISS index manager
│   ├── retriever.py           # Similarity score computation
│   ├── summarizer.py          # Cloud/Offline document summary compiler
│   ├── analytics.py           # Plotly dashboard formatter
│   └── feedback.py            # SQLite feedback registrar
│
└── pages/                     # Streamlit multi-page views
```

---

## 🚀 Local Installation & Offline Setup

### 1. Configure the Environment
Ensure Python 3.10 to 3.13 is installed, then set up your environment:
```bash
python -m venv .venv
# Activate:
.venv\Scripts\Activate.ps1   # Windows PowerShell
source .venv/bin/activate    # Linux/macOS

pip install -r requirements.txt
```

### 2. GGUF Model Setup
To use the fully local-first "Llama.cpp" mode, download a GGUF model and save it in the `models/` folder. We recommend:
*   **Qwen2.5 3B Instruct GGUF** (Highly Recommended for accuracy):
    *   Download [qwen2.5-3b-instruct-q4_k_m.gguf](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF) (~2.2 GB) and place it in the `models/` directory.
*   **Phi-4 Mini 3.8B GGUF**:
    *   Download [phi-4-mini-Q4_K_M.gguf](https://huggingface.co/bartowski/phi-4-mini-GGUF) (~2.4 GB) and place it in the `models/` directory.

### 3. Setting Up `llama-cpp-python` on Windows
The `requirements.txt` file installs `llama-cpp-python`. On Windows, if installing from source fails due to missing C++ compilers, you can install prebuilt wheels instead.
Open a terminal in your activated virtual environment and install a precompiled CPU-only wheel:
```bash
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
```
*(For Nvidia GPU hardware acceleration, configure CUDA compiler paths and build with CMake arguments as outlined in the [llama-cpp-python documentation](https://github.com/abetlen/llama-cpp-python)).*

### 4. Running the Application
Launch the app:
```bash
streamlit run app.py
```
*   Log in using the seeded default admin: `admin@campusgpt.edu` / `admin123`.
*   Go to **Settings** in the sidebar.
*   Switch **Active LLM Mode** to "Local Llama.cpp Mode".
*   Go to **Models** in the sidebar and choose your GGUF model file.

---

## ⚡ Performance Optimization Guide

1.  **Model Partitioning**: FAISS indexes are saved in directories by embedding model key. Switching from "BGE Small" to "MiniLM" dynamically routes the retrieval query to the correct vector database, avoiding dimensions mismatch errors.
2.  **Embedding Caching**: The embedding manager caches text chunk representations. When re-indexing or rebuilding, identical text chunks are skipped and fetched from cache, saving CPU resources.
3.  **Query Caching**: Turning on query caching stores generated results. The exact same question asked with the same parameters loads instantly, bypassing inference execution.
4.  **Local Context Management**: When querying local models, context text is pruned to fit within the model's GGUF context window (e.g. 2048 or 4096 tokens) to prevent out-of-memory issues.
5.  **Offline Summaries**: Summaries generated in Local mode slice the text to the first 5000 characters, enabling clean offline outlines without overloading local model buffers.

---

## 🛠️ Quality Control & Developer Tooling

CampusGPT includes strict code quality gates, automated testing, formatting, and type-checking checks.

### 1. Code Formatting (Black)
Auto-format the codebase to comply with standard PEP 8 requirements:
```bash
black .
```

### 2. Linting (Ruff)
Run fast code linting checks (cleans unused imports, verifies sorted import blocks):
```bash
ruff check .
# Automatically fix fixable warnings:
ruff check --fix .
```

### 3. Static Type Checking (MyPy)
Validate type annotations on parameters and return signatures across core modules:
```bash
mypy --explicit-package-bases modules/
```

### 4. Running Unit Tests (Pytest)
Run the automated test suite with test database isolation and code coverage reports:
```bash
python -m pytest
```

### 5. Running Environment Validation
Check database schema integrity, GGUF paths, and upload directory permissions:
```bash
python scripts/validate_project.py
```

### 6. Developer Tasks via Makefile
If you have `make` installed (Linux, macOS, or git-bash / mingw on Windows):
*   `make format` - Format code with Black
*   `make lint` - Lint check with Ruff
*   `make typecheck` - Static type check with MyPy
*   `make test` - Execute unit tests with Pytest
*   `make validate` - Validate local environment health
*   `make all` - Execute all quality checks sequentially

### 7. Setting Up Git Pre-Commit Hooks
Enable automated quality checks before every commit:
```bash
pre-commit install
```
This registers pre-commit hooks for Black, Ruff, and MyPy. Every subsequent `git commit` automatically formats, lints, and typechecks the staged files before allowing the commit to proceed.

