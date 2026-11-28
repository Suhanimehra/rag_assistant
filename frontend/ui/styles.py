"""Visual system for the Document Intelligence workspace.

An editorial "reading desk" theme: warm parchment paper, petrol ink, and ochre
annotation marks. Structure is inspired by research tools generally, but the
palette, typography, spacing and components are specific to this app.
"""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..500&display=swap');

:root {
  --paper: #f7f3e9;
  --surface: #fffdf7;
  --surface-2: #efe9db;
  --ink: #1f2a2b;
  --ink-2: #5b6663;
  --ink-3: #87908b;
  --rule: #e2dac9;
  --rule-strong: #cfc5b0;
  --petrol: #0e4d52;
  --petrol-deep: #08383c;
  --petrol-wash: #e4efed;
  --ochre: #a9762a;
  --ochre-wash: #f8eed7;
  --ochre-rule: #e4cfa2;
  --clay: #9c4433;
  --clay-wash: #f8e8e2;
  --serif: Newsreader, 'Iowan Old Style', 'Palatino Linotype', Georgia, serif;
  --sans: 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
  --mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --pad: clamp(18px, 3.6vw, 40px);
}

/* ── canvas ───────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: var(--sans);
  color: var(--ink);
  -webkit-font-smoothing: antialiased;
}
.stApp, [data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 500px at 85% -12%, rgba(169, 118, 42, .07), transparent 60%),
    var(--paper);
}
[data-testid="stHeader"] { background: transparent; height: 0; }
#MainMenu, [data-testid="stToolbar"], [data-testid="stDecoration"], footer {
  visibility: hidden; height: 0;
}
.block-container {
  max-width: 1340px;
  padding: 0 var(--pad) 3.5rem;
}
h1, h2, h3, h4, h5 { color: var(--ink); font-family: var(--serif); font-weight: 400; }
p, li, label, span { color: var(--ink); }
a { color: var(--petrol); text-underline-offset: 3px; }
hr { border-color: var(--rule); }
::selection { background: var(--ochre-wash); }

/* ── masthead ─────────────────────────────────────────── */
.masthead {
  display: flex;
  align-items: center;
  gap: clamp(14px, 2.4vw, 30px);
  height: 66px;
  margin: 0 calc(-1 * var(--pad)) 26px;
  padding: 0 var(--pad);
  border-bottom: 1px solid var(--rule-strong);
  background: rgba(247, 243, 233, .72);
  backdrop-filter: blur(6px);
}
.masthead-brand { display: flex; align-items: center; gap: 10px; flex: none; }
.wordmark-mark {
  width: 30px; height: 30px; flex: none;
  display: grid; place-items: center;
  border-radius: 3px;
  background: var(--petrol); color: var(--paper);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .12);
}
.wordmark-mark svg { width: 16px; height: 16px; }
.wordmark-text {
  font-family: var(--serif);
  font-size: 1.06rem;
  letter-spacing: -.01em;
  color: var(--ink);
  white-space: nowrap;
}
.wordmark-text em { font-style: italic; color: var(--petrol); }
.masthead-trail {
  display: flex; align-items: baseline; gap: 8px;
  padding-left: clamp(10px, 2vw, 22px);
  border-left: 1px solid var(--rule);
  min-width: 0;
}
.trail-root {
  font-family: var(--mono); font-size: .64rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--ink-3);
}
.trail-slash { color: var(--rule-strong); font-family: var(--mono); font-size: .7rem; }
.trail-page {
  font-family: var(--mono); font-size: .66rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--petrol);
}
.masthead-user {
  display: flex; align-items: center; gap: 10px;
  margin-left: auto; min-width: 0;
}
.masthead-monogram {
  width: 28px; height: 28px; flex: none;
  display: grid; place-items: center;
  border: 1px solid var(--rule-strong); border-radius: 50%;
  background: var(--surface); color: var(--petrol);
  font-family: var(--mono); font-size: .68rem; font-weight: 500;
}
.masthead-email {
  font-size: .8rem; font-weight: 500; color: var(--ink);
  max-width: 24vw; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.masthead-role {
  font-family: var(--mono); font-size: .6rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink-3);
}

