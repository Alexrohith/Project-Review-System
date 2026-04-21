import os
import json
import re
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..schemas.outputs import InterviewSession, InterviewQuestion
from ..rag.retriever import Retriever


def safe_json_load(text: str) -> Dict[str, Any]:
    """Safely load JSON with auto-repair for common issues.
    
    Handles:
    - Trailing commas
    - Missing closing braces
    - Extra whitespace
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Auto-repair: Remove trailing commas before ] or }
        repaired = re.sub(r',\s*([}\]])', r'\1', text)
        repaired = repaired.strip()
        
        # Ensure proper closing
        if repaired.count("{") > repaired.count("}"):
            repaired += "}"
        if repaired.count("[") > repaired.count("]"):
            repaired += "]"
        
        try:
            return json.loads(repaired)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON repair failed: {str(e)}\nText: {text[:200]}...")


class InterviewerAgent:
    """Agent responsible for generating technical interview questions."""

    def __init__(self, retriever: Retriever):
        """Initialize the interviewer agent.

        Args:
            retriever: Retriever instance for RAG
        """
        self.llm = ChatGroq(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=800,
            timeout=20,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.retriever = retriever
        self.output_parser = StrOutputParser()

    def _parse_interview_questions(self, text: str, expected_count: int = 10) -> InterviewSession:
        """Parse the LLM output into InterviewSession.
        
        Expected format: Valid JSON with questions.
        Uses safe_json_load for auto-repair.
        """
        questions = []
        categories = set()
        
        # Strip whitespace and remove potential markdown code block wrappers
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            # Use safe JSON loading with auto-repair
            data = safe_json_load(text)
            
            if "questions" not in data:
                raise ValueError("JSON missing 'questions' key")
            
            questions_list = data["questions"]
            
            if not isinstance(questions_list, list):
                raise ValueError("'questions' must be an array")
            
            if len(questions_list) != expected_count:
                raise ValueError(
                    f"❌ Expected {expected_count} questions, got {len(questions_list)}. "
                    f"LLM must return EXACTLY {expected_count} questions in the 'questions' array."
                )
            
            for idx, q in enumerate(questions_list):
                try:
                    if not isinstance(q, dict):
                        raise ValueError(f"Question {idx} is not a dictionary")
                    
                    question_text = q.get("question", "")
                    category = q.get("category", "General")
                    difficulty = q.get("difficulty", "Medium")
                    expected_answer = q.get("expected_answer", "")
                    
                    # Validate fields are not empty
                    if not question_text:
                        raise ValueError(f"Question {idx} has empty 'question' field")
                    if not expected_answer:
                        raise ValueError(f"Question {idx} has empty 'expected_answer' field")
                    
                    # Validate difficulty is one of the allowed values
                    if difficulty not in ["Easy", "Medium", "Hard"]:
                        raise ValueError(f"Question {idx} has invalid difficulty: {difficulty}. Must be 'Easy', 'Medium', or 'Hard'")
                    
                    question = InterviewQuestion(
                        question=question_text,
                        category=category,
                        difficulty=difficulty,
                        expected_answer=expected_answer
                    )
                    questions.append(question)
                    categories.add(category)
                except Exception as e:
                    print(f"❌ Error parsing question {idx}: {e}")
                    raise
        
        except ValueError as e:
            print(f"❌ Validation error: {e}")
            raise
        except Exception as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Raw text (first 500 chars): {text[:500]}...")
            raise ValueError(f"LLM output parsing failed: {str(e)}")

        return InterviewSession(
            questions=questions,
            total_questions=len(questions),
            categories_covered=list(categories)
        )

    def generate_interview(self, project_analysis: str, code_review_summary: str, num_questions: int = 10) -> InterviewSession:
        """Generate an interview session by splitting into 2 calls to avoid token overflow.

        Args:
            project_analysis: Analysis of the project
            code_review_summary: Summary of code review findings
            num_questions: Total number of questions to generate (default 10)

        Returns:
            InterviewSession object
        """
        if num_questions != 10:
            raise ValueError("Only 10 questions are supported")
        
        try:
            # Load prompt template
            prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "interviewer_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["project_analysis", "code_review_summary", "num_questions"]
            )

            # Create the chain
            chain = prompt | self.llm | self.output_parser
            
            # 🔥 SPLIT INTO 2 CALLS to avoid token overflow
            # Call 1: Questions 1-5
            print(f"[INTERVIEW] Generating questions 1-5...")
            payload_1 = {
                "project_analysis": project_analysis[:1200],
                "code_review_summary": code_review_summary[:600],
                "num_questions": 5
            }
            
            try:
                result_1 = chain.invoke(payload_1)
            except Exception as e:
                print(f"[INTERVIEW] Call 1 error: {e}")
                raise ValueError(f"Interview generation call 1 failed: {str(e)}")
            
            # Parse first batch
            session_1 = self._parse_interview_questions(result_1, expected_count=5)
            print(f"[INTERVIEW] ✅ Generated questions 1-5")
            
            # Call 2: Questions 6-10
            print(f"[INTERVIEW] Generating questions 6-10...")
            payload_2 = {
                "project_analysis": project_analysis[:1200],
                "code_review_summary": code_review_summary[:600],
                "num_questions": 5
            }
            
            try:
                result_2 = chain.invoke(payload_2)
            except Exception as e:
                print(f"[INTERVIEW] Call 2 error: {e}")
                raise ValueError(f"Interview generation call 2 failed: {str(e)}")
            
            # Parse second batch
            session_2 = self._parse_interview_questions(result_2, expected_count=5)
            print(f"[INTERVIEW] ✅ Generated questions 6-10")
            
            # Merge results
            merged_questions = session_1.questions + session_2.questions
            all_categories = set(session_1.categories_covered + session_2.categories_covered)
            
            return InterviewSession(
                questions=merged_questions,
                total_questions=len(merged_questions),
                categories_covered=list(all_categories)
            )

        except Exception as e:
            # Re-raise the exception so the backend can handle it properly
            print(f"❌ Interview generation failed: {str(e)}")
