import streamlit as st
import requests
import time
import os
from typing import Optional, Dict, Any

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Project Reviewer",
    page_icon="🔍",
    layout="wide"
)

DEFAULT_API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state["api_url"] = DEFAULT_API_BASE_URL
if "started" not in st.session_state:
    st.session_state["started"] = False


# ---------------- API HELPERS ----------------
def submit_review(project_path: str, review_type: str, include_analysis: bool) -> Optional[str]:
    api_url = st.session_state.get("api_url", DEFAULT_API_BASE_URL)
    try:
        res = requests.post(
            f"{api_url}/review",
            json={
                "project_path": project_path,
                "review_type": review_type,
                "include_analysis": include_analysis
            },
            timeout=15
        )
        res.raise_for_status()
        data = res.json()
        review_id = data.get("review_id")
        if not review_id:
            st.error("❌ No review ID returned from API")
            return None
        return review_id
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The API might be busy. Try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Could not connect to API at {api_url}. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"❌ Failed to submit review: {str(e)}")
        return None


def get_review_status(review_id: str, show_errors: bool = True) -> Optional[Dict[str, Any]]:
    api_url = st.session_state.get("api_url", DEFAULT_API_BASE_URL)
    try:
        res = requests.get(f"{api_url}/review/{review_id}", timeout=10)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.Timeout:
        if show_errors:
            st.error("❌ Status check timed out. The API might be busy. Retrying...")
        return None
    except requests.exceptions.ConnectionError:
        if show_errors:
            st.error("❌ Could not connect to API. Make sure the backend is running on " + api_url)
        return None
    except Exception as e:
        if show_errors:
            st.error(f"❌ Failed to fetch status: {str(e)}")
        return None


# ---------------- DISPLAY HELPERS ----------------
def display_project_analysis(analysis: Dict[str, Any]):
    if not analysis:
        st.info("No project analysis available")
        return

    st.subheader("📊 Project Analysis")

    summary = analysis.get('summary', 'N/A')
    if summary and summary != 'N/A':
        st.markdown(f"**Summary:** {summary}")
    else:
        st.warning("Summary not available")

    complexity = analysis.get('complexity', 'N/A')
    if complexity and complexity != 'N/A':
        st.markdown(f"**Complexity:** {complexity}")

    techs = analysis.get("technologies", [])
    if techs and len(techs) > 0:
        st.markdown("**Technologies Used:**")
        st.write(", ".join(techs))
    else:
        st.info("No technologies detected")

    components = analysis.get("key_components", [])
    if components and len(components) > 0:
        st.markdown("**Key Components:**")
        for c in components:
            st.write(f"• {c}")
    else:
        st.info("No key components identified")


def display_code_review(review: Dict[str, Any]):
    if not review:
        st.info("No code review available")
        return

    st.subheader("🔍 Code Review")

    rating = review.get('overall_rating')
    if rating is not None:
        st.metric("Overall Rating", f"{rating}/10")
    else:
        st.metric("Overall Rating", "N/A")

    quality_score = review.get('code_quality_score')
    if quality_score is not None:
        st.metric("Code Quality Score", f"{quality_score}/10")
    else:
        st.metric("Code Quality Score", "N/A")

    if review.get("strengths") and len(review["strengths"]) > 0:
        st.markdown("### ✅ Strengths")
        for s in review["strengths"]:
            st.write(f"• {s}")

    if review.get("weaknesses") and len(review["weaknesses"]) > 0:
        st.markdown("### ⚠️ Weaknesses")
        for w in review["weaknesses"]:
            st.write(f"• {w}")

    if review.get("recommendations") and len(review["recommendations"]) > 0:
        st.markdown("### 💡 Recommendations")
        for r in review["recommendations"]:
            # If it's a long text, display it in a scrollable area
            if len(r) > 500:
                st.text_area("Detailed Analysis", r, height=200, disabled=True)
            else:
                st.write(f"• {r}")

    if review.get("critical_issues") and len(review["critical_issues"]) > 0:
        st.markdown("### 🚨 Critical Issues")
        for issue in review["critical_issues"]:
            st.error(f"• {issue}")


def display_interview(interview: Dict[str, Any]):
    if not interview:
        st.info("No interview questions available")
        return

    st.subheader("🎯 Interview Questions")
    total_q = interview.get('total_questions', 0)
    st.write(f"**Total Questions:** {total_q}")
    
    # Defensive UI fallback
    if total_q < 10:
        st.warning(
            f"⚠️ Fewer interview questions generated ({total_q}/10). "
            "This may indicate an issue with question generation. Try regenerating the review."
        )

    for i, q in enumerate(interview.get("questions", []), 1):
        with st.expander(f"Question {i}"):
            st.write(q.get("question", "N/A"))
            st.write(f"**Category:** {q.get('category', 'N/A')}")
            st.write(f"**Difficulty:** {q.get('difficulty', 'N/A')}")
            if q.get("expected_answer"):
                st.markdown("**Expected Answer:**")
                st.write(q["expected_answer"])


