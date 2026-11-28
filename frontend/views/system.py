"""Admin-only system status."""
import streamlit as st
from core.api import call
from core.config import API
from ui.components import html_block, ledger, page_header


def render():
    page_header("Administration", "System status", "A quick read on the services behind the desk.")
    status = call("GET", "/system/status", timeout=5)
    if status:
        api_ok = str(status.get("status", "")).lower() == "healthy"
        db_ok = str(status.get("database", "")).lower() == "connected"
        ledger([
            ("API", "FastAPI is responding to health checks" if api_ok else "Check the API process",
             "Operational" if api_ok else status.get("status", "Unknown"),
             "" if api_ok else "is-bad"),
            ("Database", "PostgreSQL with pgvector",
             "Connected" if db_ok else status.get("database", "Unknown"),
             "" if db_ok else "is-bad"),
        ])
    else:
        st.error("The API did not respond. Check that the backend process is running.")
    html_block(f'<div class="panel-sub">Endpoint · <code>{API}</code></div>')
    st.info("Health checks confirm database connectivity, not model inference. "
            "Keep the API and ingestion worker running.")
    with st.expander("Retrieval settings"):
        st.write("Hybrid search, reranking, query rewriting and chunking are configured in the "
                 "backend environment.")
        st.code("ENABLE_HYBRID=true\nENABLE_RERANKING=false\nENABLE_QUERY_REWRITING=true",
                language="dotenv")
    if st.button("Refresh status", key="refresh_status"):
        st.rerun()
