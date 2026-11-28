"""Sign-in / create-account screen."""
import streamlit as st
from core.api import call
from core.state import show_notice
from ui.components import html_block, wordmark_html

HERO = f"""
<div class="access-copy">
  <div class="access-brand">{wordmark_html()}</div>
  <span class="access-kicker">Evidence-first answers</span>
  <h1 class="access-title">Every answer comes with its <em>paper trail</em>.</h1>
  <p class="access-lede">Bring your reports, manuals and meeting notes into one
     searchable desk. Ask questions in plain language and follow every claim back
     to the page that supports it.</p>
  <ol class="access-steps">
    <li><span class="step-num">01</span><div>
      <strong>Gather</strong>
      <span class="step-text">Drop in PDFs, notes and spreadsheets. Indexing runs quietly in the background.</span>
    </div></li>
    <li><span class="step-num">02</span><div>
      <strong>Ask</strong>
      <span class="step-text">Put a question to the whole collection, or narrow the search to a single source.</span>
    </div></li>
    <li><span class="step-num">03</span><div>
      <strong>Verify</strong>
      <span class="step-text">Open the footnote behind each statement and check the original excerpt.</span>
    </div></li>
  </ol>
  <div class="access-specimen">
    <div class="specimen-sheet">
      <span class="specimen-tab">SPECIMEN · EXCERPT</span>
      <p class="specimen-q">“What changed in the Q3 rollout plan?”</p>
      <p class="specimen-a">The launch moved from September to October so the
         rollback drill could run first.</p>
      <p class="specimen-ref">↳ cited in <b>Q3-plan.pdf</b> · p. 4</p>
    </div>
  </div>
</div>
"""


def _sign_in():
    html_block('<div class="access-form-title">Welcome back</div>'
               '<div class="access-form-sub">Sign in to open your reading desk.</div>')
    with st.form("signin_form", border=False):
        email = st.text_input("Email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="Your password")
        submitted = st.form_submit_button("Sign in", type="primary", width="stretch")
    if not submitted:
        return
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
                _remember_token=result["access_token"],
            )
            st.rerun()


def _sign_up():
    html_block('<div class="access-form-title">Create your account</div>'
               '<div class="access-form-sub">A private desk for your team’s documents.</div>')
    with st.form("signup_form", border=False):
        name = st.text_input("Full name", placeholder="Ada Lovelace")
        email = st.text_input("Email", placeholder="you@company.com")
        password = st.text_input("Password", type="password", placeholder="At least 12 characters")
        confirm = st.text_input("Confirm password", type="password", placeholder="Repeat your password")
        submitted = st.form_submit_button("Create account", type="primary", width="stretch")
    if not submitted:
        return
    name, email = name.strip(), email.strip().lower()
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
            result = call("POST", "/register", json={"username": name, "email": email, "password": password})
        if result:
            st.session_state.auth_redirect = "Sign in"
            st.session_state.notice = "Account created. Sign in to continue."
            st.rerun()


def render():
    left, right = st.columns([1.15, 0.85], gap="large", vertical_alignment="center")
    with left:
        html_block(HERO)
    with right, st.container(key="access-panel"):
        html_block(
            '<div class="access-panel-head">'
            '<span class="eyebrow">Member access</span>'
            '<span class="access-status">Secure</span></div>'
        )
        if st.session_state.auth_redirect:
            st.session_state.auth_view = st.session_state.auth_redirect
            st.session_state.auth_redirect = None
        view = st.segmented_control(
            "Authentication",
            ["Sign in", "Create account"],
            key="auth_view",
            label_visibility="collapsed",
            width="stretch",
        ) or "Sign in"
        show_notice()
        _sign_in() if view == "Sign in" else _sign_up()
        html_block('<div class="access-foot">Private workspace · Footnotes on every answer</div>')
