import os
import json
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..schemas.outputs import ProjectAnalysis
from ..rag.retriever import Retriever
from ..utils.tech_detector import extract_technologies


class ProjectUnderstandingAgent:
    """Agent responsible for understanding and analyzing project structure."""

    # Ignored directories to prevent token explosion
    IGNORE_DIRS = {
        "venv", ".git", "__pycache__", ".idea", ".vscode",
        "node_modules", "dist", "build", ".pytest_cache",
        "env", ".env", "eggs", ".eggs", "*.egg-info", "site-packages"
    }
    
    # Only include relevant file types
    INCLUDE_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".sh", ".bat"}

    def __init__(self, retriever: Retriever):
        """Initialize the project understanding agent.

        Args:
            retriever: Retriever instance for RAG
        """
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=600,
            timeout=20,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.retriever = retriever
        self.output_parser = StrOutputParser()

        # Create prompt template
        template = """
You are a senior software engineer analyzing a software project.

Rules:
- Be concise
- Do NOT guess technologies
- List ONLY what is clearly visible
- Keep responses short
- Avoid repetition

Project Path:
{project_path}

Project Structure (truncated):
{project_structure}

Additional Context (limited):
{context}

Return VALID JSON in this exact format:

{{
  "summary": "2–3 sentences only",
  "technologies": ["max 5 items"],
  "structure": {{"overview": "1–2 sentences"}},
  "complexity": "Low | Medium | High",
  "key_components": ["max 5 items"]
}}
"""

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["project_path", "project_structure", "context"]
        )

    def analyze_project(self, project_path: str) -> ProjectAnalysis:
        """Analyze the project structure and provide understanding.

        Args:
            project_path: Path to the project directory

        Returns:
            ProjectAnalysis object
        """
        try:
            # Get project structure
            project_structure = self._get_project_structure(project_path)

            # Extract technologies safely
            technologies = extract_technologies(project_path)

            # Get additional context from retriever
            context = self.retriever.get_project_context(project_path)

            # Create the chain
            chain = self.prompt | self.llm | self.output_parser

            # Run the analysis with safety net
            payload = {
                "project_path": project_path,
                "project_structure": project_structure,
                "context": context
            }

            try:
                result_str = chain.invoke(payload)
            except Exception:
                # Truncate inputs on overflow
                payload["project_structure"] = payload["project_structure"][:1500]
                payload["context"] = payload["context"][:800]
                result_str = chain.invoke(payload)

            # Parse JSON result
            try:
                result = json.loads(result_str)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                result = {
                    "summary": result_str[:500],
                    "structure": {"overview": "Analysis completed"},
                    "complexity": "Medium",
                    "key_components": []
                }

            return ProjectAnalysis(
                summary=result.get("summary", "Analysis completed"),
                technologies=technologies,  # 🔥 STATIC + SAFE
                structure=result.get("structure", {}),
                complexity=result.get("complexity", "Medium"),
                key_components=result.get("key_components", [])
            )

        except Exception as e:
            # Return a basic analysis if something goes wrong
            technologies = extract_technologies(project_path)
            return ProjectAnalysis(
                summary=f"Error analyzing project: {str(e)}",
                technologies=technologies,
                structure={"error": str(e)},
                complexity="Unknown",
                key_components=[]
            )

    def _get_project_structure(self, project_path: str, max_depth: int = 3) -> str:
        """Get a string representation of the project structure.

        Args:
            project_path: Path to the project
            max_depth: Maximum directory depth to traverse

        Returns:
            String representation of project structure
        """
        structure_lines = []

        def walk_directory(path: str, current_depth: int = 0, prefix: str = ""):
            if current_depth > max_depth:
                return

            try:
                items = [
                    item for item in os.listdir(path)
                    if item not in self.IGNORE_DIRS
                ]
            except PermissionError:
                structure_lines.append(f"{prefix}[Permission Denied]")
                return

            # Sort items: directories first, then files
            dirs = [item for item in items if os.path.isdir(os.path.join(path, item))]
            files = [
                item for item in items 
                if os.path.isfile(os.path.join(path, item)) and 
                any(item.endswith(ext) for ext in self.INCLUDE_EXTENSIONS)
            ]

            all_items = dirs + files

            for i, item in enumerate(all_items):
                is_last = i == len(all_items) - 1
                item_path = os.path.join(path, item)

                if os.path.isdir(item_path):
                    structure_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item}/")
                    if current_depth < max_depth:
                        new_prefix = prefix + ("    " if is_last else "│   ")
                        walk_directory(item_path, current_depth + 1, new_prefix)
                else:
                    structure_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item}")

        walk_directory(project_path)
        structure = "\n".join(structure_lines)
        return structure[:3000]  # token safety limit
