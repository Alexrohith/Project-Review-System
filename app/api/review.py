import threading
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from ..schemas.outputs import ReviewRequest, ReviewResponse

# Load environment variables
load_dotenv()

router = APIRouter()

# Global instances (lazy-loaded to avoid blocking startup)
_vector_store: Optional[Any] = None
_retriever: Optional[Any] = None
_project_agent: Optional[Any] = None
_reviewer_agent: Optional[Any] = None
_interviewer_agent: Optional[Any] = None
_gap_agent: Optional[Any] = None


def _initialize_agents():
    """Initialize agents lazily on first use."""
    global _vector_store, _retriever, _project_agent, _reviewer_agent, _interviewer_agent, _gap_agent
    
    if _project_agent is None:
        print("Initializing agents (this may take a moment)...")
        # Import inside function to defer loading
        from ..agents.project_understanding import ProjectUnderstandingAgent
        from ..agents.reviewer_agent import ReviewerAgent
        from ..agents.interviewer_agent import InterviewerAgent
        from ..agents.gap_analyzer import GapAnalyzerAgent
        from ..rag.vector_store import VectorStore
        from ..rag.retriever import Retriever
        
        _vector_store = VectorStore()
        _retriever = Retriever(_vector_store)
        _project_agent = ProjectUnderstandingAgent(_retriever)
        _reviewer_agent = ReviewerAgent(_retriever)
        _interviewer_agent = InterviewerAgent(_retriever)
        _gap_agent = GapAnalyzerAgent(_retriever)
        print("Agents initialized successfully!")


def get_project_agent():
    """Get or initialize project agent."""
    _initialize_agents()
    return _project_agent


def get_reviewer_agent():
    """Get or initialize reviewer agent."""
    _initialize_agents()
    return _reviewer_agent


def get_interviewer_agent():
    """Get or initialize interviewer agent."""
    _initialize_agents()
    return _interviewer_agent


def get_gap_agent():
    """Get or initialize gap agent."""
    _initialize_agents()
    return _gap_agent

# Store for ongoing reviews (in production, use a database)
ongoing_reviews: Dict[str, Dict[str, Any]] = {}