/* ── page intro ───────────────────────────────────────── */
.page-intro {
  display: flex; justify-content: space-between; align-items: flex-end;
  gap: 22px;
  padding: 6px 0 20px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--rule-strong);
}
.page-intro-main { min-width: 0; }
.eyebrow {
  display: inline-flex; align-items: center; gap: 9px;
  font-family: var(--mono); font-size: .63rem; font-weight: 500;
  letter-spacing: .18em; text-transform: uppercase; color: var(--ochre);
}
.eyebrow::before {
  content: ""; width: 22px; height: 1px; background: var(--ochre);
}
.display-title {
  font-family: var(--serif) !important;
  font-size: clamp(1.9rem, 3.1vw, 2.6rem);
  font-weight: 400 !important; line-height: 1.02;
  letter-spacing: -.035em;
  margin: .35rem 0 0;
  color: var(--ink) !important;
}
.lede {
  color: var(--ink-2); font-size: .92rem; line-height: 1.6;
  margin: .45rem 0 0; max-width: 46rem;
}
.state-pill {
  display: inline-flex; align-items: center; gap: 8px;
  flex: none;
  padding: .34rem .7rem;
  border: 1px solid var(--rule-strong); border-radius: 3px;
  background: var(--surface);
  font-family: var(--mono); font-size: .63rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--petrol);
  white-space: nowrap;
}
.state-pill::before {
  content: ""; width: 6px; height: 6px; border-radius: 50%;
  background: var(--petrol);
  box-shadow: 0 0 0 3px var(--petrol-wash);
}
.state-pill.is-warn { color: var(--ochre); border-color: var(--ochre-rule); }
.state-pill.is-warn::before { background: var(--ochre); box-shadow: 0 0 0 3px var(--ochre-wash); }
.state-pill.is-bad { color: var(--clay); }
.state-pill.is-bad::before { background: var(--clay); box-shadow: 0 0 0 3px var(--clay-wash); }

/* ── sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: #f2ede1;
  border-right: 1px solid var(--rule-strong);
  min-width: 274px;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 1.15rem 1rem 1.4rem;
}
.st-key-sidebar_new_chat { margin-bottom: .35rem; }
.st-key-sidebar_new_chat button {
  background: var(--petrol) !important;
  border: 1px solid var(--petrol) !important;
  border-radius: 4px !important;
  color: var(--paper) !important;
  justify-content: flex-start !important;
  padding: .52rem .8rem !important;
  font-family: var(--sans) !important;
  font-size: .82rem !important;
  font-weight: 500 !important;
  letter-spacing: .01em;
  box-shadow: none !important;
}
.st-key-sidebar_new_chat button:hover {
  background: var(--petrol-deep) !important;
  border-color: var(--petrol-deep) !important;
}
[data-testid="stSidebar"] .st-key-sidebar_new_chat button p,
[data-testid="stSidebar"] .st-key-sidebar_new_chat button span,
[data-testid="stSidebar"] .st-key-sidebar_new_chat button > div {
  color: var(--paper) !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: transparent;
  border: 0;
  border-left: 2px solid transparent;
  border-radius: 0;
  box-shadow: none;
  color: var(--ink-2);
  justify-content: flex-start !important;
  text-align: left;
  padding: .4rem .6rem .4rem .75rem;
  min-height: 2.1rem;
  font-size: .83rem;
  font-weight: 400;
  transition: background 120ms ease, color 120ms ease, border-color 120ms ease;
}
[data-testid="stSidebar"] .stButton > button > div {
  justify-content: flex-start !important;
  width: 100%;
}
[data-testid="stSidebar"] .stButton > button p { color: inherit !important; }
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255, 253, 247, .72);
  border-left-color: var(--rule-strong);
  color: var(--petrol);
}
[data-testid="stSidebar"] .stButton > button:focus:not(:active) {
  border-color: transparent;
  border-left-color: var(--ochre);
  color: var(--petrol);
}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:not(.st-key-sidebar_new_chat) .stButton > button[data-testid="stBaseButton-primary"] {
  background: var(--surface) !important;
  border-left: 2px solid var(--ochre) !important;
  color: var(--ink) !important;
  font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:not(.st-key-sidebar_new_chat) .stButton > button[data-testid="stBaseButton-primary"] p {
  color: var(--ink) !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:not(.st-key-sidebar_new_chat) .stButton > button[data-testid="stBaseButton-primary"]:hover {
  background: var(--surface) !important;
  color: var(--petrol) !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"]:not(.st-key-sidebar_new_chat) .stButton > button[data-testid="stBaseButton-primary"]:hover p {
  color: var(--petrol) !important;
}
/* current page reads as an ink mark; the selected thread carries the card */
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"] {
  background: transparent !important;
  border-left-color: var(--ochre) !important;
  color: var(--petrol) !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"] p {
  color: var(--petrol) !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"]:hover,
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"]:focus {
  background: var(--petrol-wash) !important;
  border-left-color: var(--ochre) !important;
  color: var(--petrol) !important;
}
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"]:hover p,
[data-testid="stSidebar"] [data-testid="stElementContainer"][class*="st-key-nav-"] .stButton > button[data-testid="stBaseButton-primary"]:focus p {
  color: var(--petrol) !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"] {
  background: transparent;
  border: 0;
  border-bottom: 1px solid var(--rule-strong);
  border-radius: 0;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
  border-bottom-color: var(--petrol);
  box-shadow: none;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
  background: transparent !important;
  color: var(--ink) !important;
  font-size: .8rem;
  padding-left: 2px;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
  color: var(--ink-3) !important;
  font-style: italic;
}
[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
[data-testid="stSidebarCollapsedControl"] button {
  background: var(--surface) !important;
  color: var(--ink-2) !important;
  border: 1px solid var(--rule) !important;
  visibility: visible !important;
}

/* section labels */
.section-label {
  display: flex; align-items: center; gap: 8px;
  margin: 1.2rem .2rem .3rem;
  font-family: var(--mono); font-size: .6rem; font-weight: 500;
  letter-spacing: .16em; text-transform: uppercase; color: var(--ink-3);
}
.section-label::after {
  content: ""; flex: 1; height: 1px; background: var(--rule);
}
.count {
  order: 2;
  font-family: var(--mono); font-size: .6rem; letter-spacing: 0;
  color: var(--ochre); background: var(--ochre-wash);
  border: 1px solid var(--ochre-rule); border-radius: 2px;
  padding: 0 .3rem;
}
.sidebar-empty {
  font-size: .78rem; font-style: italic; color: var(--ink-3);
  padding: .25rem .2rem .5rem;
}
/* history stays visible while pages and account remain in reach */
.st-key-chat-history {
  max-height: 40vh;
  min-height: 90px;
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-width: thin;
  scrollbar-color: var(--rule-strong) transparent;
  margin: 0 -.15rem .15rem;
  padding: 0 .15rem;
  border-bottom: 1px dotted var(--rule-strong);
}
.st-key-chat-history::-webkit-scrollbar { width: 5px; }
.st-key-chat-history::-webkit-scrollbar-thumb {
  background: var(--rule-strong);
  border-radius: 4px;
}
.history-label {
  margin: .5rem .65rem .1rem;
  font-family: var(--mono);
  font-size: .53rem;
  font-weight: 500;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--ink-3);
}
[data-testid="stSidebar"] .st-key-chat_search { margin: .1rem 0 .05rem; }
.user-card {
  display: flex; align-items: center; gap: .6rem;
  margin: 1rem 0 .45rem;
  padding: .75rem .2rem 0;
  border-top: 1px dotted var(--rule-strong);
}
.user-card .avatar {
  width: 28px; height: 28px; flex: none;
  display: grid; place-items: center;
  border: 1px solid var(--rule-strong); border-radius: 50%;
  background: var(--surface); color: var(--petrol);
  font-family: var(--mono); font-size: .64rem; font-weight: 500;
}
.user-card .user-name {
  font-size: .76rem; font-weight: 500; color: var(--ink);
  max-width: 170px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.user-card .user-role {
  font-family: var(--mono); font-size: .58rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink-3);
}
[data-testid="stSidebar"] .st-key-sidebar_signout button {
  color: var(--ink-3);
  font-family: var(--mono);
  font-size: .64rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  padding-left: .2rem;
}

