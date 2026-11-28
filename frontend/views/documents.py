"""Knowledge base: upload, ingestion jobs, indexed collection."""
import streamlit as st
from core.api import call, upload_documents
from core.config import ALLOWED_UPLOADS
from core.state import is_admin, notify
from ui.components import doc_row, html_block, page_header, section, stat_strip


def _upload_card():
    with st.container(key="upload-card"):
        html_block('<div class="panel-title">Add to the collection</div>'
                   '<div class="panel-sub">PDF, TXT, Markdown or CSV · 20 MB per file. '
                   'Uploads are indexed in the background and become searchable when ready.</div>')
        files = st.file_uploader("Upload documents", type=ALLOWED_UPLOADS, accept_multiple_files=True,
                                 label_visibility="collapsed")
        if st.button("Queue for indexing", type="primary", disabled=not files,
                     width="stretch", key="queue_upload"):
            with st.spinner("Submitting documents…"):
                queued = upload_documents(files)
            if queued:
                notify(f"Queued {queued} of {len(files)} document(s) for indexing.")


def _jobs_table(jobs):
    section("Ingestion queue", len(jobs))
    if st.button("Refresh queue", key="refresh_jobs"):
        st.rerun()
    if not jobs:
        html_block('<div class="sidebar-empty">Nothing is being indexed right now.</div>')
        return
    st.dataframe([{
        "Job": job.get("job_id"), "Document": job.get("filename"),
        "Status": str(job.get("status", "")).capitalize(),
        "Chunks": job.get("chunks_stored") or "", "Error": job.get("error") or "",
    } for job in jobs], hide_index=True, width="stretch")


def _remove_document(doc_names):
    with st.expander("Remove a document"):
        st.warning("This deletes the document and its indexed chunks for everyone.")
        doc_id = st.selectbox("Document", list(doc_names), format_func=doc_names.get,
                              key="delete_document_id")
        sure = st.checkbox("I understand this can't be undone", key="confirm_document")
        if st.button("Remove document", type="primary", disabled=not sure,
                     key="remove_document") and call("DELETE", f"/documents/{doc_id}"):
            notify("Document removed.")


def render(docs, docs_ok, doc_names):
    jobs = (call("GET", "/ingest/jobs") or []) if is_admin() else []
    page_header(
        "Library", "Your documents",
        "Everything the desk can search, and the queue behind it.",
        status=(f"{len(docs)} indexed", "" if docs else "is-warn"),
    )
    stat_strip([
        ("Indexed", len(docs) if docs_ok else 0, "Available to every member"),
        ("In progress", sum(job.get("status") in ("pending", "processing") for job in jobs),
         "Running ingestion jobs"),
        ("Needs attention", sum(job.get("status") == "failed" for job in jobs), "Failed jobs"),
    ])
    if is_admin():
        _upload_card()
        html_block('<div style="height:14px"></div>')
        _jobs_table(jobs)

    section("Collection", len(docs) if docs_ok else None)
    if docs:
        for document in docs:
            doc_row(document.get("filename", "Document"), f"Document #{document.get('id')}", "Ready")
        if is_admin():
            _remove_document(doc_names)
    elif docs_ok:
        message = "The collection is empty."
        if is_admin():
            message += " Add the first document above."
        html_block(f'<div class="sidebar-empty">{message}</div>')
