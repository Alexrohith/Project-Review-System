import json
import streamlit as st
import requests
import time
from typing import Optional, Dict, Any

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Project Analysis",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

/* Hide default Streamlit navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #F8F9FA;
}

/* Progress bar */
.stProgress > div > div > div > div {
    background-color: #4F46E5;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ---------------- #

if "api_url" not in st.session_state:
    st.session_state["api_url"] = "http://localhost:8000/api"

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.markdown("## app")

    st.page_link(
        "pages/1_Project_Analysis.py",
        label="Project Analysis"
    )

    st.page_link(
        "pages/2_Code_Review.py",
        label="Code Review"
    )

    st.page_link(
        "pages/3_Interview_Questions.py",
        label="Interview Questions"
    )

    st.page_link(
        "pages/4_Gap_Analysis.py",
        label="Gap Analysis"
    )

    st.markdown("---")

    st.header("⚙️ Configuration")

    st.session_state["api_url"] = st.text_input(
        "API Base URL",
        value=st.session_state["api_url"]
    )

    st.markdown("---")

    if st.session_state.get("project_path"):

        st.markdown("### 📁 Project")

        st.code(
            st.session_state["project_path"]
        )

# ---------------- TITLE ---------------- #

st.title("📊 Project Analysis")

st.caption(
    "AI-powered analysis of your software project."
)

st.markdown("---")

# ---------------- API FUNCTION ---------------- #

def get_review_status(review_id):

    api_url = st.session_state["api_url"]

    try:

        response = requests.get(
            f"{api_url}/review/{review_id}",
            timeout=5
        )

        response.raise_for_status()

        return response.json()

    except Exception:

        return None

# ---------------- DISPLAY FUNCTION ---------------- #

def display_project_analysis(analysis):

    if not analysis:

        st.info("No analysis available")

        return

    st.subheader("📌 Summary")

    st.write(
        analysis.get(
            "summary",
            "N/A"
        )
    )

    st.subheader("🛠 Technologies")

    technologies = analysis.get(
        "technologies",
        []
    )

    for tech in technologies:

        st.markdown(f"- {tech}")

    st.subheader("📂 Structure")

    structure = analysis.get(
        "structure",
        {}
    )

    if isinstance(structure, dict):

        st.write(
            structure.get(
                "overview",
                "N/A"
            )
        )

    st.subheader("⚡ Complexity")

    st.write(
        analysis.get(
            "complexity",
            "N/A"
        )
    )

    st.subheader("📦 Key Components")

    components = analysis.get(
        "key_components",
        []
    )

    for comp in components:

        st.markdown(f"- {comp}")

# ---------------- MAIN ---------------- #

review_id = st.session_state.get(
    "review_id"
)

if not review_id:

    st.warning(
        "No active review found."
    )

    st.stop()

# ---------------- LOADING ---------------- #

progress = st.progress(10)

status_box = st.info(
    "⏳ Fetching project analysis..."
)

data = None

# FAST POLLING

for i in range(15):

    progress.progress(min((i + 1) * 7, 95))

    data = get_review_status(review_id)

    if data:

        status = data.get("status")

        # COMPLETED

        if status == "completed":

            progress.progress(100)

            status_box.empty()

            st.success(
                "✅ Analysis completed successfully"
            )

            break

        # FAILED

        if status == "failed":

            st.error(
                data.get(
                    "error",
                    "Analysis failed"
                )
            )

            st.stop()

    time.sleep(0.3)

# ---------------- FINAL VALIDATION ---------------- #

if not data:

    st.error(
        "❌ Backend not responding."
    )

    st.stop()

status = data.get("status")

if status != "completed":

    st.warning(
        "⚠️ Analysis still processing."
    )

    st.stop()

# ---------------- STORE REVIEW ---------------- #

review = data.get(
    "review",
    {}
)

st.session_state["review_data"] = review

# ---------------- DISPLAY ---------------- #

analysis = review.get(
    "project_analysis",
    {}
)

display_project_analysis(
    analysis
)

# ---------------- NAVIGATION ---------------- #

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "🏠 New Analysis",
        use_container_width=True
    ):

        st.session_state["review_id"] = None

        st.switch_page("app.py")

with col2:

    if st.button(
        "➡️ Code Review",
        type="primary",
        use_container_width=True
    ):

        st.switch_page(
            "pages/2_Code_Review.py"
        )