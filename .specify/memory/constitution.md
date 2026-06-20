# CampusGPT Spec-Kit Constitution

This document defines the core coding standards, architectural guidelines, and quality gates for the CampusGPT project. All AI agents and developers must adhere to this constitution.

---

## 🤖 Core Standards & Guidelines

1. **Zero Placeholders**: Never insert comments like `# TODO: implement` or stub/failing functions in source code or test suites. All implementations must be production-ready and fully functional.
2. **Formatting**: Always format Python code with **Black** (`black .`) before committing.
3. **Linting Rules**:
    * Run **Ruff** checks: `ruff check .`
    * Run **Flake8** checks: `flake8 .`
    * Run **Pylint** checks: `pylint modules/`
    * Run **Vulture** checks: `vulture`
4. **Static Type Safety**: 
    * Add strict parameter and return type annotations to all logic functions in python core modules under the `modules/` directory.
    * Mypy must pass type checks: `mypy .` (excluding tests, pages, and scripts).
5. **Security Scanning**:
    * Run `bandit -c pyproject.toml -r modules/` for static analysis.
    * Run `pip-audit --local` to scan dependencies.
    * Run `detect-secrets scan --baseline .secrets.baseline` to scan for secrets.

---

## 🧪 Testing Constraints

1. **Isolated Testing Database**:
    * Never run tests against the production SQLite database `database/campusgpt.db`.
    * All test suites must use the pytest fixture redirect (`tests/conftest.py`) which points operations to `test_campusgpt.db` and deletes the file after execution.
2. **Mocking Heavy Dependencies**:
    * Mock out heavy weights, vectorizers, and local LLM execution.
3. **Coverage Thresholds**:
    * Overall project coverage must be at or above **45%** fail-under.

---

## 🚀 SDD Process (Spec-Kit Workflow)

1. **Specify**: Define requirements in a feature spec under the `specs/` directory before writing code.
2. **Plan**: Write a technical plan mapping implementation details.
3. **Tasks**: Break planning down into actionable, checklist-style tasks.
4. **Implement**: Program and execute following the spec roadmap.
