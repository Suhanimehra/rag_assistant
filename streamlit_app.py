"""Minimal Streamlit client for the V2 document intelligence API."""
import os

import requests
import streamlit as st

API = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(page_title="Document Intelligence", page_icon="📄", layout="wide")

for key, value in {
    "token": None, "role": None, "email": None, "chat_id": None,
    "page": "Chat", "last_metrics": {}, "notice": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


if "pending_page" in st.session_state:
    st.session_state.page = st.session_state.pop("pending_page")


def call(method, path, *, timeout=20, **kwargs):
    """Display actionable errors without exposing credentials or server tracebacks."""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(method, API + path, headers=headers, timeout=timeout, **kwargs)
    except requests.Timeout:
        st.error("The server took too long to respond. Check the backend or Ollama terminal before retrying.")
        return None
    except requests.ConnectionError:
        st.error("Cannot reach FastAPI. Check that the backend is running on port 8000.")
        return None
    except requests.RequestException:
        st.error("The API request could not be completed. See the backend terminal.")
        return None

    status = response.status_code
    if status == 401 and st.session_state.token:
        st.session_state.clear()
        st.session_state["notice"] = "Your session expired. Please sign in again."
        st.rerun()
    if not 200 <= status < 300:
        messages = {
            400: "The request was invalid.",
            401: "Incorrect email or password.",
            403: "You do not have permission to perform this action.",
            404: "The requested item could not be found.",
            409: "An account with this email already exists.",
            413: "The document exceeds the upload size limit.",
            422: "Check the submitted values or supported document format.",
            429: "Too many requests. Wait before trying again.",
            503: "The service is temporarily unavailable. Check the backend and Ollama terminals.",
        }
        message = messages.get(status, "The backend could not complete this request. Check its terminal for the traceback.")
        st.error(f"{message} (HTTP {status})")
        return None
    try:
        return response.json()
    except ValueError:
        st.error("The server returned an unexpected response.")
        return None


def notify(message):
    st.session_state.notice = message
    st.rerun()


def sources_panel(sources):
    if not sources:
        return
    with st.expander(f"Sources · {len(sources)}", expanded=False):
        st.caption("Retrieved document evidence, not an independent verification of every claim.")
        for source in sources:
            label = source.get("source_id", "Source")
            name = source.get("filename", "Document")
            page = source.get("page")
            st.text(f"[{label}] {name}" + (f" · page {page}" if page else ""))
            st.write(source.get("excerpt", ""))
            st.divider()


def login_screen():
    _, center, _ = st.columns([1, 2, 1])
    with center:
        st.title("Document Intelligence")
        if st.session_state.notice:
            st.info(st.session_state.pop("notice"))
        signup = st.session_state.get("auth_view") == "signup"
        st.header("Create your account" if signup else "Sign in to your workspace")
        with st.form("signup_form" if signup else "signin_form", clear_on_submit=False):
            name = st.text_input("Full name") if signup else ""
            email = st.text_input("Email").strip()
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password") if signup else password
            submit = st.form_submit_button("Create account" if signup else "Sign in", type="primary", use_container_width=True)
        if submit:
            if not email or not password or (signup and not name.strip()):
                st.warning("Complete all required fields.")
            elif "@" not in email:
                st.warning("Enter a valid email address.")
            elif signup and len(password) < 12:
                st.warning("Use at least 12 characters.")
            elif signup and password != confirm:
                st.warning("Passwords do not match.")
            else:
                with st.spinner("Creating account…" if signup else "Signing in…"):
                    if signup:
                        result = call("POST", "/register", json={"username": name.strip(), "email": email, "password": password})
                    else:
                        result = call("POST", "/login", data={"username": email, "password": password})
                if result is not None:
                    if signup:
                        st.session_state.auth_view = "signin"
                        st.session_state.notice = "Account created. Please sign in."
                    else:
                        st.session_state.clear()
                        st.session_state.update(token=result["access_token"], role=result["role"], email=email, page="Chat")
                    st.rerun()
        if st.button("Already registered? Sign in" if signup else "New here? Create an account", use_container_width=True):
            st.session_state.auth_view = "signin" if signup else "signup"
            st.rerun()


def new_chat():
    result = call("POST", "/conversations/start")
    if result:
        st.session_state.chat_id = result["conversation_id"]
        st.session_state.pending_page = "Chat"
        st.rerun()


if not st.session_state.token:
    login_screen()
    st.stop()

is_admin = st.session_state.role == "admin"
allowed_pages = ["Chat", "Documents"] + (["System"] if is_admin else [])
if st.session_state.page not in allowed_pages:
    st.session_state.page = "Chat"

with st.sidebar:
    st.subheader("Document Intelligence")
    st.caption("Your knowledge workspace")
    st.radio("Workspace", allowed_pages, key="page", label_visibility="collapsed")
    st.divider()
    if st.button("＋ New conversation", type="primary", use_container_width=True):
        new_chat()
    chats_result = call("GET", "/conversations/list")
    chats = chats_result or []
    search = st.text_input("Find a conversation", placeholder="Search conversations", label_visibility="collapsed")
    st.caption("RECENT CONVERSATIONS")
    visible = [c for c in chats if search.casefold() in (c.get("title") or "Untitled").casefold()]
    if not visible:
        st.caption("No matching conversations." if search else "No conversations yet.")
    for chat in visible:
        label = chat.get("title") or "Untitled"
        active = st.session_state.chat_id == chat["id"]
        if st.button(("● " if active else "") + label, key=f"chat-{chat['id']}", use_container_width=True):
            st.session_state.chat_id = chat["id"]
            st.session_state.pending_page = "Chat"
            st.rerun()
    st.divider()
    if st.session_state.email:
        st.caption(st.session_state.email)
    st.caption("Administrator" if is_admin else "Member")
    if st.button("Sign out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = None

page = st.session_state.page
if page == "System":
    if not is_admin:
        st.error("Administrator access required.")
        st.stop()
    st.title("System status")
    st.caption("Verify that the services are reachable before using the assistant.")
    status = call("GET", "/system/status", timeout=5)
    if status:
        a, b = st.columns(2)
        a.metric("API", status.get("status", "Unknown").capitalize())
        b.metric("Database", status.get("database", "Unknown").capitalize())
    st.caption(f"API endpoint: {API}")
    st.info("The health endpoint checks database connectivity, not model inference. Keep the Ollama and ingestion worker processes running.")
    with st.expander("Retrieval settings"):
        st.write("Hybrid search, reranking, query rewriting and chunking are configured in the backend .env file. Restart relevant backend processes after changing them.")
        st.code("ENABLE_HYBRID=true\nENABLE_RERANKING=false\nENABLE_QUERY_REWRITING=true", language="dotenv")
    st.button("Refresh status")
    st.stop()

docs_result = call("GET", "/documents")
docs = docs_result or []
doc_names = {d["id"]: d["filename"] for d in docs}

if page == "Documents":
    st.title("Knowledge base")
    st.caption("Manage the shared collection of indexed documents.")
    st.metric("Indexed documents", len(docs) if docs_result is not None else "Unavailable")
    if is_admin:
        with st.container(border=True):
            st.subheader("Add documents")
            st.caption("PDF, TXT, Markdown and CSV · 20 MB default backend limit per file")
            files = st.file_uploader("Choose documents", type=["pdf", "txt", "md", "csv"], accept_multiple_files=True)
            if st.button("Queue for indexing", type="primary", disabled=not files):
                queued = 0
                with st.spinner("Submitting files…"):
                    for file in files:
                        result = call("POST", "/upload", timeout=90, files={"file": (file.name, file.getvalue(), file.type)})
                        if result:
                            queued += 1
                if queued:
                    st.success(f"Queued {queued} of {len(files)} document(s). Refresh jobs to check progress.")
        st.subheader("Ingestion jobs")
        st.caption("Runs in the background. Refresh to see the latest job status.")
        st.button("Refresh jobs")
        jobs = call("GET", "/ingest/jobs") or []
        if jobs:
            st.dataframe([{"Job": j["job_id"], "Document": j["filename"], "Status": j["status"].capitalize(),
                           "Chunks": j.get("chunks_stored"), "Error": j.get("error") or ""}
                          for j in jobs], hide_index=True, use_container_width=True)
        else:
            st.caption("No ingestion jobs.")
    st.subheader("Indexed collection")
    if docs:
        st.dataframe([{"ID": d["id"], "Document": d["filename"]} for d in docs], hide_index=True, use_container_width=True)
        if is_admin:
            with st.expander("Remove a document"):
                st.warning("Removal deletes the indexed document and its chunks from the shared collection.")
                delete_id = st.selectbox("Document", list(doc_names), format_func=doc_names.get, key="delete_document_id")
                confirm = st.checkbox("I want to remove this document", key="confirm_document")
                if st.button("Remove document", disabled=not confirm):
                    if call("DELETE", f"/documents/{delete_id}"):
                        notify("Document removed.")
    elif docs_result is not None:
        st.info("No indexed documents. Ask an administrator to add files." if not is_admin else "Upload a document to begin.")
    st.stop()

st.title("Chat")
if chats_result is not None and st.session_state.chat_id is not None and not any(
    c["id"] == st.session_state.chat_id for c in chats
):
    st.session_state.chat_id = None
current = next((c for c in chats if c["id"] == st.session_state.chat_id), None)

st.caption(current.get("title") if current else "Ask questions about your indexed knowledge base.")
selected = st.multiselect("Search scope", list(doc_names), format_func=doc_names.get,
                          placeholder="All indexed documents", help="Leave empty to search the entire collection.")

if st.session_state.chat_id is None:
    st.info("Start a new conversation to ask questions and explore your documents.")
    if st.button("Start conversation", type="primary"):
        new_chat()
    st.stop()

chat_id = st.session_state.chat_id
with st.expander("Conversation options"):
    confirm_chat = st.checkbox("Confirm deletion of this conversation", key=f"confirm-chat-{chat_id}")
    if st.button("Delete conversation", disabled=not confirm_chat):
        if call("DELETE", f"/conversations/delete/{chat_id}"):
            st.session_state.chat_id = None
            st.session_state.last_metrics.pop(chat_id, None)
            notify("Conversation deleted.")

messages = call("GET", f"/conversations/messages/{chat_id}")
if messages is None:
    st.stop()
if messages:
    for message in messages:
        role = message["role"] if message["role"] in {"user", "assistant"} else "assistant"
        with st.chat_message(role):
            st.markdown(message["message"])
            sources_panel(message.get("sources", []))
else:
    with st.container(border=True):
        st.subheader("Start with a question")
        st.write("Ask for an explanation, a fact, or a comparison supported by your documents.")
        st.caption("Example: What are the main topics covered in this document?")

metrics = st.session_state.last_metrics.get(chat_id)
if metrics:
    with st.expander("Latest response details"):
        a, b, c = st.columns(3)
        a.metric("Retrieval", f"{metrics['retrieval_ms'] / 1000:.2f} s")
        b.metric("Generation", f"{metrics['generation_ms'] / 1000:.2f} s")
        c.metric("Sources", len(metrics.get("sources", [])))
        if metrics.get("insufficient_evidence"):
            st.info("The assistant reported insufficient document evidence.")

if docs_result is not None and not docs:
    st.warning("Index at least one document before starting a question.")
question = st.chat_input("Ask about your documents…", max_chars=4000, disabled=not docs)
if question:
    with st.chat_message("user"):
        st.markdown(question)
    with st.spinner("Retrieving evidence and generating an answer…"):
        result = call("POST", "/conversations/chat", timeout=300, json={
            "conversation_id": chat_id, "question": question, "document_ids": selected or None})
        if result:
            st.session_state.last_metrics[chat_id] = result
            st.rerun()
        else:
            st.caption("If the request timed out, refresh the conversation before submitting it again.")
