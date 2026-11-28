"""Backend API client. Every view talks to the backend through here."""
import requests
import streamlit as st
from core import session
from core.config import API

ERRORS = {
    400: "The request was invalid.",
    401: "Incorrect email or password.",
    403: "You don't have permission to do this.",
    404: "That item could not be found.",
    409: "An account with this email already exists.",
    413: "The document exceeds the upload size limit.",
    422: "Check the values you entered or the file format.",
    429: "Too many requests. Wait a moment and try again.",
    503: "The service is temporarily unavailable. Check the backend and Groq status.",
}


def call(method, path, *, timeout=20, **kwargs):
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(method, API + path, headers=headers, timeout=timeout, **kwargs)
    except requests.Timeout:
        st.error("The server took too long to respond. Try again.")
        return None
    except requests.ConnectionError:
        st.error("Can't reach the API. Check that the backend is running on port 8000.")
        return None
    except requests.RequestException:
        st.error("The request could not be completed. Try again.")
        return None

    status = response.status_code
    if status == 401 and st.session_state.token:
        session.forget()
        st.session_state.clear()
        st.session_state["notice"] = "Your session expired. Sign in again."
        st.rerun()
    if not 200 <= status < 300:
        message = ERRORS.get(status, "The backend couldn't complete this request. Check its logs.")
        st.error(f"{message} (HTTP {status})")
        return None
    try:
        return response.json()
    except ValueError:
        st.error("The server returned an unexpected response.")
        return None


def probe_token(token: str):
    """Check a stored token without touching session state.

    Returns ``(status, profile)`` where status is ``"ok"``, ``"invalid"``,
    ``"offline"`` or ``"error"``. Used only when restoring a session.
    """
    try:
        response = requests.get(
            API + "/me", headers={"Authorization": f"Bearer {token}"}, timeout=10
        )
    except requests.RequestException:
        return "offline", None
    if response.status_code == 401:
        return "invalid", None
    if response.status_code != 200:
        return "error", None
    try:
        return "ok", response.json()
    except ValueError:
        return "error", None


def upload_documents(files) -> int:
    """Upload files for indexing. Returns how many were queued."""
    queued = 0
    for file in files:
        if call("POST", "/upload", timeout=90, files={"file": (file.name, file.getvalue(), file.type)}):
            queued += 1
    return queued