@router.post("/review", response_model=ReviewResponse)
def review_project(request: ReviewRequest):
    """Endpoint to submit a project for review (SYNC - returns immediately).

    Args:
        request: ReviewRequest containing project details

    Returns:
        ReviewResponse with review ID for tracking
    """
    try:
        # Validate project path
        if not os.path.exists(request.project_path):
            raise HTTPException(status_code=400, detail="Project path does not exist")

        # Generate review ID
        review_id = str(uuid.uuid4())

        # Initialize review status
        ongoing_reviews[review_id] = {
            "status": "processing",
            "project_path": request.project_path,
            "review_type": request.review_type,
            "include_analysis": request.include_analysis,
            "started_at": datetime.now().isoformat()
        }

        print(f"[POST] Accepted review {review_id}")

        # Start background processing in a separate thread (NON-BLOCKING)
        threading.Thread(
            target=process_review,
            args=(review_id,),
            daemon=True
        ).start()

        # Return immediately with review ID
        return ReviewResponse(
            project_analysis=None,
            code_review=None,
            interview=None,
            gap_analysis=None,
            timestamp=datetime.now().isoformat(),
            review_id=review_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating review: {str(e)}")


@router.get("/review/{review_id}")
def get_review_status(review_id: str):
    """Get the status and results of a review (SYNC endpoint).

    Args:
        review_id: Unique review identifier

    Returns:
        Review status and results if completed
    """
    if review_id not in ongoing_reviews:
        raise HTTPException(status_code=404, detail="Review not found")

    review_data = ongoing_reviews[review_id]

    if review_data["status"] == "completed":
        # Return the completed review
        return {
            "status": "completed",
            "review": review_data["result"],
            "completed_at": review_data.get("completed_at")
        }
    elif review_data["status"] == "error":
        return {
            "status": "error",
            "error": review_data.get("error"),
            "completed_at": review_data.get("completed_at")
        }
    else:
        return {
            "status": "processing",
            "message": "Review is still being processed",
            "started_at": review_data["started_at"]
        }


def process_review(review_id: str):
    """Background task to process the review (SYNC - runs in thread).

    Args:
        review_id: Unique review identifier
    """
    print(f"[PROCESS] Started review {review_id}")
    
    # 🔧 ENSURE status is ALWAYS updated (safe wrapper)
    try:
        # Mark as processing
        ongoing_reviews[review_id]["status"] = "processing"
        
        review_data = ongoing_reviews[review_id]
        project_path = review_data["project_path"]
        review_type = review_data["review_type"]
        include_analysis = review_data["include_analysis"]

        results = {}

        # Get agents (lazy-loaded)
        project_agent = get_project_agent()
        reviewer_agent = get_reviewer_agent()
        interviewer_agent = get_interviewer_agent()
        gap_agent = get_gap_agent()

        # Always perform project analysis if requested
        if include_analysis:
            print(f"[PROCESS {review_id}] ⏳ Starting project analysis...")
            results["project_analysis"] = project_agent.analyze_project(project_path)
            print(f"[PROCESS {review_id}] ✅ Project analysis done")

        # Perform requested review types
        if review_type in ["full", "code"]:
            project_context = ""
            if "project_analysis" in results:
                project_context = f"Project: {results['project_analysis'].summary}\nTechnologies: {', '.join(results['project_analysis'].technologies)}"

            print(f"[PROCESS {review_id}] ⏳ Starting code review...")
            results["code_review"] = reviewer_agent.review_code(project_path, project_context)
            print(f"[PROCESS {review_id}] ✅ Code review done")

        if review_type in ["full", "interview"]:
            project_analysis_str = ""
            code_review_summary = ""

            if "project_analysis" in results:
                project_analysis_str = f"Summary: {results['project_analysis'].summary}\nComplexity: {results['project_analysis'].complexity}"

            if "code_review" in results:
                code_review_summary = f"Rating: {results['code_review'].overall_rating}/10\nStrengths: {', '.join(results['code_review'].strengths[:3])}"

            print(f"[PROCESS {review_id}] ⏳ Starting interview generation...")
            try:
                interview_result = interviewer_agent.generate_interview(
                    project_analysis_str, code_review_summary
                )
                
                # Validate exactly 10 questions (STRICT backend validation)
                if interview_result is None or not hasattr(interview_result, 'questions'):
                    raise ValueError(
                        "Interview agent returned invalid result. Expected InterviewSession object."
                    )
                
                if len(interview_result.questions) != 10:
                    raise ValueError(
                        f"❌ Interview agent did not generate exactly 10 questions. Got {len(interview_result.questions)}. "
                        f"This indicates the LLM output was not properly validated or the prompt was not followed."
                    )
                
                results["interview"] = interview_result
                print(f"[PROCESS {review_id}] ✅ Interview generation done (10 questions)")
            
            except Exception as e:
                # 🔥 NEVER FAIL THE WHOLE REVIEW - graceful degradation
                print(f"[PROCESS {review_id}] ⚠️  Interview generation failed: {str(e)}")
                results["interview"] = {
                    "questions": [],
                    "total_questions": 0,
                    "categories_covered": [],
                    "error": f"Interview generation failed. {str(e)}"
                }
                print(f"[PROCESS {review_id}] ✅ Interview generation done (graceful fallback)")

        if review_type in ["full", "gaps"]:
            project_analysis_str = ""
            code_review_findings = ""
            technologies = []

            if "project_analysis" in results:
                project_analysis_str = f"Summary: {results['project_analysis'].summary}\nStructure: {results['project_analysis'].structure}"
                technologies = results['project_analysis'].technologies

            if "code_review" in results:
                code_review_findings = f"Weaknesses: {', '.join(results['code_review'].weaknesses)}\nRecommendations: {', '.join(results['code_review'].recommendations[:3])}"

            print(f"[PROCESS {review_id}] ⏳ Starting gap analysis...")
            results["gap_analysis"] = gap_agent.analyze_gaps(
                project_analysis_str, code_review_findings, technologies
            )
            print(f"[PROCESS {review_id}] ✅ Gap analysis done")

        # Update review status on SUCCESS
        print(f"[PROCESS {review_id}] ✅ All tasks completed successfully!")
        ongoing_reviews[review_id]["status"] = "completed"
        ongoing_reviews[review_id].update({
            "result": ReviewResponse(
                **results,
                timestamp=datetime.now().isoformat(),
                review_id=review_id
            ).model_dump(),
            "completed_at": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[PROCESS {review_id}] ❌ Error: {str(e)}")
        # Update review status on ERROR (ALWAYS)
        ongoing_reviews[review_id]["status"] = "error"
        ongoing_reviews[review_id].update({
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })
    
    finally:
        # 🔒 FINAL SAFETY: Guarantee status is set (never stuck)
        if ongoing_reviews[review_id]["status"] == "processing":
            print(f"[PROCESS {review_id}] ⚠️  WARNING: Status still 'processing' in finally block. Forcing to 'error'.")
            ongoing_reviews[review_id]["status"] = "error"
            ongoing_reviews[review_id]["error"] = "Review process did not complete properly"
            ongoing_reviews[review_id]["completed_at"] = datetime.now().isoformat()
        
        print(f"[PROCESS {review_id}] Final status: {ongoing_reviews[review_id]['status']}")


@router.get("/health")
def health_check():
    """Health check endpoint (SYNC)."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
