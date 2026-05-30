import streamlit as st

from app.session import login_user
from db.models import create_user, get_user_by_username, verify_password


def render_auth() -> None:
    st.title("🧠 NerdoRA")
    st.caption("Sign in to keep your flashcards and exams saved.")

    tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", use_container_width=True)
        if submitted:
            user = get_user_by_username(username.strip())
            if user and verify_password(password, user["password_hash"]):
                login_user({"id": user["id"], "username": user["username"]})
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab_signup:
        with st.form("signup_form"):
            new_username = st.text_input("Choose a username", key="signup_username")
            new_password = st.text_input(
                "Choose a password", type="password", key="signup_password"
            )
            confirm = st.text_input(
                "Confirm password", type="password", key="signup_confirm"
            )
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if not new_username or not new_password:
                st.error("Username and password are required.")
            elif new_password != confirm:
                st.error("Passwords do not match.")
            elif get_user_by_username(new_username.strip()):
                st.error("Username already taken.")
            else:
                user_id = create_user(new_username.strip(), new_password)
                login_user({"id": user_id, "username": new_username.strip()})
                st.success("Account created!")
                st.rerun()
