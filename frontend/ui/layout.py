"""Layout and sidebar theme, layered on top of styles.py.

* Sidebar: fixed, always open, deep-petrol, account pinned to the bottom.
* Chat page: window is locked; only the message list scrolls; the composer is pinned.
"""
import streamlit as st

BASE = """
.block-container { padding-top: 2.4rem !important; }

/* ── sidebar: always open ─────────────────────────────── */
[data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarResizeHandle"],
[data-testid="stSidebarHeader"] { display: none !important; }
@media (min-width: 900px) {
  [data-testid="stSidebar"] {
    transform: none !important; margin-left: 0 !important; visibility: visible !important;
    width: 280px !important; min-width: 280px !important; max-width: 280px !important;
  }
}

/* the palette is re-pointed inside the sidebar, so styles.py follows automatically */
[data-testid="stSidebar"] {
  --ink: #f6f1e3; --ink-2: #d3e2de; --ink-3: #93b5af;
  --paper: #0b3d41; --surface: rgba(255,255,255,.10); --surface-2: rgba(255,255,255,.12);
  --rule: rgba(255,255,255,.12); --rule-strong: rgba(255,255,255,.24);
  --petrol: #f0e4c4; --petrol-deep: #fff8e3; --petrol-wash: rgba(255,255,255,.10);
  background: #0b3d41 !important; border-right: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { overflow-y: auto; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding: 1.5rem 1rem 130px; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .3rem; }

.sidebar-brand { padding: 0 .2rem 1.1rem; }
.wordmark-text { font-size: 1.12rem !important; }
[data-testid="stSidebar"] .wordmark-text em { color: #e6bd6e; }

/* new conversation */
[data-testid="stSidebar"] .st-key-sidebar_new_chat { margin-bottom: .9rem; }
[data-testid="stSidebar"] .st-key-sidebar_new_chat button {
  min-height: 2.6rem !important; font-weight: 600 !important; border-radius: 8px !important;
  justify-content: center !important;
}

/* page links */
[data-testid="stSidebar"] [class*="st-key-nav-"] button {
  min-height: 2.5rem !important; border-radius: 8px !important; border-left-width: 0 !important;
  padding: .45rem .8rem !important; font-size: .9rem !important; color: var(--ink) !important;
}
[data-testid="stSidebar"][data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"] {
  background: rgba(255,255,255,.14) !important; color: #fff !important; font-weight: 600;
  border-left: 0 !important; box-shadow: inset 3px 0 0 #e6bd6e !important;
}
[data-testid="stSidebar"][data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"] p { color: #fff !important; }
[data-testid="stSidebar"] [class*="st-key-nav-"] button[data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255,255,255,.08) !important;
}

/* recent + search */
[data-testid="stSidebar"] .count { background: transparent; border-color: rgba(230,189,110,.5); color: #e6bd6e; }
[data-testid="stSidebar"] .section-label { margin: 1.4rem .2rem .55rem; color: var(--ink-3); }
[data-testid="stSidebar"] .st-key-chat_search { margin: 0 0 .6rem; }
[data-testid="stSidebar"] [data-testid="stTextInputRootElement"] {
  background: rgba(255,255,255,.07) !important;
  border: 1px solid rgba(255,255,255,.16) !important; border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stTextInputRootElement"]:focus-within {
  border-color: #e6bd6e !important; background: rgba(255,255,255,.10) !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="base-input"] {
  background: transparent !important; border: 0 !important; box-shadow: none !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  color: #f6f1e3 !important; font-size: .86rem !important; padding: .55rem .7rem !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder { color: #93b5af !important; font-style: normal !important; }

.st-key-chat-history {
  max-height: calc(100dvh - 480px) !important; min-height: 110px;
  overflow-y: auto !important; border-bottom: 0 !important; margin: 0 !important;
}
[data-testid="stSidebar"] .st-key-chat-history button {
  min-height: 2.25rem !important; border-radius: 8px !important; border-left-width: 0 !important;
  padding: .35rem .7rem !important; font-size: .86rem !important; color: var(--ink-2) !important;
}
[data-testid="stSidebar"] .st-key-chat-history button:hover { background: rgba(255,255,255,.08) !important; color: #fff !important; }
[data-testid="stSidebar"] .st-key-chat-history button[data-testid="stBaseButton-primary"] {
  background: rgba(255,255,255,.14) !important; color: #fff !important;
}
[data-testid="stSidebar"] .st-key-chat-history button > div { width: 100%; overflow: hidden; }
[data-testid="stSidebar"] .st-key-chat-history button p {
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: left;
}
.history-label { margin: .8rem .7rem .25rem !important; color: var(--ink-3) !important; }

/* account block pinned to the bottom edge */
.st-key-sidebar-account {
  position: fixed; left: 0; bottom: 0; width: 280px; z-index: 5; margin: 0;
  padding: 14px 16px 12px; background: #0a3639;
  border-top: 1px solid rgba(255,255,255,.12); gap: .35rem !important;
}
.st-key-sidebar-account .user-card { border-top: 0; margin: 0 0 12px; padding: 0; gap: .7rem; }
.st-key-sidebar-account .avatar {
  width: 34px; height: 34px; background: #f0e4c4 !important; color: #0b3d41 !important;
  border: 0 !important; font-weight: 600; font-size: .8rem;
}
.st-key-sidebar-account .user-name { font-size: .84rem; max-width: 190px; color: #fff; }
.st-key-sidebar-account .user-role { color: #93b5af; }
[data-testid="stSidebar"] .st-key-sidebar_signout button {
  font-family: var(--sans); text-transform: none; letter-spacing: 0; font-size: .84rem;
  color: var(--ink-2) !important; min-height: 2.2rem; padding: .3rem .6rem !important;
  border: 1px solid rgba(255,255,255,.16) !important; border-radius: 8px !important;
  justify-content: center !important;
}
[data-testid="stSidebar"] .st-key-sidebar_signout button:hover { color: #fff !important; background: rgba(255,255,255,.08) !important; }
@media (max-width: 899px) { .st-key-sidebar-account { width: 100%; } }
"""

