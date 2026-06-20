import os
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def package_source_code_zip():
    print("Packaging codebase into CampusGPT.zip...")
    zip_path = os.path.join(BASE_DIR, "CampusGPT.zip")

    # If old zip exists, remove it first
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except Exception as e:
            print(f"Warning: could not remove old zip: {e}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(BASE_DIR):
            # Skip heavy runtime folders, indices, database files, and caches
            if any(
                part in root
                for part in [
                    "data",
                    "database",
                    "logs",
                    "__pycache__",
                    ".git",
                    ".venv",
                    "htmlcov",
                    ".mypy_cache",
                    ".pytest_cache",
                    ".ruff_cache",
                ]
            ):
                continue

            for file in files:
                # Exclude runtime-generated files and the zip itself
                if file.endswith((".db", ".log", ".pyc", ".zip")) or file == ".coverage":
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                zip_file.write(file_path, rel_path)
                print(f"  [ADD] {rel_path}")

    print("Successfully packaged CampusGPT.zip!")


if __name__ == "__main__":
    package_source_code_zip()
