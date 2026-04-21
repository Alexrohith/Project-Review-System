from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ProjectAnalysis(BaseModel):
    """Schema for project understanding analysis."""
    summary: str
    technologies: List[str]
    structure: Dict[str, Any]
    complexity: str
    key_components: List[str]


class CodeReview(BaseModel):
    """Schema for code review output."""
    overall_rating: int  # 1-10
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    critical_issues: List[str]
    code_quality_score: int  # 1-10


class InterviewQuestion(BaseModel):
    """Schema for interview questions."""
    question: str
    category: str
    difficulty: str
    expected_answer: Optional[str] = None


class InterviewSession(BaseModel):
    """Schema for complete interview session."""
    questions: List[InterviewQuestion]
    total_questions: int
    categories_covered: List[str]


class GapAnalysis(BaseModel):
    """Schema for gap analysis output."""
    identified_gaps: List[str]
    missing_features: List[str]
    improvement_suggestions: List[str]
    priority_level: str


class ReviewRequest(BaseModel):
    """Schema for review request input."""
    project_path: str
    review_type: str  # "full", "code", "interview", "gaps"
    include_analysis: bool = True


class ReviewResponse(BaseModel):
    """Schema for complete review response."""
    project_analysis: Optional[ProjectAnalysis] = None
    code_review: Optional[CodeReview] = None
    interview: Optional[InterviewSession] = None
    gap_analysis: Optional[GapAnalysis] = None
    timestamp: str
    review_id: str