/* ── buttons ──────────────────────────────────────────── */
.stButton > button, .stFormSubmitButton > button {
  border-radius: 4px;
  border: 1px solid var(--rule-strong);
  background: var(--surface);
  color: var(--ink);
  font-family: var(--sans);
  font-size: .84rem;
  font-weight: 500;
  box-shadow: none;
  transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--petrol);
  color: var(--petrol);
  background: var(--surface);
}
.stButton > button:focus:not(:active), .stFormSubmitButton > button:focus:not(:active) {
  border-color: var(--petrol);
  box-shadow: 0 0 0 3px rgba(14, 77, 82, .10);
  color: var(--petrol);
}
.stButton > button[data-testid="stBaseButton-primary"],
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] {
  background: var(--petrol) !important;
  border-color: var(--petrol) !important;
  color: var(--paper) !important;
}
.stButton > button[data-testid="stBaseButton-primary"] p,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] p {
  color: var(--paper) !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:hover,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  background: var(--petrol-deep) !important;
  border-color: var(--petrol-deep) !important;
  color: var(--paper) !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:hover p,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:hover p {
  color: var(--paper) !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:disabled,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:disabled {
  background: var(--surface-2) !important;
  border-color: var(--rule) !important;
  color: var(--ink-3) !important;
}
.stButton > button[data-testid="stBaseButton-primary"]:disabled p,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"]:disabled p {
  color: var(--ink-3) !important;
}

/* ── inputs & widgets ─────────────────────────────────── */
[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stTextArea"] div[data-baseweb="textarea"],
[data-testid="stNumberInput"] div[data-baseweb="input"] {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 4px;
}
[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
  border-color: var(--petrol);
  box-shadow: 0 0 0 3px rgba(14, 77, 82, .09);
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  color: var(--ink);
  font-size: .88rem;
}
[data-testid="stWidgetLabel"] p {
  font-family: var(--mono);
  font-size: .62rem !important;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--ink-2) !important;
}
[data-testid="stMultiSelect"] div[data-baseweb="select"] {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 4px;
}
[data-testid="stMultiSelect"] div[data-baseweb="select"]:focus-within {
  border-color: var(--petrol);
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
  background: var(--petrol-wash) !important;
  border-radius: 2px !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { color: var(--petrol) !important; }
[data-testid="stCheckbox"] p { font-size: .82rem; }
[data-testid="stSelectbox"] div[data-baseweb="select"] {
  background: var(--surface);
  border-radius: 4px;
}
[data-testid="stExpander"] { border: 0; background: transparent; }
[data-testid="stExpander"] details {
  border: 0; border-top: 1px dotted var(--rule-strong);
  background: transparent; border-radius: 0;
}
[data-testid="stExpander"] summary {
  padding: .55rem 0;
  font-family: var(--mono);
  font-size: .64rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--petrol);
}
[data-testid="stExpander"] summary:hover { color: var(--petrol-deep); }
[data-testid="stExpander"] summary svg { color: var(--ochre); }
[data-testid="stDataFrame"] {
  border: 1px solid var(--rule);
  border-radius: 3px;
  overflow: hidden;
}
[data-testid="stFileUploader"] {
  border: 1px dashed var(--rule-strong);
  border-radius: 4px;
  background: rgba(255, 253, 247, .55);
  padding: .2rem;
}
[data-testid="stFileUploader"] section {
  border: 0; padding: .7rem;
  background: transparent;
}
[data-testid="stFileUploader"] section > button {
  border-radius: 3px;
  border: 1px solid var(--petrol);
  background: transparent;
  color: var(--petrol);
}
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span { color: var(--ink-3); }
[data-testid="stFileUploaderDropzoneInstructions"] span { color: var(--ink-2); }

/* alerts */
[data-testid="stAlert"] [data-testid="stAlertContainer"] {
  border-radius: 4px;
  border-left: 3px solid var(--petrol) !important;
  background: var(--petrol-wash) !important;
}
[data-testid="stAlert"] p { color: var(--ink) !important; font-size: .84rem; }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) [data-testid="stAlertContainer"] {
  border-left-color: var(--petrol) !important; background: var(--petrol-wash) !important;
}
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) [data-testid="stAlertContainer"] {
  border-left-color: var(--ochre) !important; background: var(--ochre-wash) !important;
}
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) [data-testid="stAlertContainer"] {
  border-left-color: var(--clay) !important; background: var(--clay-wash) !important;
}

