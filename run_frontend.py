#!/usr/bin/env python3
"""
Streamlit Frontend Runner for AI Project Reviewer
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit frontend."""
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")

    if not os.path.exists(frontend_path):
        print(f"Error: Frontend app not found at {frontend_path}")
        sys.exit(1)

    print("Starting AI Project Reviewer Frontend...")
    print("Make sure the API server is running on http://localhost:8000")
    print("Frontend will be available at http://localhost:8501")
    print()

    try:
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", frontend_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nFrontend stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()