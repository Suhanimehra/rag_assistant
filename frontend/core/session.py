"""Persistent sign-in helpers.

The backend issues a long-lived bearer token. We keep it in a first-party
cookie so a browser refresh keeps the user signed in, and we clear it on
sign-out. Streamlit can read cookies with ``st.context.cookies``; writing
one needs a small script in a zero-height component iframe.
"""
import json

import streamlit as st
import streamlit.components.v1 as components

COOKIE_NAME = "di_session"
MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days, matching the token lifetime


def stored_token() -> str | None:
    """Return the token saved by a previous visit, if the browser sent one."""
    try:
        return st.context.cookies.get(COOKIE_NAME) or None
    except (AttributeError, KeyError, TypeError):
        return None


def _emit(value: str | None) -> None:
    script = f"""
<script>
(function () {{
  try {{
    var parent = window.parent;
    var secure = parent.location.protocol === "https:" ? "; Secure" : "";
    var value = {json.dumps(value or "")};
    if (value) {{
      parent.document.cookie = "{COOKIE_NAME}=" + value +
        "; path=/; max-age={MAX_AGE_SECONDS}; SameSite=Lax" + secure;
    }} else {{
      parent.document.cookie = "{COOKIE_NAME}=; path=/; max-age=0; SameSite=Lax" + secure;
    }}
  }} catch (err) {{
    /* Cross-origin or sandboxed iframe: nothing else to do. */
  }}
}})();
</script>
"""
    if hasattr(st, "iframe"):
        # A one-pixel iframe is enough to run the script and is visually silent.
        st.iframe(script, height=1)
    else:  # Streamlit before 1.6x
        components.html(script, height=0, scrolling=False)


def remember(token: str) -> None:
    """Persist a freshly issued token in the browser."""
    _emit(token)


def forget() -> None:
    """Remove the persisted token (sign-out or a revoked session)."""
    _emit(None)


def restore() -> bool:
    """Rehydrate ``st.session_state`` from the cookie.

    Returns ``True`` when the stored token is still accepted by the API.
    A network failure leaves the cookie alone so a temporary outage does
    not sign the user out.
    """
    if st.session_state.get("token"):
        return True
    token = stored_token()
    if not token:
        return False

    from core.api import probe_token

    status, profile = probe_token(token)
    if status == "ok":
        st.session_state.token = token
        st.session_state.email = profile.get("email")
        st.session_state.role = profile.get("role", "user")
        return True
    if status == "invalid":
        forget()
    return False
