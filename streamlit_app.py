import os
import requests
import streamlit as st

API = os.getenv("API_BASE", "http://127.0.0.1:8000")
st.set_page_config(page_title="Document Intelligence Assistant", layout="wide")
st.title("Document Intelligence Assistant")
for key, value in {"token": None, "role": None, "chat_id": None, "sources": []}.items():
    if key not in st.session_state:
        st.session_state[key] = value

def call(method, path, **kwargs):
    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
    try:
        response = requests.request(method, API + path, headers=headers, timeout=180, **kwargs)
        if response.status_code == 401 and st.session_state.token:
            st.session_state.token = None
            st.session_state.chat_id = None
            st.rerun()
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error("Request failed. Check the server and try again.")
        return None

if not st.session_state.token:
    mode = st.radio("Account", ["Login", "Register"], horizontal=True)
    with st.form("account"):
        username = st.text_input("Name") if mode == "Register" else ""
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button(mode):
            if mode == "Register":
                if call("POST", "/register", json={"username": username, "email": email, "password": password}):
                    st.success("Account created. Please log in.")
            else:
                result = call("POST", "/login", data={"username": email, "password": password})
                if result:
                    st.session_state.token = result["access_token"]
                    st.session_state.role = result["role"]
                    st.rerun()
    st.stop()

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
    if st.button("New chat"):
        result = call("POST", "/conversations/start")
        if result:
            st.session_state.chat_id = result["conversation_id"]
            st.session_state.sources = []
            st.rerun()
    for chat in call("GET", "/conversations/list") or []:
        if st.button(chat["title"], key=f"chat-{chat['id']}"):
            st.session_state.chat_id = chat["id"]
            st.session_state.sources = []
            st.rerun()
    if st.session_state.role == "admin":
        file = st.file_uploader("Add a document", type=["pdf","txt","md","csv"])
        if file and st.button("Index document"):
            with st.spinner("Extracting and indexing..."):
                result = call("POST", "/upload", files={"file": (file.name, file.getvalue(), file.type)})
                if result:
                    st.success(f"Queued ingestion job {result['job_id']}")
        if st.button("Refresh ingestion status"):
            st.rerun()
        for job in call("GET", "/ingest/jobs") or []:
            st.caption(f"{job['filename']}: {job['status']}")
    docs = call("GET", "/documents") or []
    selected = st.multiselect("Search these documents (empty = all)", docs, format_func=lambda d: d["filename"])
    if st.session_state.chat_id and st.button("Delete current chat"):
        if call("DELETE", f"/conversations/delete/{st.session_state.chat_id}"):
            st.session_state.chat_id = None
            st.session_state.sources = []
            st.rerun()

if not st.session_state.chat_id:
    st.info("Start a new chat to explore the knowledge base.")
    st.stop()
for message in call("GET", f"/conversations/messages/{st.session_state.chat_id}") or []:
    with st.chat_message(message["role"]):
        st.markdown(message["message"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.caption(f"[{source['source_id']}] {source['filename']} — page {source['page'] or 'N/A'}")
                    st.write(source["excerpt"])
if question := st.chat_input("Ask a question about your documents"):
    with st.spinner("Retrieving evidence and generating an answer..."):
        result = call("POST", "/conversations/chat", json={"conversation_id": st.session_state.chat_id,
            "question": question, "document_ids": [d["id"] for d in selected] or None})
        if result:
            st.session_state.sources = result["sources"]
            st.rerun()
if st.session_state.sources:
    with st.expander("Retrieved evidence", expanded=True):
        for source in st.session_state.sources:
            st.write(f"[{source['source_id']}] {source['filename']} — page {source['page'] or 'N/A'}")
            st.caption(source["excerpt"])
