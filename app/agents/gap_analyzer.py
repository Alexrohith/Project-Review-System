import os
import re
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..schemas.outputs import GapAnalysis
from ..rag.retriever import Retriever


class GapAnalyzerAgent:
    """Agent responsible for identifying gaps and areas for improvement."""

    def __init__(self, retriever: Retriever):
        """Initialize the gap analyzer agent.

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

    def _parse_gap_analysis(self, text: str) -> GapAnalysis:
        """Parse the LLM output into GapAnalysis components."""
        identified_gaps = []
        missing_features = []
        improvement_suggestions = []
        priority_level = "Medium"

        # Split by numbered sections
        sections = re.split(r'\d+\.\s*', text)
        for section in sections[1:]:  # Skip the first empty part
            section = section.strip()
            if section.startswith("Identified Gaps:"):
                content = section.replace("Identified Gaps:", "").strip()
                identified_gaps = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Missing Features:"):
                content = section.replace("Missing Features:", "").strip()
                missing_features = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Improvement Suggestions:"):
                content = section.replace("Improvement Suggestions:", "").strip()
                improvement_suggestions = [line.strip('- ').strip() for line in content.split('\n') if line.strip()]
            elif section.startswith("Priority Level:"):
                content = section.replace("Priority Level:", "").strip()
                priority_level = content.strip()

        return GapAnalysis(
            identified_gaps=identified_gaps,
            missing_features=missing_features,
            improvement_suggestions=improvement_suggestions,
            priority_level=priority_level
        )

    def analyze_gaps(self, project_analysis: str, code_review_findings: str, technologies: List[str]) -> GapAnalysis:
        """Analyze gaps and provide improvement suggestions.

        Args:
            project_analysis: Analysis of the project
            code_review_findings: Findings from code review
            technologies: List of technologies used

        Returns:
            GapAnalysis object
        """
        try:
            # Load prompt template
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "gap_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["project_analysis", "code_review_findings", "technologies"]
            )

            # Create the chain
            chain = prompt | self.llm | self.output_parser

            # Run the gap analysis with safety net
            payload = {
                "project_analysis": project_analysis,
                "code_review_findings": code_review_findings,
                "technologies": ", ".join(technologies)
            }

            try:
                result = chain.invoke(payload)
            except Exception:
                # Truncate inputs on overflow
                payload["project_analysis"] = payload["project_analysis"][:1500]
                payload["code_review_findings"] = payload["code_review_findings"][:800]
                payload["technologies"] = payload["technologies"][:500]
                result = chain.invoke(payload)

            return self._parse_gap_analysis(result)

        except Exception as e:
            # Return a basic gap analysis if something goes wrong
            return GapAnalysis(
                identified_gaps=[f"Error during analysis: {str(e)}"],
                missing_features=[],
                improvement_suggestions=["Fix analysis errors"],
                priority_level="High"
            )
