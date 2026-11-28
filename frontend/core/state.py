"""Session-state defaults and small helpers."""
import streamlit as st

DEFAULTS = {
    "token": None, "role": None, "email": None,
    "chat_id": None, "page": "Chat",
    "last_metrics": {}, "notice": None,
    "pending_question": None,
    "auth_view": "Sign in", "auth_redirect": None,
    "_remember_token": None,
}


def init():
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def notify(message: str):
    """Show a success banner on the next run."""
    st.session_state.notice = message
    st.rerun()


def show_notice():
    if st.session_state.notice:
        st.success(st.session_state.notice)
        st.session_state.notice = None


def is_admin() -> bool:
    return st.session_state.role == "admin"