/* ── chat workspace ───────────────────────────────────── */
[data-testid="stHorizontalBlock"] { gap: clamp(18px, 2.4vw, 34px); }

/* the conversation is its own bounded surface, ChatGPT-style */
.st-key-chat-shell {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 12px;
  gap: 0 !important;
  box-shadow:
    0 1px 0 rgba(31, 42, 43, .03),
    0 26px 60px -42px rgba(31, 42, 43, .45);
  overflow: hidden;
}
.chat-head {
  display: flex; justify-content: space-between; align-items: center;
  gap: 18px;
  padding: 15px 22px;
  border-bottom: 1px solid var(--rule);
  background:
    linear-gradient(180deg, rgba(255, 253, 247, .95), rgba(247, 243, 233, .55));
}
.chat-head-main { min-width: 0; }
.chat-title {
  font-family: var(--serif) !important;
  font-size: 1.22rem !important;
  font-weight: 400 !important;
  line-height: 1.2;
  letter-spacing: -.015em;
  margin: .16rem 0 0;
  color: var(--ink) !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 52ch;
}
.chat-head .state-pill { flex: none; }
.st-key-chat-body {
  padding: 22px 26px 8px;
  min-height: 360px;
  max-height: calc(100vh - 380px);
  overflow-y: auto;
  overscroll-behavior: contain;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: var(--rule-strong) transparent;
}
.st-key-chat-body::-webkit-scrollbar { width: 8px; }
.st-key-chat-body::-webkit-scrollbar-thumb {
  background: var(--rule-strong);
  border-radius: 8px;
  border: 2px solid var(--surface);
}
.st-key-chat-body::-webkit-scrollbar-track { background: transparent; }
.st-key-chat-composer {
  border-top: 1px solid var(--rule);
  background: rgba(247, 243, 233, .55);
  padding: 14px 22px 16px;
  gap: .15rem !important;
}
.st-key-chat-composer [data-testid="stChatInput"] {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(31, 42, 43, .04);
}
.st-key-chat-composer [data-testid="stChatInput"]:focus-within {
  border-color: var(--petrol);
  box-shadow: 0 0 0 3px rgba(14, 77, 82, .09);
}
.st-key-sources-panel {
  border: 1px solid var(--rule);
  border-radius: 10px;
  background: rgba(255, 253, 247, .6);
  padding: 18px 18px 16px;
  min-height: 60vh;
}

