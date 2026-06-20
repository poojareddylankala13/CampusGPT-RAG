# CampusGPT Contribution Guidelines

Welcome! We are excited to have you contribute to CampusGPT. Please follow these instructions to ensure consistency, safety, and high-quality updates across the codebase.

---

## 🤖 Code Style & Integrity Standards

1. **Zero Placeholders**: Never insert comments like `# TODO: implement` or stub/failing functions in source code or test suites. All implementations must be production-ready and fully functional.
2. **Formatting**: Always format Python code with **Black** (`black .`) before committing.
3. **Linting Rules**:
    * Run **Ruff** checks: `ruff check .`
    * Long lines (E501) and whitespace blank lines (W293) are ignored in `ruff.toml` to support multi-line HTML strings used in Streamlit interfaces. All other PEP 8 syntax errors and import rules must pass without warnings.
4. **Static Type Safety**: 
    * Add strict parameter and return type annotations to all logic functions in python core modules under the `modules/` directory.
    * Mypy must pass type checks: `mypy .` (excluding tests, pages, and samples via config).
5. **Preserve Existing Features**: Do not replace or modify existing features (such as user database registrations, local GGUF models mapping, FAISS dimension partitions, or caching mechanics) unless explicitly requested.

---

## 🧪 Testing Guidelines

1. **Isolated Testing Database**:
    * Never run tests against the production SQLite database `database/campusgpt.db` to prevent user accounts and log metrics from being contaminated or deleted.
    * All test suites must use the pytest fixture redirect (`tests/conftest.py`) which points operations to `test_campusgpt.db` and deletes the file after execution.
2. **Mocking Heavy Dependencies**:
    * When writing unit tests for embeddings or local LLM execution, use mock stubs (`unittest.mock.patch`) to simulate model vectors and streaming outputs. Test suites must complete in milliseconds without requiring heavy weight files (GGUFs) to be loaded on standard CPU test environments.
3. **Test Coverage**: Keep overall project coverage high, prioritizing core logic files in the `modules/` folder. Minimum test coverage limit is enforced at **45%** fail-under.

---

## 🚀 Branching & Workflow

1. **Branch Naming**:
   * Features: `feature/feature-name`
   * Bug Fixes: `bugfix/bug-name`
   * Refactoring: `refactor/change-name`
2. **Local Validation**:
   Before pushing, run all quality checks locally:
   ```bash
   make all
   ```
3. **Pull Requests (PRs) / Merge Requests (MRs)**:
   * Make sure your branch is rebased on the latest `main`.
   * Open a PR/MR with a descriptive title detailing what has changed.
   * Verify that the GitLab CI/CD pipelines pass completely.
