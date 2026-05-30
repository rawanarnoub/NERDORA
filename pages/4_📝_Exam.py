import streamlit as st
from dotenv import load_dotenv

from app.session import require_login
from db.models import list_exams, save_exam
from utils.ai import chat
from utils.prompts import exam_prompt

load_dotenv()
user = require_login()

st.title("📝 Exam Generator")
st.caption("Build a quiz with an answer key, save it, and revisit later.")

tab_create, tab_history = st.tabs(["Create", "History"])

with tab_create:
    topic = st.text_input("Topic", placeholder="e.g. Newton's laws of motion")
    col1, col2, col3 = st.columns(3)
    difficulty = col1.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
    num_mcq = col2.number_input("MCQs", min_value=0, max_value=20, value=5)
    num_short = col3.number_input("Short-answer", min_value=0, max_value=10, value=2)

    if st.button("Generate exam", type="primary", disabled=not topic.strip()):
        if num_mcq + num_short == 0:
            st.error("Pick at least one MCQ or short-answer question.")
        else:
            system, prompt = exam_prompt(topic.strip(), difficulty, num_mcq, num_short)
            with st.spinner("Drafting your exam..."):
                try:
                    exam_md = chat(system, prompt, temperature=0.4, max_tokens=3000)
                except Exception as exc:
                    st.error(f"AI request failed: {exc}")
                    exam_md = ""
            if exam_md:
                st.session_state["pending_exam"] = {
                    "topic": topic.strip(),
                    "difficulty": difficulty,
                    "content_md": exam_md,
                }

    pending = st.session_state.get("pending_exam")
    if pending:
        st.divider()
        st.markdown(pending["content_md"])
        col_save, col_dl = st.columns(2)
        if col_save.button("💾 Save"):
            save_exam(
                user["id"],
                pending["topic"],
                pending["difficulty"],
                pending["content_md"],
            )
            st.success("Saved.")
            st.session_state.pop("pending_exam", None)
        col_dl.download_button(
            "⬇️ Download as Markdown",
            data=pending["content_md"],
            file_name=f"{pending['topic'].replace(' ', '_')}_exam.md",
            mime="text/markdown",
        )

with tab_history:
    exams = list_exams(user["id"])
    if not exams:
        st.info("No saved exams yet.")
    else:
        for exam in exams:
            with st.expander(
                f"{exam['topic']} — {exam['difficulty']} ({exam['created_at']})"
            ):
                st.markdown(exam["content_md"])