/* rail */
.rail-head { padding-bottom: 14px; border-bottom: 1px solid var(--rule-strong); margin-bottom: 14px; }
.rail-title {
  font-family: var(--serif); font-size: 1.28rem; font-weight: 400;
  letter-spacing: -.02em; margin: 0;
}
.rail-sub { color: var(--ink-2); font-size: .76rem; line-height: 1.5; margin: .2rem 0 0; }
.rail-label {
  display: flex; align-items: center; gap: 7px;
  font-family: var(--mono); font-size: .6rem; font-weight: 500;
  letter-spacing: .15em; text-transform: uppercase;
  color: var(--ink-3);
  margin: 1.1rem 0 .4rem;
}
.rail-label::after { content: ""; flex: 1; height: 1px; background: var(--rule); }
.rail-divider { border: 0; border-top: 1px dotted var(--rule-strong); margin: 1rem 0; }
.rail-empty {
  font-size: .76rem; font-style: italic; color: var(--ink-3);
  padding: .2rem 0 .6rem;
}

/* ── chat turns ───────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: transparent;
  border: 0;
  padding: 0;
  margin: 0 0 24px;
  gap: 0;
  max-width: none;
}
[data-testid="stChatMessage"] > [data-testid^="stChatMessageAvatar"] { display: none; }
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
  background: transparent;
  padding: 0;
  min-width: 0;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
  border-left: 2px solid var(--petrol);
  padding-left: 16px;
}
[data-testid="stChatMessage"]:not(:has([aria-label="Chat message from user"])) [data-testid="stChatMessageContent"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] {
  color: var(--ink);
  font-size: .94rem;
  line-height: 1.68;
}
[data-testid="stChatMessage"]:not(:has([aria-label="Chat message from user"])) [data-testid="stChatMessageContent"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"]::before {
  content: "ASSISTANT";
  display: block;
  margin-bottom: .45rem;
  font-family: var(--mono);
  font-size: .58rem;
  font-weight: 500;
  letter-spacing: .18em;
  color: var(--ochre);
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
  display: flex;
  justify-content: flex-end;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"] {
  background: var(--ochre-wash);
  border: 1px solid var(--ochre-rule);
  border-radius: 7px 7px 2px 7px;
  padding: .6rem .9rem;
  margin-left: auto;
  width: fit-content;
  max-width: 86%;
  color: var(--ink);
  font-size: .9rem;
  line-height: 1.6;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) [data-testid="stChatMessageContent"] > [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] > [data-testid="stMarkdown"] [data-testid="stMarkdownContainer"]::before {
  content: "YOU";
  display: block;
  margin-bottom: .2rem;
  font-family: var(--mono);
  font-size: .56rem;
  font-weight: 500;
  letter-spacing: .18em;
  color: var(--ochre);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4 {
  font-family: var(--serif) !important;
  font-weight: 500 !important;
  letter-spacing: -.01em;
  color: var(--ink) !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1 { font-size: 1.5rem; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2 { font-size: 1.3rem; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3 { font-size: 1.15rem; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4 { font-size: 1.02rem; }
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
  font-family: var(--sans);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] table {
  width: 100%;
  margin: .6rem 0 .9rem;
  border-collapse: collapse;
  font-size: .8rem;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] thead th {
  padding: .45rem .5rem;
  border-bottom: 1px solid var(--rule-strong);
  background: transparent;
  font-family: var(--mono);
  font-size: .56rem;
  font-weight: 500;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--ink-3);
  text-align: left;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] tbody td {
  padding: .5rem;
  border-bottom: 1px solid var(--rule);
  vertical-align: top;
  color: var(--ink-2);
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] tbody tr:last-child td {
  border-bottom: 0;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {
  font-family: var(--mono);
  font-size: .78em;
  background: var(--surface-2);
  border-radius: 2px;
  padding: .05rem .25rem;
}
[data-testid="stChatMessage"] [data-testid="stExpander"] { margin: 0; }
[data-testid="stChatMessage"] [data-testid="stExpander"] summary {
  font-size: .58rem;
  letter-spacing: .14em;
}
.answer-meta {
  display: flex; align-items: center; gap: 10px;
  margin: -12px 0 22px;
  font-family: var(--mono);
  font-size: .6rem;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--ink-3);
}
.answer-meta::before { content: ""; width: 18px; height: 1px; background: var(--ochre); }

/* empty state + suggestions */
.blank-state {
  max-width: 430px;
  margin: 2.4rem auto 1.2rem;
  text-align: center;
}
.blank-mark {
  width: 44px; height: 44px;
  margin: 0 auto .8rem;
  display: grid; place-items: center;
  border: 1px solid var(--rule-strong);
  border-radius: 50%;
  color: var(--petrol);
  font-family: var(--serif);
  font-size: 1.15rem;
  background: var(--surface);
}
.blank-state h3 {
  font-family: var(--serif) !important;
  font-size: 1.42rem;
  font-weight: 400 !important;
  letter-spacing: -.02em;
  margin: 0 0 .35rem;
}
.blank-state p {
  color: var(--ink-2);
  font-size: .87rem;
  line-height: 1.6;
  margin: 0;
}
.suggestion-note {
  margin: 1.5rem 0 .55rem;
  font-family: var(--mono);
  font-size: .6rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: var(--ink-3);
}
.st-key-suggestions [data-testid="stHorizontalBlock"] { gap: 12px !important; }
.st-key-suggestions [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  flex: 1 1 0 !important;
  min-width: 0 !important;
}
.st-key-suggestions .stButton > button {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  width: 100%;
  min-height: 82px;
  padding: .8rem .85rem;
  text-align: left;
  white-space: normal;
  line-height: 1.4;
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: 4px;
}
.st-key-suggestions .stButton > button > div {
  justify-content: flex-start !important;
  align-items: flex-start !important;
  width: 100%;
}
.st-key-suggestions .stButton > button p {
  font-size: .8rem;
  color: var(--ink-2) !important;
}
.st-key-suggestions .stButton > button:hover {
  border-color: var(--petrol);
  box-shadow: 0 10px 24px rgba(31, 42, 43, .06);
}
.st-key-suggestions .stButton > button:hover p { color: var(--petrol) !important; }

