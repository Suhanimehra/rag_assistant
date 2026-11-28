"""Conversation page: one centred column, message list scrolls, composer is pinned."""
import streamlit as st
from core.api import call, upload_documents
from core.config import ALLOWED_UPLOADS
from core.state import is_admin, notify
from ui.components import doc_row, empty_state, escape, html_block, scroll_to_bottom, sources_panel

SUGGESTIONS = [
    "Summarize the key takeaways",
    "What are the main themes?",
    "Which details should I pay attention to?",
    "What questions does this document answer?",
]


def _history(messages):
    for message in messages:
        role = message.get("role") if message.get("role") in {"user", "assistant"} else "assistant"
        with st.chat_message(role):
            st.markdown(message.get("message", ""))
            sources_panel(message.get("sources") or [])
    metrics = st.session_state.last_metrics.get(st.session_state.chat_id)
    if metrics:
        seconds = (metrics["retrieval_ms"] + metrics["generation_ms"]) / 1000
        html_block(f'<div class="answer-meta">Answered in {seconds:.2f}s · '
                   f'{len(metrics.get("sources") or [])} footnote(s)</div>')
        if metrics.get("insufficient_evidence"):
            st.info("The selected documents don't contain enough evidence to answer fully.")


def _blank(docs):
    empty_state("¶", "What would you like to know?",
                "Ask a question about your documents. Every answer links back to its source."
                if docs else "Add a document from Sources to get started.")
    with st.container(key="suggestions"):
        columns = st.columns(2, gap="small")
        for index, text in enumerate(SUGGESTIONS):
            with columns[index % 2]:
                if st.button(text, key=f"suggest-{index}", width="stretch", disabled=not docs):
                    st.session_state.pending_question = text
                    st.rerun()


def _sources_popover(docs, docs_ok, doc_names, scope_key):
    """Document scope and uploads live in a popover instead of a side rail."""
    selected = []
    with st.popover(f"Sources · {len(docs)}", icon=":material/folder_open:"):
        if docs:
            html_block('<div class="rail-label">Search in</div>')
            selected = st.multiselect(
                "Limit search to", list(doc_names), format_func=doc_names.get,
                placeholder="The whole collection", label_visibility="collapsed", key=scope_key,
            )
            for document in docs:
                doc_row(document.get("filename", "Document"), "Indexed", "Ready")
        elif docs_ok:
            html_block('<div class="rail-empty">No documents indexed yet.</div>')
        if is_admin():
            html_block('<div class="rail-label">Add a source</div>'
                       '<div class="rail-sub">PDF, TXT, Markdown or CSV · 20 MB per file.</div>')
            files = st.file_uploader("Upload", type=ALLOWED_UPLOADS, accept_multiple_files=True,
                                     label_visibility="collapsed", key="chat_document_upload")
            if files and st.button(f"Upload {len(files)} file{'s' if len(files) != 1 else ''}",
                                   type="primary", width="stretch", key="chat_upload_submit"):
                with st.spinner("Uploading…"):
                    queued = upload_documents(files)
                if queued:
                    notify(f"Queued {queued} document(s). They appear once indexing completes.")
    return selected


def _ask(chat_id, selected, docs):
    # Top level on purpose: Streamlit pins a root-level chat_input to the bottom.
    question = st.chat_input(
        "Ask anything about your documents…" if docs else "Add a document to start asking",
        max_chars=4000, disabled=not docs, key=f"chat-input-{chat_id or 'new'}",
    )
    if st.session_state.get("pending_question"):
        question = st.session_state.pop("pending_question")
    if not question:
        return
    with st.spinner("Reading your documents and drafting an answer…"):
        target = chat_id
        if target is None:
            created = call("POST", "/conversations/start")
            if not created:
                return
            target = created["conversation_id"]
            st.session_state.chat_id = target
            st.query_params["chat"] = str(target)
        result = call("POST", "/conversations/chat", timeout=300, json={
            "conversation_id": target, "question": question, "document_ids": selected or None,
        })
    if result:
        st.session_state.last_metrics[target] = result
        st.rerun()


def render(chats, docs, docs_ok, doc_names):
    chat_id = st.session_state.chat_id
    current = next((c for c in chats if c["id"] == chat_id), None)
    messages = call("GET", f"/conversations/messages/{chat_id}") if chat_id is not None else None
    title = (current or {}).get("title") or "New conversation"
    scope_key = f"document-scope-{chat_id or 'new'}"

    with st.container(key="chat-shell"):
        with st.container(key="chat-head"):
            html_block(f'<h1 class="chat-title">{escape(title)}</h1>')
            selected = _sources_popover(docs, docs_ok, doc_names, scope_key)
        with st.container(key="chat-body"):
            if messages:
                _history(messages)
            else:
                _blank(docs)
    _ask(chat_id, selected, docs)
    if messages:
        scroll_to_bottom()