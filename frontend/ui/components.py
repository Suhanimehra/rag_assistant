"""HTML building blocks for the workspace interface."""
import html
import re

import streamlit as st

# Folded-page mark, drawn inline so the app needs no image assets.
LOGO_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M6 3.5h8.5L19 8v12.5H6z"/><path d="M14 3.5V8h5"/>'
    '<path d="M9 12.5h7M9 16h5"/></svg>'
)


def escape(value) -> str:
    return html.escape(str(value), quote=True)


def html_block(markup: str):
    st.markdown(markup, unsafe_allow_html=True)


def wordmark_html() -> str:
    return (
        f'<div class="masthead-brand"><span class="wordmark-mark">{LOGO_SVG}</span>'
        '<span class="wordmark-text">Document <em>Intelligence</em></span></div>'
    )


def topbar(current: str = "Workspace"):
    email = st.session_state.email or ""
    initial = escape((email[:1] or "?").upper())
    role = "Administrator" if st.session_state.role == "admin" else "Member"
    html_block(
        '<header class="masthead">'
        f'{wordmark_html()}'
        '<div class="masthead-trail">'
        '<span class="trail-root">Workspace</span>'
        '<span class="trail-slash">/</span>'
        f'<span class="trail-page">{escape(current)}</span>'
        '</div>'
        '<div class="masthead-user">'
        f'<span class="masthead-monogram">{initial}</span>'
        f'<span class="masthead-email">{escape(email)}</span>'
        f'<span class="masthead-role">{role}</span>'
        '</div>'
        '</header>'
    )


def page_header(kicker: str, title: str, subtitle: str = "", status: tuple[str, str] | None = None):
    """Render a page introduction. ``status`` is an optional (label, tone)."""
    sub = f'<p class="lede">{escape(subtitle)}</p>' if subtitle else ""
    chip = ""
    if status:
        label, tone = status
        chip = f'<span class="state-pill {escape(tone)}">{escape(label)}</span>'
    html_block(
        f'<div class="page-intro"><div class="page-intro-main">'
        f'<span class="eyebrow">{escape(kicker)}</span>'
        f'<h1 class="display-title">{escape(title)}</h1>{sub}</div>'
        f'<div>{chip}</div></div>'
    )


def section(label: str, count: int | None = None):
    badge = f'<span class="count">{count}</span>' if count is not None else ""
    html_block(f'<div class="section-label">{escape(label)} {badge}</div>')


def stat_strip(items):
    """items: list of (label, value, note)."""
    stats = "".join(
        f'<div class="stat"><div class="stat-label">{escape(label)}</div>'
        f'<div class="stat-value">{escape(value)}</div>'
        f'<div class="stat-note">{escape(note)}</div></div>'
        for label, value, note in items
    )
    html_block(f'<div class="stat-strip">{stats}</div>')


def ledger(rows):
    """rows: list of (name, note, value, tone) where tone is '', 'is-warn' or 'is-bad'."""
    cells = "".join(
        f'<div class="ledger-row"><span class="ledger-dot {escape(tone)}"></span>'
        f'<div><div class="ledger-name">{escape(name)}</div>'
        f'<div class="ledger-note">{escape(note)}</div></div>'
        f'<div class="ledger-value {escape(tone)}">{escape(value)}</div></div>'
        for name, note, value, tone in rows
    )
    html_block(f'<div class="ledger">{cells}</div>')


def empty_state(icon: str, title: str, text: str):
    html_block(
        f'<div class="blank-state"><div class="blank-mark">{escape(icon)}</div>'
        f'<h3>{escape(title)}</h3><p>{escape(text)}</p></div>'
    )


def _extension(name: str) -> str:
    stem, _, ext = str(name).rpartition(".")
    return ext[:4].upper() if stem and ext else "DOC"


def doc_row(name: str, meta: str, badge: str | None = None):
    chip = f'<span class="entry-tag">{escape(badge)}</span>' if badge else ""
    html_block(
        f'<div class="entry-row"><span class="entry-icon">{escape(_extension(name))}</span>'
        f'<div class="entry-body"><div class="entry-name">{escape(name)}</div>'
        f'<div class="entry-meta">{escape(meta)}</div></div>{chip}</div>'
    )


def _clean_excerpt(value, limit: int = 280) -> str:
    """Strip markup and collapse whitespace so excerpts read as prose."""
    text = re.sub(r"<[^>]+>", " ", str(value or ""))
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def footnote(source):
    page = source.get("page")
    page_html = f'<span class="footnote-page">p. {escape(page)}</span>' if page else ""
    html_block(
        '<div class="footnote"><div class="footnote-head">'
        f'<span class="footnote-id">{escape(source.get("source_id", "S"))}</span>'
        f'<span class="footnote-name">{escape(source.get("filename", "Document"))}</span>'
        f'{page_html}</div>'
        f'<div class="footnote-excerpt">{escape(_clean_excerpt(source.get("excerpt")))}</div></div>'
    )


def sources_panel(sources):
    if not sources:
        return
    with st.expander(f"Footnotes · {len(sources)}"):
        st.caption("Each claim in the answer points back to one of these excerpts.")
        for source in sources:
            footnote(source)