/* composer */
[data-testid="stChatInput"] {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 5px;
  box-shadow: 0 8px 26px rgba(31, 42, 43, .05);
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--petrol);
  box-shadow: 0 0 0 3px rgba(14, 77, 82, .09);
}
[data-testid="stChatInput"] textarea {
  color: var(--ink);
  font-size: .9rem;
}
[data-testid="stChatInput"] textarea::placeholder {
  color: var(--ink-3);
  font-style: italic;
}
[data-testid="stChatInput"] button { color: var(--petrol); }
.composer-hint {
  display: flex; justify-content: space-between; gap: 14px;
  margin-top: .4rem;
  font-family: var(--mono);
  font-size: .57rem;
  letter-spacing: .06em;
  color: var(--ink-3);
}

/* ── footnotes / citations ────────────────────────────── */
.footnote {
  padding: .65rem 0 .65rem .85rem;
  border-left: 1px solid var(--ochre-rule);
  margin: .35rem 0;
}
.footnote-head {
  display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap;
  margin-bottom: .22rem;
}
.footnote-id {
  font-family: var(--mono);
  font-size: .58rem;
  font-weight: 500;
  letter-spacing: .06em;
  color: var(--ochre);
}
.footnote-name {
  font-family: var(--serif);
  font-size: .86rem;
  font-weight: 500;
  color: var(--ink);
  overflow-wrap: anywhere;
}
.footnote-page {
  font-family: var(--mono);
  font-size: .56rem;
  letter-spacing: .06em;
  color: var(--ink-3);
}
.footnote-excerpt {
  font-size: .78rem;
  line-height: 1.55;
  color: var(--ink-2);
}

/* ── collection rows ──────────────────────────────────── */
.entry-list { border-top: 1px solid var(--rule); }
.entry-row {
  display: flex; align-items: center; gap: .75rem;
  padding: .72rem .1rem;
  border-bottom: 1px solid var(--rule);
  overflow-wrap: anywhere;
}
.entry-icon {
  width: 28px; height: 32px; flex: none;
  display: grid; place-items: center;
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  background: var(--surface);
  color: var(--petrol);
  font-family: var(--mono);
  font-size: .52rem;
  font-weight: 500;
  letter-spacing: .02em;
}
.entry-body { min-width: 0; flex: 1; }
.entry-name {
  font-size: .86rem; font-weight: 500; color: var(--ink);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.entry-meta {
  font-family: var(--mono); font-size: .6rem; letter-spacing: .04em;
  color: var(--ink-3);
}
.entry-tag {
  flex: none;
  padding: .12rem .4rem;
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  font-family: var(--mono); font-size: .56rem; letter-spacing: .08em;
  text-transform: uppercase; color: var(--petrol);
  background: var(--surface);
}

/* ── stat strip ───────────────────────────────────────── */
.stat-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  border-top: 1px solid var(--rule-strong);
  border-bottom: 1px solid var(--rule-strong);
  margin: 0 0 30px;
}
.stat {
  padding: 15px 22px 16px 0;
  border-right: 1px dotted var(--rule-strong);
}
.stat:last-child { border-right: 0; }
.stat-label {
  font-family: var(--mono); font-size: .58rem; font-weight: 500;
  letter-spacing: .14em; text-transform: uppercase; color: var(--ink-3);
}
.stat-value {
  font-family: var(--serif); font-size: 1.95rem; font-weight: 400;
  line-height: 1.1; color: var(--ink); margin: .15rem 0 .05rem;
}
.stat-note { font-size: .72rem; color: var(--ink-2); }

