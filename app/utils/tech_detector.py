import os
import re
from typing import Set

KNOWN_TECH_KEYWORDS = {
    "fastapi": "FastAPI",
    "streamlit": "Streamlit",
    "flask": "Flask",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "langchain": "LangChain",
    "faiss": "FAISS",
    "numpy": "NumPy",
    "pandas": "Pandas",
    "sklearn": "Scikit-learn",
    "openai": "OpenAI",
    "groq": "Groq",
    "uvicorn": "Uvicorn"
}

def extract_technologies(project_path: str) -> list[str]:
    detected: Set[str] = set()

    # 1️⃣ Scan requirements.txt
    req_file = os.path.join(project_path, "requirements.txt")
    if os.path.exists(req_file):
        with open(req_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                for key, tech in KNOWN_TECH_KEYWORDS.items():
                    if key in line.lower():
                        detected.add(tech)

    # 2️⃣ Scan Python files for imports
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        for key, tech in KNOWN_TECH_KEYWORDS.items():
                            if re.search(rf"\b{key}\b", content):
                                detected.add(tech)
                except Exception:
                    pass

    # 3️⃣ File-based conventions
    if os.path.exists(os.path.join(project_path, "app.py")):
        detected.add("Python")

    return sorted(detected)