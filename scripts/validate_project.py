import os
import sqlite3
import sys


def validate_environment() -> bool:
    """Verifies that all project requirements, directories, and tables are set up correctly.

    Returns:
        bool: True if validation succeeds, else False.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("====================================================")
    print("🎓 Validating CampusGPT Project Environment Setup...")
    print("====================================================")

    success = True

    # 1. Check Required Files
    required_files = ["app.py", "requirements.txt", ".gitignore", "Makefile"]
    print("\n📁 Checking critical files:")
    for file in required_files:
        path = os.path.join(project_root, file)
        if os.path.exists(path):
            print(f"  [OK] Found: {file}")
        else:
            print(f"  [MISSING] Required file: {file}")
            success = False

    # 2. Check Directories & Write Access
    required_dirs = [
        ("data/uploads", "Upload directory"),
        ("database", "SQLite directory"),
        ("models", "Local GGUF models folder"),
        ("cache/embeddings", "Embeddings cache directory"),
        ("cache/queries", "Query cache directory"),
    ]
    print("\n📂 Checking directories and write permissions:")
    for rel_path, desc in required_dirs:
        abs_path = os.path.join(project_root, rel_path)
        os.makedirs(abs_path, exist_ok=True)
        # Test write access
        test_file = os.path.join(abs_path, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print(f"  [OK] Write access verified for {rel_path} ({desc})")
        except Exception as e:
            print(f"  [ERROR] Write access failed for {rel_path} ({desc}): {e}")
            success = False

    # 3. Check SQLite Database Connection & Tables
    db_path = os.path.join(project_root, "database", "campusgpt.db")
    print("\n🗄️ Checking SQLite Database connection:")
    if not os.path.exists(db_path):
        print("  [WARN] Database file campusgpt.db not found on disk yet. It will be initialized on first run.")
    else:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Verify table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            conn.close()

            expected_tables = ["users", "documents", "chat_history", "feedback", "searches", "rag_evaluations"]
            all_tables_ok = True
            for t in expected_tables:
                if t in tables:
                    print(f"  [OK] Table verified: {t}")
                else:
                    print(f"  [MISSING] Table: {t}")
                    all_tables_ok = False

            if not all_tables_ok:
                print("  [ERROR] Database schema tables check failed.")
                success = False
        except Exception as e:
            print(f"  [ERROR] Database connection failed: {e}")
            success = False

    # 4. Check FAISS Vector Folders
    faiss_dir = os.path.join(project_root, "data", "faiss_index")
    print("\n🔀 Checking FAISS vector store folders:")
    if os.path.exists(faiss_dir):
        indices = os.listdir(faiss_dir)
        print(f"  [OK] Found FAISS index folder. Current models partitioned: {indices}")
    else:
        print("  [WARN] FAISS vector index folder not created yet. It will build when files are uploaded.")

    # 5. Check GGUF Models Folder
    models_dir = os.path.join(project_root, "models")
    print("\n🤖 Checking local GGUF models:")
    if os.path.exists(models_dir):
        ggufs = [f for f in os.listdir(models_dir) if f.lower().endswith(".gguf")]
        if ggufs:
            print(f"  [OK] Found GGUF models: {ggufs}")
        else:
            print(
                "  [INFO] Models directory is currently empty. Use Gemini mode or download GGUF models to run offline."
            )
    else:
        print("  [WARN] Models directory is missing.")

    print("\n====================================================")
    if success:
        print("🎉 Validation Successful: Project environment is completely ready!")
    else:
        print("❌ Validation Failed: Some issues were encountered.")
    print("====================================================")

    return success


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if validate_environment() else 1)