/* ── ledger (system) ──────────────────────────────────── */
.ledger {
  border-top: 1px solid var(--rule-strong);
  margin: .4rem 0 24px;
}
.ledger-row {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  gap: 14px;
  align-items: center;
  padding: .85rem .15rem;
  border-bottom: 1px solid var(--rule);
}
.ledger-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--petrol);
  box-shadow: 0 0 0 4px var(--petrol-wash);
}
.ledger-dot.is-warn { background: var(--ochre); box-shadow: 0 0 0 4px var(--ochre-wash); }
.ledger-dot.is-bad { background: var(--clay); box-shadow: 0 0 0 4px var(--clay-wash); }
.ledger-name { font-size: .88rem; font-weight: 500; color: var(--ink); }
.ledger-note { font-size: .76rem; color: var(--ink-2); margin-top: .1rem; }
.ledger-value {
  font-family: var(--mono); font-size: .62rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--petrol); text-align: right;
}
.ledger-value.is-warn { color: var(--ochre); }
.ledger-value.is-bad { color: var(--clay); }

/* ── upload card ──────────────────────────────────────── */
.st-key-upload-card {
  background: rgba(255, 253, 247, .58);
  border: 1px dashed var(--rule-strong);
  border-radius: 4px;
  padding: clamp(16px, 2vw, 24px);
  margin-bottom: 8px;
}
.panel-title {
  font-family: var(--serif);
  font-size: 1.12rem;
  font-weight: 500;
  letter-spacing: -.01em;
  color: var(--ink);
}
.panel-sub {
  font-size: .78rem;
  line-height: 1.55;
  color: var(--ink-2);
  margin: .2rem 0 .7rem;
}
.panel-sub code {
  font-family: var(--mono);
  font-size: .72rem;
  background: var(--surface-2);
  padding: .05rem .25rem;
  border-radius: 2px;
}
.section-note {
  font-family: var(--mono);
  font-size: .6rem;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--ink-3);
}

