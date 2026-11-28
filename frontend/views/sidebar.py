"""Left navigation: brand, new conversation, pages, history, account."""
from datetime import UTC, datetime

import streamlit as st
from core import session
from core.api import call
from core.state import is_admin
from ui.components import escape, html_block, section, wordmark_html


def start_new_chat():
    """Open a blank thread. The conversation is created on the first question."""
    st.session_state.chat_id = None
    st.session_state.page = "Chat"
    st.rerun()


def _nav_button(label, key, active, **state):
    if st.button(label, key=key, width="stretch", type="primary" if active else "secondary"):
        st.session_state.update(state)
        st.rerun()


def _bucket(chat) -> int:
    """0 today, 1 yesterday, 2 previous 7 days, 3 older."""
    try:
        when = datetime.fromisoformat(str(chat.get("created_at")))
    except (TypeError, ValueError):
        return 0
    if when.tzinfo is None:
        when = when.replace(tzinfo=UTC)
    days = (datetime.now(UTC).date() - when.astimezone(UTC).date()).days
    return 0 if days <= 0 else 1 if days == 1 else 2 if days < 7 else 3


def _history(chats):
    groups = [("Today", []), ("Yesterday", []), ("Previous 7 days", []), ("Older", [])]
    for chat in chats:
        groups[_bucket(chat)][1].append(chat)
    with st.container(key="chat-history"):
        for label, items in groups:
            if not items:
                continue
            html_block(f'<div class="history-label">{label}</div>')
            for chat in items:
                title = (chat.get("title") or "Untitled").strip()
                short = title[:80]
                active = st.session_state.chat_id == chat["id"] and st.session_state.page == "Chat"
                _nav_button(short, f"chat-{chat['id']}", active, chat_id=chat["id"], page="Chat")


def _account():
    with st.container(key="sidebar-account"):
        email = st.session_state.email or ""
        html_block(
            f'<div class="user-card"><div class="avatar">{escape(email[:1].upper() or "?")}</div>'
            f'<div><div class="user-name">{escape(email)}</div>'
            f'<div class="user-role">{"Administrator" if is_admin() else "Member"}</div></div></div>'
        )
        if st.button("Sign out", width="stretch", key="sidebar_signout"):
            call("POST", "/logout")
            session.forget()
            st.session_state.clear()
            if "chat" in st.query_params:
                del st.query_params["chat"]
            st.session_state["notice"] = "You have been signed out."
            st.rerun()


def render(chats, chats_ok):
    chats = [c for c in chats if (c.get("title") or "").strip() != "New Chat"]
    with st.sidebar:
        html_block(f'<div class="sidebar-brand">{wordmark_html()}</div>')
        if st.button("＋  New conversation", type="primary", width="stretch", key="sidebar_new_chat"):
            start_new_chat()

        pages = [("◈", "Chat"), ("▤", "Documents")] + ([("◎", "System")] if is_admin() else [])
        for glyph, name in pages:
            _nav_button(f"{glyph}   {name}", f"nav-{name}", st.session_state.page == name, page=name)

        section("Recent", len(chats) if chats_ok else None)
        st.text_input("Search conversations", placeholder="Search your chats",
                      label_visibility="collapsed", key="chat_search")
        if not chats_ok:
            html_block('<div class="sidebar-empty">Conversations are unavailable.</div>')
        else:
            needle = st.session_state.chat_search.casefold()
            visible = [c for c in chats if needle in (c.get("title") or "Untitled").casefold()]
            if visible:
                _history(visible[:200])
            else:
                html_block('<div class="sidebar-empty">'
                           + ("Nothing matches that search." if needle else "Your conversations will appear here.")
                           + '</div>')
        _account()