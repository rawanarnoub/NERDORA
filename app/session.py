import streamlit as st


def is_logged_in() -> bool:
    return bool(st.session_state.get("user"))


def current_user() -> dict | None:
    return st.session_state.get("user")


def login_user(user: dict) -> None:
    st.session_state["user"] = user


def logout() -> None:
    for key in ("user",):
        st.session_state.pop(key, None)


def require_login() -> dict:
    """Call at the top of any protected page. Stops execution if not logged in."""
    if not is_logged_in():
        st.warning("Please log in from the home page to continue.")
        st.stop()
    return current_user()
