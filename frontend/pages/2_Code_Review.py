import streamlit as st
import requests
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Code Review - AI Project Reviewer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state["api_url"] = "http://localhost:8000/api"

st.title("🔍 Code Review")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.session_state["api_url"] = st.text_input(
        "API Base URL",
        value=st.session_state.get("api_url", "http://localhost:8000/api")
    )
    
    st.markdown("---")
    if st.session_state.get("project_path"):
        st.markdown(f"**Project:** `{st.session_state['project_path']}`")

# Helper functions
def get_review_status(review_id: str) -> Optional[Dict[str, Any]]:
    """Get the status of a review"""
    api_url = st.session_state.get("api_url", "http://localhost:8000/api")
    try:
        res = requests.get(f"{api_url}/review/{review_id}", timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception:
        return None


def display_code_review(review: Dict[str, Any]):
    """Display code review results"""
    if not review:
        st.info("No code review available")
        return

    # Ratings
    col1, col2 = st.columns(2)
    
    with col1:
        rating = review.get('overall_rating')
        if rating is not None:
            st.metric("Overall Rating", f"{rating}/10")
        else:
            st.metric("Overall Rating", "N/A")

    with col2:
        quality_score = review.get('code_quality_score')
        if quality_score is not None:
            st.metric("Code Quality Score", f"{quality_score}/10")
        else:
            st.metric("Code Quality Score", "N/A")

    # Explanation about scores
    with st.expander("ℹ️ About the Scores", expanded=False):
        st.markdown("""
        **Score Interpretation:**
        - **1-3/10**: Poor code quality, significant issues
        - **4-5/10**: Below average, needs improvement
        - **6-7/10**: Good code, some improvements needed
        - **8-9/10**: Excellent code quality
        - **10/10**: Exceptional code quality
        
        The scores are based on:
        - Code structure and organization
        - Error handling and robustness
        - Documentation and comments
        - Best practices adherence
        - Performance considerations
        - Security practices
        """)

    st.markdown("---")

    # Strengths
    if review.get("strengths") and len(review["strengths"]) > 0:
        st.markdown("### ✅ Strengths")
        for s in review["strengths"]:
            st.write(f"• {s}")

    # Weaknesses
    if review.get("weaknesses") and len(review["weaknesses"]) > 0:
        st.markdown("### ⚠️ Weaknesses")
        for w in review["weaknesses"]:
            st.write(f"• {w}")

    # Recommendations
    if review.get("recommendations") and len(review["recommendations"]) > 0:
        st.markdown("### 💡 Recommendations")
        for r in review["recommendations"]:
            if len(r) > 500:
                with st.expander("📖 View detailed recommendation"):
                    st.write(r)
            else:
                st.write(f"• {r}")

    # Critical Issues
    if review.get("critical_issues") and len(review["critical_issues"]) > 0:
        st.markdown("### 🚨 Critical Issues")
        for issue in review["critical_issues"]:
            st.error(f"• {issue}")


# Main content
if not st.session_state.get("review_id"):
    st.warning("⚠️ No project is being analyzed. Please go to the Home page and submit a project first.")
else:
    review_id = st.session_state.get("review_id")
    
    # Try to get cached data first
    if st.session_state.get("review_data"):
        review = st.session_state["review_data"]
        code_review = review.get("code_review")
        display_code_review(code_review)
    else:
        # Fetch from API
        st.info("⏳ Fetching code review...")
        data = get_review_status(review_id)
        
        if data and data.get("status") == "completed":
            review = data.get("review", {})
            st.session_state["review_data"] = review
            code_review = review.get("code_review")
            display_code_review(code_review)
        else:
            st.warning("⏳ Analysis not completed yet. Please check back in a moment.")

    st.markdown("---")
    
    # Navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬅️ Project Analysis", use_container_width=True):
            st.switch_page("pages/1_Project_Analysis.py")
    
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state["project_path"] = ""
            st.session_state["review_id"] = None
            st.rerun()
    
    with col3:
        if st.button("Interview Questions →", type="primary", use_container_width=True):
            st.switch_page("pages/3_Interview_Questions.py")
