import streamlit as st

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Gap Analysis",
    page_icon="🧩",
    layout="wide"
)

# ---------------- GET REVIEW DATA ---------------- #

review_data = st.session_state.get("review_data", {})

gap_analysis = review_data.get("gap_analysis", {})

# ---------------- TITLE ---------------- #

st.title("🧩 Gap Analysis")

# ---------------- PRIORITY ---------------- #

priority = gap_analysis.get("priority_level", "N/A")

st.markdown(f"## 🔴 Priority Level: {priority}")

st.markdown("---")

# ---------------- IDENTIFIED GAPS ---------------- #

st.markdown("## 📌 Identified Gaps")

identified_gaps = gap_analysis.get("identified_gaps", [])

for index, gap in enumerate(identified_gaps, start=1):

    with st.expander(f"Gap {index}: {gap.get('title')}"):

        st.markdown(f"**Reason:** {gap.get('reason')}")

        st.markdown(f"**Impact:** {gap.get('impact')}")

        st.markdown(f"**Priority:** {gap.get('priority')}")

# ---------------- MISSING FEATURES ---------------- #

st.markdown("---")

st.markdown("## 🧩 Missing Features")

missing_features = gap_analysis.get("missing_features", [])

for index, feature in enumerate(missing_features, start=1):

    with st.expander(f"Feature {index}: {feature.get('feature')}"):

        st.markdown(f"**Reason:** {feature.get('reason')}")

        st.markdown(f"**Solution:** {feature.get('solution')}")

# ---------------- IMPROVEMENTS ---------------- #

st.markdown("---")

st.markdown("## 🚀 Improvement Suggestions")

suggestions = gap_analysis.get("improvement_suggestions", [])

for suggestion in suggestions:

    st.markdown(f"- {suggestion}")

# ---------------- NAVIGATION ---------------- #

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    if st.button("⬅️ Interview Questions", use_container_width=True):
        st.switch_page("pages/3_Interview_Questions.py")

with col2:

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")