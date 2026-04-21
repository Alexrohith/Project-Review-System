import os
import re
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..schemas.outputs import CodeReview
from ..rag.retriever import Retriever


class ReviewerAgent:
    """Agent responsible for providing code reviews."""

    def __init__(self, retriever: Retriever):
        """Initialize the reviewer agent.

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

    def _parse_code_review(self, text: str) -> CodeReview:
        """Parse the LLM output into CodeReview components."""
        overall_rating = 5
        strengths = []
        weaknesses = []
        recommendations = []
        critical_issues = []
        code_quality_score = 5

        # Split by numbered sections
        sections = re.split(r'\d+\.\s*', text)
        for section in sections[1:]:  # Skip the first empty part
            section = section.strip()
            if section.startswith("Overall Rating"):
                content = section.replace("Overall Rating", "").strip()
                try:
                    overall_rating = int(re.search(r'\d+', content).group())
                    overall_rating = max(1, min(10, overall_rating))
                except:
                    pass
            elif section.startswith("Key Strengths") or section.startswith("Strengths"):
                content = section.replace("Key Strengths", "").replace("Strengths", "").strip()
                strengths = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Areas for Improvement") or section.startswith("Weaknesses"):
                content = section.replace("Areas for Improvement", "").replace("Weaknesses", "").strip()
                weaknesses = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Specific Recommendations") or section.startswith("Recommendations"):
                content = section.replace("Specific Recommendations", "").replace("Recommendations", "").strip()
                recommendations = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Critical Issues"):
                content = section.replace("Critical Issues", "").strip()
                critical_issues = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Code Quality Score"):
                content = section.replace("Code Quality Score", "").strip()
                try:
                    code_quality_score = int(re.search(r'\d+', content).group())
                    code_quality_score = max(1, min(10, code_quality_score))
                except:
                    pass

        return CodeReview(
            overall_rating=overall_rating,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            critical_issues=critical_issues,
            code_quality_score=code_quality_score
        )

    def review_code(self, project_path: str, project_context: str) -> CodeReview:
        """Provide a comprehensive code review.

        Args:
            project_path: Path to the project
            project_context: Context about the project

        Returns:
            CodeReview object
        """
        try:
            # Read key code files
            code_content = self._extract_code_content(project_path)

            # Get relevant best practices
            best_practices = self.retriever.get_best_practices("code quality")

            # Load prompt template
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "reviewer_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["project_context", "code_content"]
            )

            # Create the chain
            chain = prompt | self.llm | self.output_parser

            # Run the review with safety net
            payload = {
                "project_context": project_context,
                "code_content": code_content
            }

            try:
                result = chain.invoke(payload)
            except Exception:
                # Truncate inputs on overflow
                payload["project_context"] = payload["project_context"][:1500]
                payload["code_content"] = payload["code_content"][:2000]
                result = chain.invoke(payload)

            return self._parse_code_review(result)

        except Exception as e:
            # Return a basic review if something goes wrong
            return CodeReview(
                overall_rating=5,
                strengths=["Project structure appears functional"],
                weaknesses=[f"Error during analysis: {str(e)}"],
                recommendations=["Fix analysis errors"],
                critical_issues=[],
                code_quality_score=5
            )

    def _extract_code_content(self, project_path: str, max_files: int = 10) -> str:
        """Extract content from key code files.

        Args:
            project_path: Path to the project
            max_files: Maximum number of files to analyze

        Returns:
            String containing code content
        """
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go'}
        code_content = []
        files_processed = 0

        for root, dirs, files in os.walk(project_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in {'node_modules', '__pycache__', '.git', 'venv', 'env'}]

            for file in files:
                if files_processed >= max_files:
                    break

                _, ext = os.path.splitext(file)
                if ext.lower() in code_extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():  # Only include non-empty files
                                relative_path = os.path.relpath(file_path, project_path)
                                code_content.append(f"=== {relative_path} ===\n{content[:2000]}...")  # Limit content
                                files_processed += 1
                    except Exception as e:
                        continue

        return "\n\n".join(code_content) if code_content else "No code files found or accessible."