CHAT = """
/* lock the window: only the message list scrolls */
html, body, .stApp, [data-testid="stAppViewContainer"], .stMain {
  height: 100dvh; overflow: hidden !important;
}
.stMain .block-container {
  max-width: 820px !important; padding: 0 24px !important; margin: 0 auto;
}

.stMain .block-container > [data-testid="stVerticalBlock"] { height: auto !important; justify-content: flex-start !important; gap: 0 !important; }
.st-key-chat-shell > *, .st-key-chat-head, .st-key-chat-body { flex: 0 0 auto !important; }
.st-key-chat-shell {
  background: transparent !important; border: 0 !important; box-shadow: none !important;
  border-radius: 0 !important; overflow: visible !important; gap: 0 !important;
}

/* title bar */
.st-key-chat-head {
  position: relative; height: 64px; justify-content: center; gap: 0 !important;
  border-bottom: 1px solid var(--rule);
}
.st-key-chat-head .chat-title {
  margin: 0 !important; padding: 0 160px 0 0 !important; max-width: 100%;
  font-size: 1.08rem !important; font-weight: 500 !important; line-height: 1.3;
  font-family: var(--serif) !important; color: var(--ink) !important;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.st-key-chat-head .chat-title a { display: none; }
.st-key-chat-head [data-testid="stPopover"] { position: absolute; right: 0; top: 12px; width: auto; }
.st-key-chat-head [data-testid="stPopover"] > button {
  min-height: 2.5rem; border-radius: 999px; padding: 0 1rem;
  background: var(--surface); border: 1px solid var(--rule-strong); font-weight: 500; color: var(--ink);
}
.st-key-chat-head [data-testid="stPopover"] > button:hover { border-color: var(--petrol); color: var(--petrol); }

/* message list */
.st-key-chat-body {
  height: calc(100dvh - 64px - 108px);
  min-height: 0 !important; max-height: none !important;
  padding: 28px 0 16px !important;
}
.st-key-scroll-anchor { position: absolute; height: 0; overflow: hidden; }

/* composer: Streamlit pins a top-level chat_input to the bottom */
[data-testid="stBottom"], [data-testid="stBottom"] > div { background: transparent !important; }
[data-testid="stBottomBlockContainer"] {
  max-width: 820px !important; margin: 0 auto; padding: 0 24px 26px !important;
}
[data-testid="stChatInput"] {
  border-radius: 24px !important; background: var(--surface) !important;
  border: 1px solid var(--rule-strong) !important;
  box-shadow: 0 12px 32px -16px rgba(31, 42, 43, .35) !important;
}
[data-testid="stChatInput"] textarea { font-size: .98rem !important; font-style: normal !important; }

/* turns */
[data-testid="stChatMessage"] { margin-bottom: 32px !important; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]::before { content: none !important; }
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
  border-left: 0 !important; padding-left: 0 !important;
}
[data-testid="stChatMessage"]:not(:has([aria-label="Chat message from user"])) [data-testid="stMarkdownContainer"] :is(p, li):not(details *) {
  font-family: var(--serif) !important; font-size: 1.06rem !important; line-height: 1.75 !important; color: var(--ink);
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stMarkdownContainer"] {
  background: #e7dfca !important; border: 0 !important; color: var(--ink) !important;
  border-radius: 18px 18px 4px 18px !important; padding: .7rem 1.05rem !important; max-width: 78% !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] thead th { color: var(--ink-2); }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] tbody td { color: var(--ink); font-size: .84rem; }
[data-testid="stChatMessage"] [data-testid="stExpander"] summary p {
  font-family: var(--mono) !important; font-size: .68rem !important; letter-spacing: .12em; text-transform: uppercase; color: var(--petrol);
}

/* empty state */
.st-key-chat-body .blank-state { margin-top: 10vh; max-width: 560px; }
.blank-state h3 { font-size: 2.1rem !important; }
.st-key-suggestions .stButton > button {
  min-height: 0 !important; padding: .6rem 1.1rem !important; border-radius: 999px !important;
}

@media (max-width: 640px) {
  .stMain .block-container { padding: 0 14px !important; }
  .st-key-chat-body { height: calc(100dvh - 64px - 100px); }
}
"""


def inject(chat_page: bool):
    st.markdown(f"<style>{BASE}{CHAT if chat_page else ''}</style>", unsafe_allow_html=True)