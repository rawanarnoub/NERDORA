import streamlit as st
from dotenv import load_dotenv

from app.login import render_auth
from app.session import is_logged_in, logout, current_user
from db.database import init_db

load_dotenv()
init_db()

st.set_page_config(
    page_title="NerdoRA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_home() -> None:
    user = current_user()
    st.title("🧠 NerdoRA")
    st.caption("Your AI-powered study assistant")
    st.write(f"Welcome back, **{user['username']}** 👋")

    st.markdown(
        """
        ### What would you like to do today?
        Pick a tool from the sidebar:

        - 📘 **Explain** — break a topic down into beginner-friendly steps
        - 🧮 **Solve** — get worked solutions to exercises
        - 🃏 **Flashcards** — generate study cards from any topic or file
        - 📝 **Exam** — build a quiz with an answer key
        """
    )

    with st.sidebar:
        st.divider()
        if st.button("Log out", use_container_width=True):
            logout()
            st.rerun()


def main() -> None:
    if not is_logged_in():
        render_auth()
        return
    render_home()


if __name__ == "__main__":
    main()