def display_gap_analysis(gap: Dict[str, Any]):
    if not gap:
        st.info("No gap analysis available")
        return

    st.subheader("🧩 Gap Analysis")
    st.markdown(f"**Priority Level:** {gap.get('priority_level', 'N/A')}")

    if gap.get("identified_gaps"):
        st.markdown("### 🔎 Identified Gaps")
        for g in gap["identified_gaps"]:
            st.write(f"• {g}")

    if gap.get("missing_features") and len(gap["missing_features"]) > 0:
        st.markdown("### 🚫 Missing Features")
        for f in gap["missing_features"]:
            st.write(f"• {f}")

    if gap.get("improvement_suggestions"):
        st.markdown("### 🚀 Improvement Suggestions")
        for s in gap["improvement_suggestions"]:
            st.write(f"• {s}")


# ---------------- MAIN APP ----------------
def main():
    st.title("🔍 AI Project Reviewer")
    st.caption("AI-powered project understanding, review & interview prep")

    # -------- SIDEBAR --------
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.session_state["api_url"] = st.text_input(
            "API Base URL",
            value=st.session_state.get("api_url", DEFAULT_API_BASE_URL)
        )

        st.markdown("---")
        st.markdown("### Features")
        st.markdown("- Project Analysis")
        st.markdown("- Code Review")
        st.markdown("- Interview Questions")
        st.markdown("- Gap Analysis")

    # -------- INPUT SECTION --------
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Submit Project")

        project_path = st.text_input(
            "Project Path",
            placeholder="D:\\AI-Project-Reviewer"
        )

        review_type = st.selectbox(
            "Review Type",
            ["full", "code", "interview", "gaps"]
        )

        include_analysis = st.checkbox("Include Project Analysis", value=True)

        if st.button("🚀 Start Review", type="primary"):
            if not os.path.exists(project_path):
                st.error("❌ Project path does not exist")
                return

            with st.spinner("Submitting review..."):
                review_id = submit_review(project_path, review_type, include_analysis)

            if review_id:
                st.session_state["review_id"] = review_id
                st.session_state["started"] = True
                st.success(f"Review submitted (ID: {review_id})")
                # Remove st.rerun() to avoid potential issues
                st.info("🔄 Check status in the right panel")

    # -------- STATUS & RESULTS --------
    with col2:
        st.subheader("📋 Review Status")

        # Clear button
        if st.button("🗑️ Clear Results"):
            for key in ["review_id", "started"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        if st.session_state.get("started"):
            review_id = st.session_state.get("review_id")

            # Manual refresh button
            if st.button("🔄 Refresh Status"):
                st.rerun()

            progress = st.progress(0)
            status_box = st.empty()
            
            # Track elapsed time for timeout warning
            if "review_start_time" not in st.session_state:
                st.session_state["review_start_time"] = time.time()
            
            elapsed_seconds = time.time() - st.session_state["review_start_time"]

            # Get current status - with better error handling
            max_retries = 3
            data = None
            
            for attempt in range(max_retries):
                data = get_review_status(review_id, show_errors=(attempt == max_retries - 1))
                if data:
                    break
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait before retry

            if data:
                status = data.get("status")
                
                # Show timeout warning after 2 minutes
                if elapsed_seconds > 120 and status == "processing":
                    st.warning(
                        f"⏱️ Review is taking longer than expected ({int(elapsed_seconds // 60)} minutes). "
                        "You can refresh the status or try submitting again."
                    )

                if status == "completed":
                    progress.progress(100)
                    status_box.success("✅ Review Completed")
                    # Clear the start time on completion
                    if "review_start_time" in st.session_state:
                        del st.session_state["review_start_time"]

                    review = data.get("review", {})

                    # ---- TABS ----
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Project Analysis",
                        "🔍 Code Review",
                        "🎯 Interview",
                        "🧩 Gap Analysis"
                    ])

                    with tab1:
                        display_project_analysis(review.get("project_analysis"))

                    with tab2:
                        display_code_review(review.get("code_review"))

                    with tab3:
                        display_interview(review.get("interview"))

                    with tab4:
                        display_gap_analysis(review.get("gap_analysis"))

                elif status == "error":
                    progress.progress(0)
                    status_box.error("❌ Review Failed")
                    st.error(data.get("error", "Unknown error"))

                else:
                    progress.progress(50)
                    status_box.info("🔄 Processing...")
                    st.info("Review is still being processed. Click '🔄 Refresh Status' to check progress.")
                    # Auto-refresh after 2 seconds
                    time.sleep(2)
                    st.rerun()
            else:
                status_box.error("❌ Could not fetch status")
                st.warning("Make sure the API server is running and the URL is correct.")
        else:
            st.info("Submit a project to view results")


if __name__ == "__main__":
    main()
