import streamlit as st

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="Interview Questions",
    page_icon="💬",
    layout="wide"
)

# ---------------- GET REVIEW DATA ---------------- #

review_data = st.session_state.get("review_data", {})

questions = review_data.get("interview_questions", [])

# ---------------- TITLE ---------------- #

st.title("💬 Interview Questions")

# ---------------- QUESTIONS ---------------- #

if questions:

    st.markdown(f"### Total Questions: {len(questions)}")

    st.write("")

    for index, item in enumerate(questions, start=1):

        question = item.get("question", "Question")
        answer = item.get("answer", "No answer available")

        with st.expander(f"Question {index}"):

            st.markdown(f"### ❓ {question}")

            st.write(answer)

else:

    st.info("No interview questions available")

# ---------------- NAVIGATION ---------------- #

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button("⬅️ Code Review", use_container_width=True):
        st.switch_page("pages/2_Code_Review.py")

with col2:

    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")

with col3:

    if st.button("Gap Analysis ➜", use_container_width=True):
        st.switch_page("pages/4_Gap_Analysis.py")