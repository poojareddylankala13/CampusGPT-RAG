import os
import subprocess
import sys


def run_test_suite() -> int:
    """Runs the pytest suite with coverage configuration.

    Returns:
        int: The exit code of the pytest execution.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("====================================================")
    print("🚀 Starting CampusGPT Pytest Suite...")
    print("====================================================")

    # Define pytest flags
    cmd = [sys.executable, "-m", "pytest", "--cov=modules", "--cov-report=term-missing", "--cov-report=html"]

    # Run process
    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print("\n✅ All unit tests passed successfully!")
    else:
        print(f"\n❌ Test suite failed with exit code: {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_test_suite())
