"""Entry point: streamlit run frontend/app.py"""
import sys
from pathlib import Path

import streamlit as st

# Make the local packages importable regardless of how the script is launched.
FRONTEND_DIR = str(Path(__file__).resolve().parent)
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

st.set_page_config(page_title="Document Intelligence", page_icon="📄",
                   layout="wide", initial_sidebar_state="expanded")

from core import session, state
from core.api import call
from ui import styles
from ui.components import topbar
from views import auth, chat, documents, sidebar, system

state.init()
styles.inject()

# A token issued during the previous run is written once the page is live.
pending = st.session_state.pop("_remember_token", None)
if pending:
    session.remember(pending)

if not session.restore():
    auth.render()
    st.stop()

topbar(st.session_state.page or "Workspace")

pages = ["Chat", "Documents"] + (["System"] if state.is_admin() else [])
if st.session_state.page not in pages:
    st.session_state.page = "Chat"

chats_result = call("GET", "/conversations/list")
chats = chats_result or []
if chats_result is not None:
    known = {c["id"] for c in chats}
    if st.session_state.chat_id is None:
        # A refresh (or a shared link) can point back at a conversation.
        try:
            requested = int(st.query_params.get("chat", ""))
        except (TypeError, ValueError):
            requested = None
        if requested in known:
            st.session_state.chat_id = requested
    elif st.session_state.chat_id not in known:
        st.session_state.chat_id = None
    if st.session_state.chat_id is not None:
        st.query_params["chat"] = str(st.session_state.chat_id)
    elif "chat" in st.query_params:
        del st.query_params["chat"]

docs_result = call("GET", "/documents")
docs = docs_result or []
doc_names = {d["id"]: d["filename"] for d in docs}

sidebar.render(chats, chats_result is not None)
state.show_notice()

page = st.session_state.page
if page == "Chat":
    chat.render(chats, docs, docs_result is not None, doc_names)
elif page == "Documents":
    documents.render(docs, docs_result is not None, doc_names)
else:
    system.render()
