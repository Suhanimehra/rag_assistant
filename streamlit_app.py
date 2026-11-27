"""Streamlit client for the Document Intelligence RAG API."""
import html
import os

import requests
import streamlit as st

API = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
st.set_page_config(
    page_title="Document Intelligence",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

for key, value in {
    "token": None,
    "role": None,
    "email": None,
    "chat_id": None,
    "page": "Chat",
    "last_metrics": {},
    "notice": None,
    "pending_question": None,
    "auth_view": "Sign in",
    "auth_redirect": None,
}.items():
    st.session_state.setdefault(key, value)


def escape(value) -> str:
    return html.escape(str(value), quote=True)


BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --ink: #0f172a;
  --muted: #64748b;
  --line: #e2e8f0;
  --surface: #ffffff;
  --canvas: #f5f7fb;
  --accent: #4f46e5;
  --accent-soft: #eef2ff;
  --sidebar: #0b1220;
  --sidebar-line: #1e293b;
}

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stAppViewContainer"] { background: var(--canvas); }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"], footer {
  visibility: hidden;
  height: 0;
}
.block-container { padding: 1.4rem 2.2rem 3rem; max-width: 1180px; }

h1, h2, h3, h4 { color: var(--ink); letter-spacing: -0.02em; }
p, li, label { color: var(--ink); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {
  background: var(--sidebar);
  border-right: 1px solid var(--sidebar-line);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 1rem 0.85rem 1.2rem;
}
[data-testid="stSidebar"] * { color: #cbd5e1; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f8fafc; }
[data-testid="stSidebar"] input {
  background: #111c31 !important;
  color: #e2e8f0 !important;
  border: 1px solid var(--sidebar-line) !important;
  border-radius: 9px !important;
}
[data-testid="stSidebar"] input::placeholder { color: #64748b !important; }
[data-testid="stSidebar"] .stButton > button {
  background: transparent;
  border: 1px solid transparent;
  color: #cbd5e1;
  justify-content: flex-start;
  text-align: left;
  border-radius: 9px;
  font-weight: 500;
  min-height: 2.2rem;
  padding: 0.35rem 0.55rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #17233b;
  color: #ffffff;
  border-color: #24324d;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
[data-testid="stSidebar"] button[kind="primary"] {
  background: #312e81;
  border-color: #4338ca;
  color: #eef2ff;
}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover,
[data-testid="stSidebar"] button[kind="primary"]:hover {
  background: #3730a3;
  border-color: #4f46e5;
  color: #ffffff;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
  color: #cbd5e1 !important;
}
[data-testid="stSidebarCollapsedControl"] {
  background: var(--sidebar);
  border-radius: 0 8px 8px 0;
}

/* ---------- buttons & inputs ---------- */
.stButton > button, .stFormSubmitButton > button, [data-testid="stPopover"] > button {
  border-radius: 10px;
  border: 1px solid var(--line);
  font-weight: 500;
  transition: all 0.15s ease;
}
.stButton > button:hover { border-color: #c7d2fe; color: var(--accent); }
[data-testid="stBaseButton-primary"], button[kind="primary"] {
  background: var(--accent);
  border-color: var(--accent);
  color: #ffffff;
}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover {
  background: #4338ca;
  border-color: #4338ca;
  color: #ffffff;
}
[data-testid="stTextInput"] input,
[data-testid="stMultiSelect"] div[data-baseweb="select"] {
  border-radius: 10px;
}

/* ---------- chat ---------- */
[data-testid="stChatMessage"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 0.85rem 1rem;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  margin-bottom: 0.6rem;
}
[data-testid="stChatMessageAvatarUser"] {
  background: var(--accent) !important;
  color: #ffffff !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: #0f172a !important;
  color: #ffffff !important;
}
[data-testid="stChatInput"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}
[data-testid="stChatInput"] textarea { background: transparent; }

/* ---------- custom blocks ---------- */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.1rem 0 1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.15rem;
}
.eyebrow {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--muted);
}
.page-title {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
  margin-top: 0.12rem;
}
.topbar-user { display: flex; align-items: center; gap: 0.65rem; }
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--accent-soft);
  color: var(--accent);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex: none;
}
.user-name { font-size: 0.84rem; font-weight: 600; color: var(--ink); }
.user-role { font-size: 0.72rem; color: var(--muted); }

.brand { display: flex; align-items: center; gap: 0.6rem; padding: 0.15rem 0.2rem 0.9rem; }
.brand-mark {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.05rem;
  flex: none;
}
.brand-name { font-weight: 700; color: #f8fafc; font-size: 0.96rem; letter-spacing: -0.01em; }
.brand-sub { font-size: 0.68rem; color: #94a3b8; }
.section-label {
  font-size: 0.66rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #64748b;
  margin: 0.95rem 0.25rem 0.4rem;
}
.sidebar-empty { font-size: 0.78rem; color: #64748b; padding: 0.3rem 0.35rem; }

.user-card {
  background: #111c31;
  border: 1px solid var(--sidebar-line);
  border-radius: 12px;
  padding: 0.7rem;
  display: flex;
  gap: 0.6rem;
  align-items: center;
  margin-top: 0.45rem;
}
.user-card .avatar { background: #312e81; color: #c7d2fe; }
.user-card .user-name { color: #e2e8f0; }
.user-card .user-role { color: #94a3b8; }

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
  gap: 0.8rem;
  margin: 0.2rem 0 1.15rem;
}
.metric-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.9rem 1rem;
}
.metric-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
.metric-value { font-size: 1.45rem; font-weight: 700; color: var(--ink); margin-top: 0.2rem; }
.metric-note { font-size: 0.74rem; color: var(--muted); }

.source-card {
  background: #f8fafc;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
  margin: 0.45rem 0;
}
.source-head { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.35rem; }
.source-id {
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.68rem;
  font-weight: 700;
  padding: 0.14rem 0.42rem;
  border-radius: 6px;
}
.source-name { font-size: 0.82rem; font-weight: 600; color: var(--ink); }
.source-page {
  font-size: 0.68rem;
  color: var(--muted);
  background: #eef2f7;
  padding: 0.1rem 0.4rem;
  border-radius: 5px;
}
.source-excerpt { font-size: 0.81rem; line-height: 1.55; color: #475569; }

.empty-hero { text-align: center; padding: 2rem 1rem 1.2rem; }
.empty-hero .icon { font-size: 1.9rem; }
.empty-hero h2 { margin: 0.5rem 0 0.25rem; font-size: 1.35rem; }
.empty-hero p { color: var(--muted); font-size: 0.9rem; margin: 0 auto; max-width: 34rem; }

.doc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.62rem 0.9rem;
  margin: 0.4rem 0;
}
.doc-name { font-size: 0.87rem; font-weight: 500; color: var(--ink); }
.doc-meta { font-size: 0.71rem; color: var(--muted); }

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 0.22rem 0.55rem;
  border-radius: 999px;
  background: #ecfdf5;
  color: #047857;
}
.status-pill.warn { background: #fef3c7; color: #92400e; }
.status-pill.bad { background: #fee2e2; color: #b91c1c; }

/* ---------- auth ---------- */
.auth-hero { padding: 2.2rem 1rem 2.2rem 0.4rem; }
.auth-hero .brand-mark { width: 50px; height: 50px; border-radius: 14px; font-size: 1.35rem; }
.auth-hero h1 {
  font-size: 2.35rem;
  line-height: 1.12;
  margin: 0.75rem 0 0.65rem;
  letter-spacing: -0.035em;
}
.auth-hero > p {
  color: var(--muted);
  font-size: 0.96rem;
  line-height: 1.65;
  max-width: 30rem;
}
.feature-list { list-style: none; padding: 0; margin: 1.5rem 0 0; display: grid; gap: 0.65rem; }
.feature-list li { display: flex; gap: 0.6rem; align-items: flex-start; color: #334155; font-size: 0.87rem; }
.feature-icon {
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: var(--accent-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  flex: none;
}
.auth-card-title { font-size: 1.3rem; font-weight: 700; margin-bottom: 0.15rem; }
.auth-card-sub { color: var(--muted); font-size: 0.84rem; margin-bottom: 0.9rem; }
.auth-foot { text-align: center; color: var(--muted); font-size: 0.73rem; margin-top: 0.9rem; }

/* ---------- responsive ---------- */
@media (max-width: 900px) {
  .block-container { padding: 1rem 1rem 2rem; }
  .auth-hero { padding: 1rem 0; }
  .auth-hero h1 { font-size: 1.85rem; }
  .topbar-user .user-name { display: none; }
}
</style>
"""

AUTH_CSS = """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] { display: none !important; }
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(900px 500px at 8% 0%, #eef2ff 0%, rgba(238, 242, 255, 0) 60%),
    radial-gradient(700px 500px at 100% 100%, #f5f3ff 0%, rgba(245, 243, 255, 0) 55%),
    #f8fafc;
}
</style>
"""


def call(method, path, *, timeout=20, **kwargs):
    """Call the API and surface actionable errors without leaking tracebacks."""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    try:
        response = requests.request(method, API + path, headers=headers, timeout=timeout, **kwargs)
    except requests.Timeout:
        st.error("The server took too long to respond. Please try again.")
        return None
    except requests.ConnectionError:
        st.error("Cannot reach the API. Check that the backend is running on port 8000.")
        return None
    except requests.RequestException:
        st.error("The API request could not be completed. Please try again.")
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
            422: "Check the submitted values or the file format.",
            429: "Too many requests. Please wait and try again.",
            503: "The service is temporarily unavailable. Check the backend and Groq status.",
        }
        message = messages.get(
            status,
            "The backend could not complete this request. Check its terminal for details.",
        )
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


def new_chat():
    result = call("POST", "/conversations/start")
    if result:
        st.session_state.chat_id = result["conversation_id"]
        st.session_state.page = "Chat"
        st.rerun()


def sources_panel(sources):
    if not sources:
        return
    with st.expander(f"📚  {len(sources)} supporting source{'s' if len(sources) != 1 else ''}"):
        st.caption("Retrieved document evidence. Citations refer to these excerpts.")
        for source in sources:
            source_id = escape(source.get("source_id", "S"))
            name = escape(source.get("filename", "Document"))
            page = source.get("page")
            page_html = f'<span class="source-page">page {escape(page)}</span>' if page else ""
            excerpt = escape(source.get("excerpt", ""))
            st.markdown(
                f'<div class="source-card">'
                f'<div class="source-head"><span class="source-id">[{source_id}]</span>'
                f'<span class="source-name">{name}</span>{page_html}</div>'
                f'<div class="source-excerpt">{excerpt}</div></div>',
                unsafe_allow_html=True,
            )


def topbar(eyebrow, title):
    email = escape(st.session_state.email or "")
    initial = escape((st.session_state.email or "?")[0].upper())
    role = "Administrator" if st.session_state.role == "admin" else "Member"
    st.markdown(
        f'<div class="topbar">'
        f'<div><div class="eyebrow">{escape(eyebrow)}</div>'
        f'<div class="page-title">{escape(title)}</div></div>'
        f'<div class="topbar-user"><div class="avatar">{initial}</div>'
        f'<div><div class="user-name">{email}</div><div class="user-role">{role}</div></div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def auth_screen():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")

    with left:
        st.markdown(
            '<div class="auth-hero">'
            '<div class="brand-mark">📄</div>'
            '<div class="eyebrow" style="margin-top:1rem">DOCUMENT INTELLIGENCE</div>'
            '<h1>Ask your documents.<br/>Get grounded answers.</h1>'
            '<p>Upload reports, manuals and notes, then ask questions in plain language. '
            'Every answer is grounded in retrieved evidence with page-level citations.</p>'
            '<ul class="feature-list">'
            '<li><span class="feature-icon">🔍</span><span><b>Hybrid retrieval</b> across your indexed collection</span></li>'
            '<li><span class="feature-icon">📌</span><span><b>Page-level citations</b> for every answer</span></li>'
            '<li><span class="feature-icon">🔒</span><span><b>Private conversations</b> scoped to your account</span></li>'
            '</ul></div>',
            unsafe_allow_html=True,
        )

    with right:
        with st.container(border=True):
            if st.session_state.auth_redirect:
                st.session_state.auth_view = st.session_state.auth_redirect
                st.session_state.auth_redirect = None
            view = st.segmented_control(
                "Authentication",
                ["Sign in", "Create account"],
                key="auth_view",
                label_visibility="collapsed",
                width="stretch",
            )
            view = view or "Sign in"

            if st.session_state.notice:
                st.success(st.session_state.notice)
                st.session_state.notice = None

            if view == "Sign in":
                st.markdown(
                    '<div class="auth-card-title">Welcome back</div>'
                    '<div class="auth-card-sub">Sign in to continue to your workspace.</div>',
                    unsafe_allow_html=True,
                )
                with st.form("signin_form"):
                    email = st.text_input("Email", placeholder="you@company.com")
                    password = st.text_input("Password", type="password", placeholder="Your password")
                    submitted = st.form_submit_button("Sign in", type="primary", width="stretch")
                if submitted:
                    email = email.strip().lower()
                    if not email or not password:
                        st.error("Enter your email and password.")
                    elif "@" not in email:
                        st.error("Enter a valid email address.")
                    else:
                        with st.spinner("Signing in…"):
                            result = call("POST", "/login", data={"username": email, "password": password})
                        if result:
                            st.session_state.clear()
                            st.session_state.update(
                                token=result["access_token"],
                                role=result.get("role", "user"),
                                email=email,
                                page="Chat",
                            )
                            st.rerun()
            else:
                st.markdown(
                    '<div class="auth-card-title">Create your account</div>'
                    '<div class="auth-card-sub">Start asking questions in under a minute.</div>',
                    unsafe_allow_html=True,
                )
                with st.form("signup_form"):
                    name = st.text_input("Full name", placeholder="Ada Lovelace")
                    email = st.text_input("Email", placeholder="you@company.com")
                    password = st.text_input("Password", type="password", placeholder="At least 12 characters")
                    confirm = st.text_input("Confirm password", type="password", placeholder="Repeat your password")
                    submitted = st.form_submit_button("Create account", type="primary", width="stretch")
                if submitted:
                    name = name.strip()
                    email = email.strip().lower()
                    if not name:
                        st.error("Enter your full name.")
                    elif not email or "@" not in email:
                        st.error("Enter a valid email address.")
                    elif len(password) < 12:
                        st.error("Use at least 12 characters for your password.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    else:
                        with st.spinner("Creating your account…"):
                            result = call(
                                "POST",
                                "/register",
                                json={"username": name, "email": email, "password": password},
                            )
                        if result:
                            st.session_state.auth_redirect = "Sign in"
                            st.session_state.notice = "Account created. Sign in to continue."
                            st.rerun()

            st.markdown(
                '<div class="auth-foot">Protected workspace · Your conversations stay private</div>',
                unsafe_allow_html=True,
            )


def sidebar(chats, chats_result, is_admin):
    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-mark">📄</div>'
            '<div><div class="brand-name">Document Intelligence</div>'
            '<div class="brand-sub">Knowledge workspace</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("＋  New conversation", type="primary", width="stretch", key="sidebar_new_chat"):
            new_chat()

        search = st.text_input(
            "Search conversations",
            placeholder="Search conversations",
            label_visibility="collapsed",
            key="chat_search",
        )

        st.markdown('<div class="section-label">Workspace</div>', unsafe_allow_html=True)
        nav = [("💬", "Chat"), ("📚", "Documents")]
        if is_admin:
            nav.append(("⚙️", "System"))
        for icon, name in nav:
            active = st.session_state.page == name
            if st.button(
                f"{icon}  {name}",
                key=f"nav-{name}",
                width="stretch",
                type="primary" if active else "secondary",
            ):
                st.session_state.page = name
                st.rerun()

        st.markdown('<div class="section-label">Recent conversations</div>', unsafe_allow_html=True)
        if chats_result is None:
            st.markdown('<div class="sidebar-empty">Conversations unavailable.</div>', unsafe_allow_html=True)
        else:
            visible = [
                c for c in chats
                if search.casefold() in (c.get("title") or "Untitled").casefold()
            ] if search else chats
            if not visible:
                st.markdown(
                    '<div class="sidebar-empty">No conversations yet.</div>',
                    unsafe_allow_html=True,
                )
            for chat in visible[:40]:
                title = (chat.get("title") or "Untitled").strip()
                label = title[:34] + "…" if len(title) > 34 else title
                active = st.session_state.chat_id == chat["id"] and st.session_state.page == "Chat"
                if st.button(
                    ("●  " if active else "") + label,
                    key=f"chat-{chat['id']}",
                    width="stretch",
                    type="primary" if active else "secondary",
                ):
                    st.session_state.chat_id = chat["id"]
                    st.session_state.page = "Chat"
                    st.rerun()

        st.markdown('<div class="section-label">Account</div>', unsafe_allow_html=True)
        email = escape(st.session_state.email or "")
        initial = escape((st.session_state.email or "?")[0].upper())
        role = "Administrator" if is_admin else "Member"
        st.markdown(
            f'<div class="user-card"><div class="avatar">{initial}</div>'
            f'<div><div class="user-name">{email}</div>'
            f'<div class="user-role">{role}</div></div></div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign out", width="stretch", key="sidebar_signout"):
            call("POST", "/logout")
            st.session_state.clear()
            st.session_state["notice"] = "You have been signed out."
            st.rerun()


def chat_page(chats, chats_result, docs, docs_result, doc_names):
    current = next((c for c in chats if c["id"] == st.session_state.chat_id), None)
    topbar("Chat", (current.get("title") if current else None) or "New conversation")

    if st.session_state.chat_id is None:
        st.markdown(
            '<div class="empty-hero"><div class="icon">💬</div>'
            '<h2>Start a conversation</h2>'
            '<p>Create a chat, choose a scope, and ask anything about your indexed documents.</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("Start a new conversation", type="primary", key="start_chat_empty"):
            new_chat()
        return

    chat_id = st.session_state.chat_id
    with st.container(border=True):
        scope_col, new_col, options_col = st.columns([3.2, 1.1, 1.0], vertical_alignment="bottom")
        with scope_col:
            selected = st.multiselect(
                "Search scope",
                list(doc_names),
                format_func=doc_names.get,
                placeholder="All indexed documents",
                key=f"scope-{chat_id}",
            )
        with new_col:
            if st.button("＋ New chat", width="stretch", key="new_chat_control"):
                new_chat()
        with options_col:
            with st.popover("Options", width="stretch"):
                st.caption("Delete this conversation and all of its messages.")
                confirm = st.checkbox("Confirm deletion", key=f"confirm-delete-{chat_id}")
                if st.button(
                    "Delete conversation",
                    type="primary",
                    disabled=not confirm,
                    width="stretch",
                    key=f"delete-{chat_id}",
                ):
                    if call("DELETE", f"/conversations/delete/{chat_id}"):
                        st.session_state.chat_id = None
                        st.session_state.last_metrics.pop(chat_id, None)
                        notify("Conversation deleted.")

    messages = call("GET", f"/conversations/messages/{chat_id}")
    if messages is None:
        return

    if messages:
        for message in messages:
            role = message.get("role")
            role = role if role in {"user", "assistant"} else "assistant"
            with st.chat_message(role, avatar="user" if role == "user" else "assistant"):
                st.markdown(message.get("message", ""))
                sources_panel(message.get("sources") or [])
        metrics = st.session_state.last_metrics.get(chat_id)
        if metrics:
            st.caption(
                f"⚡ Retrieval {metrics['retrieval_ms'] / 1000:.2f}s · "
                f"Generation {metrics['generation_ms'] / 1000:.2f}s · "
                f"{len(metrics.get('sources') or [])} sources"
            )
            if metrics.get("insufficient_evidence"):
                st.info("The assistant reported insufficient document evidence for this question.")
    else:
        st.markdown(
            '<div class="empty-hero"><div class="icon">✨</div>'
            '<h2>Ask your first question</h2>'
            '<p>Answers are grounded in your indexed documents and include citations.</p></div>',
            unsafe_allow_html=True,
        )
        suggestions = [
            "Summarize the key topics covered in these documents.",
            "What are the main steps or recommendations?",
            "List the important terms and their definitions.",
            "Compare the topics covered across the documents.",
        ]
        columns = st.columns(2)
        for index, text in enumerate(suggestions):
            with columns[index % 2]:
                if st.button(text, key=f"suggest-{index}", width="stretch", disabled=not docs):
                    st.session_state.pending_question = text
                    st.rerun()

    if docs_result is not None and not docs:
        st.warning("No documents are indexed yet. An administrator can upload files from the Documents page.")

    question = st.chat_input("Ask about your documents…", max_chars=4000, disabled=not docs)
    if st.session_state.get("pending_question"):
        question = st.session_state.pop("pending_question")
    if question:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(question)
        with st.spinner("Retrieving evidence and drafting an answer…"):
            result = call(
                "POST",
                "/conversations/chat",
                timeout=300,
                json={
                    "conversation_id": chat_id,
                    "question": question,
                    "document_ids": selected or None,
                },
            )
        if result:
            st.session_state.last_metrics[chat_id] = result
            st.rerun()


def documents_page(docs, docs_result, doc_names, is_admin):
    topbar("Workspace", "Knowledge base")

    jobs = (call("GET", "/ingest/jobs") or []) if is_admin else []
    ready = len(docs) if docs_result is not None else 0
    pending = sum(1 for job in jobs if job.get("status") in ("pending", "processing"))
    failed = sum(1 for job in jobs if job.get("status") == "failed")
    st.markdown(
        f'<div class="metric-grid">'
        f'<div class="metric-card"><div class="metric-label">Indexed documents</div>'
        f'<div class="metric-value">{ready}</div><div class="metric-note">Shared with all members</div></div>'
        f'<div class="metric-card"><div class="metric-label">In progress</div>'
        f'<div class="metric-value">{pending}</div><div class="metric-note">Ingestion jobs</div></div>'
        f'<div class="metric-card"><div class="metric-label">Needs attention</div>'
        f'<div class="metric-value">{failed}</div><div class="metric-note">Failed jobs</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if is_admin:
        with st.container(border=True):
            st.markdown(
                '<div class="auth-card-title" style="font-size:1.05rem">Add documents</div>'
                '<div class="auth-card-sub">PDF, TXT, Markdown or CSV. Files are queued for background indexing.</div>',
                unsafe_allow_html=True,
            )
            files = st.file_uploader(
                "Upload documents",
                type=["pdf", "txt", "md", "csv"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )
            if files:
                st.caption(f"{len(files)} file{'s' if len(files) != 1 else ''} selected")
            if st.button(
                "Queue for indexing",
                type="primary",
                disabled=not files,
                width="stretch",
                key="queue_upload",
            ):
                queued = 0
                with st.spinner("Submitting documents…"):
                    for file in files:
                        result = call(
                            "POST",
                            "/upload",
                            timeout=90,
                            files={"file": (file.name, file.getvalue(), file.type)},
                        )
                        if result:
                            queued += 1
                if queued:
                    notify(f"Queued {queued} of {len(files)} document(s) for indexing.")

        st.markdown('<div class="section-label">Ingestion jobs</div>', unsafe_allow_html=True)
        if st.button("Refresh jobs", key="refresh_jobs"):
            st.rerun()
        if jobs:
            rows = [
                {
                    "Job": job.get("job_id"),
                    "Document": job.get("filename"),
                    "Status": str(job.get("status", "")).capitalize(),
                    "Chunks": job.get("chunks_stored") or "",
                    "Error": job.get("error") or "",
                }
                for job in jobs
            ]
            st.dataframe(rows, hide_index=True, width="stretch")
        else:
            st.caption("No ingestion jobs yet.")

    st.markdown('<div class="section-label">Indexed collection</div>', unsafe_allow_html=True)
    if docs:
        for doc in docs:
            st.markdown(
                f'<div class="doc-row"><div>'
                f'<div class="doc-name">📄 {escape(doc.get("filename", "Document"))}</div>'
                f'<div class="doc-meta">Document #{escape(doc.get("id"))}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        if is_admin:
            with st.expander("Remove a document"):
                st.warning("Removing a document deletes it and its indexed chunks for everyone.")
                delete_id = st.selectbox(
                    "Document",
                    list(doc_names),
                    format_func=doc_names.get,
                    key="delete_document_id",
                )
                confirm = st.checkbox("I understand this cannot be undone", key="confirm_document")
                if st.button(
                    "Remove document",
                    type="primary",
                    disabled=not confirm,
                    key="remove_document",
                ):
                    if call("DELETE", f"/documents/{delete_id}"):
                        notify("Document removed.")
    elif docs_result is not None:
        st.info("No documents indexed yet. Administrators can upload files above.")


def system_page():
    topbar("Administration", "System status")
    status = call("GET", "/system/status", timeout=5)
    if status:
        api_ok = str(status.get("status", "")).lower() == "healthy"
        db_ok = str(status.get("database", "")).lower() == "connected"
        st.markdown(
            f'<div class="metric-grid">'
            f'<div class="metric-card"><div class="metric-label">API</div>'
            f'<div class="metric-value">{"Operational" if api_ok else escape(status.get("status", "Unknown"))}</div>'
            f'<div class="metric-note">{"FastAPI is responding" if api_ok else "Check the API container"}</div></div>'
            f'<div class="metric-card"><div class="metric-label">Database</div>'
            f'<div class="metric-value">{"Connected" if db_ok else escape(status.get("database", "Unknown"))}</div>'
            f'<div class="metric-note">PostgreSQL with pgvector</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.caption(f"API endpoint: {API}")
    st.info("Health checks confirm database connectivity, not model inference. Keep the API and ingestion worker running.")
    with st.expander("Retrieval settings"):
        st.write("Hybrid search, reranking, query rewriting and chunking are configured in the backend environment.")
        st.code(
            "ENABLE_HYBRID=true\nENABLE_RERANKING=false\nENABLE_QUERY_REWRITING=true",
            language="dotenv",
        )
    if st.button("Refresh status", key="refresh_status"):
        st.rerun()


if not st.session_state.token:
    auth_screen()
    st.stop()

st.markdown(BASE_CSS, unsafe_allow_html=True)

is_admin = st.session_state.role == "admin"
allowed_pages = ["Chat", "Documents"] + (["System"] if is_admin else [])
if st.session_state.page not in allowed_pages:
    st.session_state.page = "Chat"

chats_result = call("GET", "/conversations/list")
chats = chats_result or []
if (
    st.session_state.chat_id is not None
    and chats_result is not None
    and not any(chat["id"] == st.session_state.chat_id for chat in chats)
):
    st.session_state.chat_id = None

docs_result = call("GET", "/documents")
docs = docs_result or []
doc_names = {doc["id"]: doc["filename"] for doc in docs}

sidebar(chats, chats_result, is_admin)

if st.session_state.notice:
    st.success(st.session_state.notice)
    st.session_state.notice = None

if st.session_state.page == "Chat":
    chat_page(chats, chats_result, docs, docs_result, doc_names)
elif st.session_state.page == "Documents":
    documents_page(docs, docs_result, doc_names, is_admin)
else:
    system_page()
