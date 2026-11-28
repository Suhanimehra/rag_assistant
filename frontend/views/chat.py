"""Conversation page: a bounded chat panel plus a citation rail."""
import streamlit as st
from core.api import call, upload_documents
from core.config import ALLOWED_UPLOADS
from core.state import is_admin, notify
from ui.components import (
    doc_row,
    empty_state,
    escape,
    footnote,
    html_block,
    sources_panel,
)

SUGGESTIONS = [
    ("01", "Summarize the key takeaways"),
    ("02", "What are the main themes?"),
    ("03", "Which details should I pay attention to?"),
    ("04", "What questions does this document answer?"),
]


def _latest_sources(messages):
    for message in reversed(messages or []):
        if message.get("role") == "assistant" and message.get("sources"):
            return message["sources"]
    return []


def _history(messages):
    metrics = st.session_state.last_metrics.get(st.session_state.chat_id)
    for message in messages:
        role = message.get("role") if message.get("role") in {"user", "assistant"} else "assistant"
        with st.chat_message(role):
            st.markdown(message.get("message", ""))
            sources_panel(message.get("sources") or [])
    if metrics:
        seconds = (metrics["retrieval_ms"] + metrics["generation_ms"]) / 1000
        html_block(
            f'<div class="answer-meta">Answered in {seconds:.2f}s · '
            f'{len(metrics.get("sources") or [])} footnote(s)</div>'
        )
        if metrics.get("insufficient_evidence"):
            st.info("The selected documents don't contain enough evidence to answer fully.")


def _blank(docs):
    empty_state("¶", "What would you like to know?",
                "Ask a question, request a summary, or compare information across your documents.")
    html_block('<div class="suggestion-note">Start with one of these</div>')
    with st.container(key="suggestions"):
        columns = st.columns(2, gap="small")
        for index, (number, text) in enumerate(SUGGESTIONS):
            with columns[index % 2]:
                if st.button(f"{number} — {text}", key=f"suggest-{number}", width="stretch",
                             disabled=not docs):
                    st.session_state.pending_question = text
                    st.rerun()


def _ask(chat_id, selected, docs):
    question = st.chat_input(
        "Ask anything about your documents…", max_chars=4000,
        disabled=not docs, key=f"chat-input-{chat_id or 'new'}",
    )
    html_block('<div class="composer-hint"><span>Open the footnotes to check a claim.</span>'
               '<span>Enter to send · Shift + Enter for a new line</span></div>')
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


def _sources_side(docs, docs_ok, doc_names, scope_key, latest_sources):
    with st.container(key="sources-panel"):
        html_block(
            '<div class="rail-head"><div class="rail-title">Sources</div>'
            f'<div class="rail-sub">{len(docs)} indexed document'
            f'{"s" if len(docs) != 1 else ""} on this desk</div></div>'
        )
        selected = []
        if docs:
            html_block('<div class="rail-label">Scope</div>')
            selected = st.multiselect(
                "Limit search to", list(doc_names), format_func=doc_names.get,
                placeholder="Search the whole collection", label_visibility="collapsed", key=scope_key,
            )
            html_block('<div class="rail-label">On the desk</div>')
            for document in docs:
                doc_row(document.get("filename", "Document"), "Indexed", "Ready")
        elif docs_ok:
            html_block('<div class="rail-empty">No documents indexed yet.</div>')

        if is_admin():
            html_block('<hr class="rail-divider"/><div class="rail-label">Add a source</div>'
                       '<div class="rail-sub">PDF, TXT, Markdown or CSV · 20 MB per file.</div>')
            files = st.file_uploader("Upload", type=ALLOWED_UPLOADS, accept_multiple_files=True,
                                     label_visibility="collapsed", key="chat_document_upload")
            if files and st.button(f"Upload {len(files)} file{'s' if len(files) != 1 else ''}",
                                   type="primary", width="stretch", key="chat_upload_submit"):
                with st.spinner("Uploading…"):
                    queued = upload_documents(files)
                if queued:
                    notify(f"Queued {queued} document(s). They appear once indexing completes.")

        if latest_sources:
            html_block('<hr class="rail-divider"/><div class="rail-label">Latest footnotes</div>')
            for source in latest_sources[:4]:
                footnote(source)
    return selected


def render(chats, docs, docs_ok, doc_names):
    chat_id = st.session_state.chat_id
    current = next((c for c in chats if c["id"] == chat_id), None)
    messages = call("GET", f"/conversations/messages/{chat_id}") if chat_id is not None else None
    latest_sources = _latest_sources(messages)
    scope_key = f"document-scope-{chat_id or 'new'}"
    title = (current or {}).get("title") or "New conversation"
    ready = len(docs)
    ready_label = (f"{ready} source{'s' if ready != 1 else ''} ready" if ready
                   else "Waiting for sources")

    main, side = st.columns([0.7, 0.3], gap="large", vertical_alignment="top")
    with side:
        selected = _sources_side(docs, docs_ok, doc_names, scope_key, latest_sources)

    with main, st.container(key="chat-shell"):
        html_block(
            '<div class="chat-head">'
            '<div class="chat-head-main"><span class="eyebrow">Conversation</span>'
            f'<h1 class="chat-title">{escape(title)}</h1></div>'
            f'<span class="state-pill{" is-warn" if not ready else ""}">'
            f'{escape(ready_label)}</span></div>'
        )
        with st.container(key="chat-body"):
            if messages:
                _history(messages)
            else:
                _blank(docs)
        with st.container(key="chat-composer"):
            _ask(chat_id, selected, docs)
