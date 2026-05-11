import json
import streamlit as st
import requests
import time
from typing import Optional, Dict, Any

st.set_page_config(
    page_title="Project Analysis - AI Project Reviewer",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if "api_url" not in st.session_state:
    st.session_state["api_url"] = "http://localhost:8000/api"

st.title("📊 Project Analysis")

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
    except Exception as e:
        return None


def parse_json_string(value: str) -> Optional[Dict[str, Any]]:
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None
    return None


def normalize_string_list(value):
    if isinstance(value, str):
        clean = value.strip()
        if clean.startswith('[') and clean.endswith(']'):
            try:
                parsed = json.loads(clean)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in clean.replace('[', '').replace(']', '').replace('"', '').split(',') if item.strip()]
    return value


def display_project_analysis(analysis: Dict[str, Any]):
    """Display project analysis results"""
    if not analysis:
        st.info("No project analysis available")
        return

    # Summary may come back as a JSON string
    summary_value = analysis.get('summary')
    parsed_summary = parse_json_string(summary_value)
    if parsed_summary:
        analysis = {**analysis, **parsed_summary}

    summary = analysis.get('summary', 'N/A')
    if isinstance(summary, dict) and 'summary' in summary:
        summary = summary['summary']

    if summary and summary != 'N/A':
        st.markdown("### Summary")
        if isinstance(summary, (dict, list)):
            st.json(summary)
        else:
            st.write(summary)

    # Complexity
    complexity = analysis.get('complexity', 'N/A')
    if complexity and complexity != 'N/A':
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Complexity", complexity)

    # Technologies
    techs = normalize_string_list(analysis.get("technologies", []))
    if techs and len(techs) > 0:
        st.markdown("### 🛠️ Technologies Used")
        for tech in techs:
            st.write(f"• {tech}")

    # Key Components
    components = normalize_string_list(analysis.get("key_components", []))
    if components and len(components) > 0:
        st.markdown("### 📦 Key Components")
        for c in components:
            st.write(f"• {c}")
    else:
        st.info("No key components identified")

    # Structure
    structure = analysis.get("structure", {})
    if isinstance(structure, str):
        parsed_structure = parse_json_string(structure)
        if parsed_structure:
            structure = parsed_structure

    if structure:
        st.markdown("### 📂 Project Structure")
        if isinstance(structure, dict):
            for key, value in structure.items():
                if isinstance(value, (dict, list)):
                    st.write(f"**{key}:**")
                    st.json(value)
                else:
                    st.write(f"**{key}:** {value}")


# Main content
if not st.session_state.get("review_id"):
    st.warning("⚠️ No project is being analyzed. Please go to the Home page and submit a project first.")
else:
    review_id = st.session_state.get("review_id")
    progress_bar = st.progress(0)
    status_container = st.container()
    
    with status_container:
        st.info("⏳ Fetching project analysis...")
    
    # Poll for results
    max_retries = 50
    retry_count = 0
    data = None
    
    while retry_count < max_retries:
        data = get_review_status(review_id)
        
        if data:
            status = data.get("status")
            
            if status == "completed":
                progress_bar.progress(100)
                with status_container:
                    st.success("✅ Analysis completed!")
                
                review = data.get("review", {})
                st.session_state["review_data"] = review
                
                analysis = review.get("project_analysis")
                display_project_analysis(analysis)
                
                st.markdown("---")
                
                # Navigation to next page
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🏠 Back to Home", use_container_width=True):
                        st.session_state["project_path"] = ""
                        st.session_state["review_id"] = None
                        st.rerun()
                
                with col2:
                    if st.button("➡️ Code Review →", type="primary", use_container_width=True):
                        st.switch_page("pages/2_Code_Review.py")
                
                break
            
            elif status == "error":
                progress_bar.progress(0)
                with status_container:
                    st.error("❌ Analysis failed!")
                st.error(data.get("error", "Unknown error"))
                break
            
            else:
                progress = min(50 + (retry_count * 2), 95)
                progress_bar.progress(progress / 100)
                with status_container:
                    st.info(f"⏳ Analyzing project... ({retry_count * 0.8}s)")
        
        retry_count += 1
        time.sleep(0.8)
    
    if retry_count >= max_retries:
        progress_bar.progress(0)
        with status_container:
            st.error("❌ Analysis timed out. Please check if the backend is running.")
