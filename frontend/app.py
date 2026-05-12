import streamlit as st
import requests
import time
import os
from typing import Optional

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="AI Project Reviewer",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

/* Hide default Streamlit multipage navigation */
[data-testid="stSidebarNav"] {
    display: none;
}

/* Main spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Button styling */
.stButton > button {
    border-radius: 10px;
    height: 3rem;
    font-size: 17px;
    font-weight: 600;
}

/* Input styling */
.stTextInput input {
    border-radius: 10px !important;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #F8F9FA;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ---------------- #

if "api_url" not in st.session_state:
    st.session_state["api_url"] = "http://localhost:8000/api"

if "review_id" not in st.session_state:
    st.session_state["review_id"] = None

if "project_path" not in st.session_state:
    st.session_state["project_path"] = ""

# ---------------- SIDEBAR ---------------- #

with st.sidebar:

    st.subheader("⚙️ Settings")

    st.session_state["api_url"] = st.text_input(
        "Backend API URL",
        value=st.session_state["api_url"]
    )

    st.markdown("---")

    st.subheader("📌 Features")

    st.markdown("""
- AI Project Analysis
- Code Review
- Interview Preparation
- Gap Detection
- Tech Stack Insights
""")

# ---------------- MAIN PAGE ---------------- #

st.title("🚀 AI Project Reviewer")

st.caption(
    "Analyze software projects using AI-powered architecture and code review."
)

st.markdown("---")

# ---------------- PROJECT INPUT ---------------- #

st.markdown("## 📂 Select Your Project")

project_path = st.text_input(
    "Project Folder Path",
    placeholder="Enter project path (Example: D:\\MyProject)"
)

# ---------------- API FUNCTION ---------------- #

def submit_review(project_path: str) -> Optional[str]:

    api_url = st.session_state["api_url"]

    try:

        response = requests.post(
            f"{api_url}/review",
            json={
                "project_path": project_path,
                "review_type": "full",
                "include_analysis": True
            },
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data.get("review_id")

    except requests.exceptions.ConnectionError:
        st.error("❌ Unable to connect to backend API")
        return None

    except requests.exceptions.Timeout:
        st.error("❌ Request timeout. Try again.")
        return None

    except Exception as e:
        st.error(f"❌ {str(e)}")
        return None

# ---------------- ANALYZE BUTTON ---------------- #

if st.button("🚀 Analyze Project", use_container_width=True):

    if not project_path.strip():

        st.warning("⚠️ Please enter a valid project path.")

    elif not os.path.exists(project_path):

        st.error("❌ Project directory not found.")

    else:

        st.session_state["project_path"] = project_path

        st.markdown("### 🔍 Initializing Analysis")

        progress_bar = st.progress(0)

        status_text = st.info("⏳ Fetching project analysis...")

        for i in range(100):

            time.sleep(0.01)

            progress_bar.progress(i + 1)

        review_id = submit_review(project_path)

        if review_id:

            st.session_state["review_id"] = review_id

            status_text.empty()

            st.success("✅ Project Analysis Started Successfully")

            time.sleep(1)

            st.switch_page("pages/1_Project_Analysis.py")