/* ── access screen ────────────────────────────────────── */
.st-key-access-copy {
  padding: clamp(10px, 2vw, 30px) 0;
}
.st-key-access-panel {
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 5px;
  padding: clamp(22px, 3vw, 36px);
  box-shadow: 0 24px 60px rgba(31, 42, 43, .08);
}
.access-brand {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: clamp(26px, 5vw, 54px);
}
.access-kicker {
  display: inline-flex; align-items: center; gap: 10px;
  font-family: var(--mono); font-size: .62rem; font-weight: 500;
  letter-spacing: .18em; text-transform: uppercase; color: var(--ochre);
  margin-bottom: .9rem;
}
.access-kicker::before { content: ""; width: 30px; height: 1px; background: var(--ochre); }
.access-title {
  font-family: var(--serif) !important;
  font-size: clamp(2.3rem, 4.5vw, 3.9rem);
  font-weight: 300 !important;
  line-height: .99;
  letter-spacing: -.04em;
  margin: 0 0 1rem;
  max-width: 12ch;
  color: var(--ink) !important;
}
.access-title em { font-style: italic; color: var(--petrol); }
.access-lede {
  max-width: 34rem;
  color: var(--ink-2);
  font-size: .96rem;
  line-height: 1.68;
  margin: 0 0 1.7rem;
}
.access-steps {
  list-style: none;
  margin: 0 0 1.8rem;
  padding: 0;
  max-width: 38rem;
  border-top: 1px solid var(--rule-strong);
}
.access-steps li {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 12px;
  padding: .7rem 0;
  border-bottom: 1px solid var(--rule);
}
.access-steps .step-num {
  font-family: var(--mono);
  font-size: .62rem;
  letter-spacing: .08em;
  color: var(--ochre);
  padding-top: .15rem;
}
.access-steps strong {
  display: block;
  font-size: .84rem;
  font-weight: 600;
  color: var(--ink);
}
.access-steps span.step-text {
  display: block;
  font-size: .78rem;
  line-height: 1.5;
  color: var(--ink-2);
}
.access-specimen {
  position: relative;
  max-width: 410px;
  margin: 0 0 .4rem 8px;
}
.access-specimen::before,
.access-specimen::after {
  content: "";
  position: absolute;
  inset: 0;
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  background: var(--surface);
}
.access-specimen::before { transform: rotate(-1.4deg); }
.access-specimen::after { transform: rotate(.9deg); background: #fbf7ec; }
.specimen-sheet {
  position: relative;
  z-index: 1;
  background: var(--surface);
  border: 1px solid var(--rule-strong);
  border-radius: 2px;
  padding: 1rem 1.15rem;
  transform: rotate(-.4deg);
}
.specimen-tab {
  display: inline-block;
  margin-bottom: .55rem;
  font-family: var(--mono);
  font-size: .55rem;
  letter-spacing: .18em;
  color: var(--ochre);
}
.specimen-q {
  font-family: var(--serif);
  font-size: 1.02rem;
  font-style: italic;
  color: var(--ink);
  margin: 0 0 .5rem;
}
.specimen-a {
  font-size: .78rem;
  line-height: 1.6;
  color: var(--ink-2);
  margin: 0;
  padding-left: .7rem;
  border-left: 1px solid var(--ochre-rule);
}
.specimen-ref {
  margin: .55rem 0 0;
  font-family: var(--mono);
  font-size: .57rem;
  letter-spacing: .04em;
  color: var(--ink-3);
}
.specimen-ref b { color: var(--petrol); font-weight: 500; }
.access-panel-head {
  display: flex; justify-content: space-between; align-items: center;
  padding-bottom: .9rem;
  margin-bottom: 1.3rem;
  border-bottom: 1px solid var(--rule);
}
.access-status {
  display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--mono);
  font-size: .55rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: var(--ink-3);
}
.access-status::before {
  content: "";
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--petrol);
}
.access-form-title {
  font-family: var(--serif);
  font-size: 1.72rem;
  font-weight: 400;
  letter-spacing: -.025em;
  margin: 0 0 .2rem;
}
.access-form-sub {
  color: var(--ink-2);
  font-size: .84rem;
  line-height: 1.55;
  margin: 0 0 1rem;
}
.st-key-access-panel [data-testid="stForm"] { border: 0; padding: 0; }
.st-key-access-panel [data-testid="stWidgetLabel"] p {
  font-size: .58rem !important;
  letter-spacing: .14em;
  color: var(--ink-2) !important;
}
.st-key-access-panel [data-testid="stTextInput"] div[data-baseweb="input"] {
  background: var(--paper);
}
.st-key-access-panel [data-testid="stTextInput"] input {
  background: var(--paper) !important;
}
.st-key-access-panel [data-testid="stFormSubmitButton"] button {
  margin-top: .35rem;
  letter-spacing: .02em;
}
.st-key-access-panel [data-testid="stButtonGroup"] {
  background: transparent;
  border-bottom: 1px solid var(--rule);
  border-radius: 0;
  padding: 0;
  margin-bottom: 1.1rem;
}
.st-key-access-panel [data-testid="stButtonGroup"] [role="radiogroup"] {
  gap: 2px;
  width: 100%;
}
.st-key-access-panel [data-testid="stButtonGroup"] button {
  flex: 1;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0 !important;
  background: transparent !important;
  color: var(--ink-3) !important;
  font-family: var(--mono);
  font-size: .61rem;
  letter-spacing: .12em;
  text-transform: uppercase;
  padding: .45rem .5rem;
  margin-bottom: -1px;
  box-shadow: none !important;
}
.st-key-access-panel [data-testid="stButtonGroup"] button[aria-checked="true"] {
  background: transparent !important;
  color: var(--petrol) !important;
  border-bottom-color: var(--ochre) !important;
  box-shadow: none !important;
}
.access-foot {
  margin-top: 1.2rem;
  padding-top: .9rem;
  border-top: 1px dotted var(--rule-strong);
  font-family: var(--mono);
  font-size: .56rem;
  letter-spacing: .08em;
  color: var(--ink-3);
}

/* ── responsive ───────────────────────────────────────── */
@media (max-width: 960px) {
  .masthead { gap: 12px; }
  .masthead-trail { border-left: 0; padding-left: 0; }
  .trail-root { display: none; }
  .masthead-email { max-width: 30vw; }
  .display-title { font-size: 1.8rem; }
  .st-key-sources-panel { min-height: 0; margin-top: 18px; }
  .st-key-chat-body { max-height: none; min-height: 280px; }
  .access-title { max-width: none; }
  .access-brand { margin-bottom: 24px; }
  .access-specimen { max-width: none; }
}
@media (max-width: 640px) {
  .block-container { padding: 0 16px 2.4rem; }
  .masthead { height: 58px; margin-bottom: 20px; }
  .masthead-user .masthead-email,
  .masthead-user .masthead-role { display: none; }
  .chat-head, .page-intro { flex-direction: column; align-items: flex-start; }
  .chat-head { gap: 10px; }
  .chat-title { max-width: 100%; }
  .st-key-chat-body { padding: 18px 16px 8px; }
  .st-key-chat-composer { padding: 12px 14px 10px; }
  .stat { border-right: 0; border-bottom: 1px dotted var(--rule-strong); padding-right: 0; }
  .stat:last-child { border-bottom: 0; }
  .composer-hint span:last-child { display: none; }
}
</style>
"""


def inject():
    st.markdown(CSS, unsafe_allow_html=True)
