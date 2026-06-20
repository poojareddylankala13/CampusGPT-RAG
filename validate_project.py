import os
import sys


def validate_structure() -> bool:
    """Verifies that all required files, directories, specifications, and tests exist.

    Exits with 0 on success, 1 on failure.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    print("====================================================")
    print("🎓 Validating CampusGPT Quality & Compliance Footprint...")
    print("====================================================")

    success = True

    # 1. Check Required Directories
    required_dirs = [
        "modules",
        "pages",
        "tests",
        "specs",
        ".specify",
        "database",
        "models",
    ]
    print("\n📂 Checking required directories:")
    for directory in required_dirs:
        dir_path = os.path.join(project_root, directory)
        if os.path.isdir(dir_path):
            print(f"  [OK] Directory exists: {directory}/")
        else:
            print(f"  [MISSING] Directory: {directory}/")
            success = False

    # 2. Check Compliance & Configuration Files
    required_files = [
        "app.py",
        "requirements.txt",
        "Makefile",
        ".gitignore",
        "Dockerfile",
        ".dockerignore",
        "CHANGELOG.md",
        "SECURITY.md",
        "CODE_OF_CONDUCT.md",
        "AGENTS.md",
        ".editorconfig",
    ]
    print("\n📁 Checking required root files:")
    for file in required_files:
        file_path = os.path.join(project_root, file)
        if os.path.isfile(file_path):
            print(f"  [OK] File exists: {file}")
        else:
            print(f"  [MISSING] File: {file}")
            success = False

    # 3. Check Specification Files in specs/
    required_specs = [
        "specs/authentication.md",
        "specs/chat_system.md",
        "specs/rag_pipeline.md",
        "specs/embeddings.md",
        "specs/vector_store.md",
        "specs/summarization.md",
        "specs/pdf_upload.md",
        "specs/campus_search.md",
    ]
    print("\n📖 Checking specification documents:")
    for spec in required_specs:
        spec_path = os.path.join(project_root, spec)
        if os.path.isfile(spec_path):
            print(f"  [OK] Spec exists: {spec}")
        else:
            print(f"  [MISSING] Spec document: {spec}")
            success = False

    # 4. Check Unit Tests in tests/
    required_tests = [
        "tests/test_auth.py",
        "tests/test_chat.py",
        "tests/test_document_parser.py",
        "tests/test_embeddings.py",
        "tests/test_vector_store.py",
        "tests/test_rag_pipeline.py",
        "tests/test_summarizer.py",
    ]
    print("\n🧪 Checking unit test suites:")
    for test in required_tests:
        test_path = os.path.join(project_root, test)
        if os.path.isfile(test_path):
            print(f"  [OK] Test exists: {test}")
        else:
            print(f"  [MISSING] Test suite: {test}")
            success = False

    print("\n====================================================")
    if success:
        print("🎉 Success: Project structure is completely valid!")
    else:
        print("❌ Error: Some required components are missing.")
    print("====================================================")

    return success


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if validate_structure() else 1)
