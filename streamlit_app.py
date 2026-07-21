import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Assistant", layout="wide")

# ---------------- SESSION ----------------

if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- HEADER ----------------

st.title("🤖 AI RAG Assistant")

# ---------------- AUTH ----------------

st.sidebar.title("Authentication")

auth_mode = st.sidebar.radio("Mode", ["Login", "Register"])

if auth_mode == "Register":
    username = st.sidebar.text_input("Username")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    role = st.sidebar.selectbox("Role", ["user", "admin"])

    if st.sidebar.button("Register"):
        res = requests.post(f"{API_BASE}/register", json={
            "username": username,
            "email": email,
            "password": password,
            "role": role
        })
        st.sidebar.success("Registered") 
        if res.status_code == 200:
            st.sidebar.success("uploaded")
        
        else:
            st.sidebar.error(res.text)

if auth_mode == "Login":
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        try:
            res = requests.post(
            f"{API_BASE}/login",
            data={
            "username": email,
            "password": password
        }
    )
        except requests.exceptions.ConnectionError:
            st.sidebar.error("Backend not running ❌")
            st.stop()
            
        if res.status_code == 200:
            data = res.json()
            st.session_state.token = data["access_token"]
            st.session_state.role = data["role"]
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")

# ---------------- MAIN APP ----------------

if st.session_state.token:

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # ---------- SIDEBAR: CHAT LIST ----------

    st.sidebar.title("💬 Chats")

    if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
        res = requests.get(f"{API_BASE}/conversations/start", headers=headers)
        if res.status_code == 200:
            chat = res.json()
            st.session_state.current_chat = chat["conversation_id"]
            st.session_state.messages = []
            st.rerun()

    # Load chats
    res = requests.get(f"{API_BASE}/conversations/list", headers=headers)
    if res.status_code == 200:
        chats = res.json()
        for chat in chats:
            if st.sidebar.button(chat["title"], key=f"chat_{chat['id']}"):
                st.session_state.current_chat = chat["id"]

                # load messages
                msg_res = requests.get(
                    f"{API_BASE}/conversations/messages/{chat['id']}",
                    headers=headers
                )
                if msg_res.status_code == 200:
                    st.session_state.messages = msg_res.json()

                st.rerun()

    # ---------- ADMIN PANEL ----------

    if st.session_state.role == "admin":
        st.sidebar.title("📂 Admin")

        uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
        if uploaded_file:
            if st.sidebar.button("Upload" , key="upload_btn"):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                res = requests.post(f"{API_BASE}/upload", headers=headers, files=files)
                st.sidebar.success("Uploaded") if res.status_code == 200 else st.sidebar.error(res.text)

    # ---------- CHAT UI ----------

    if st.session_state.current_chat:

        st.subheader("💬 Chat")

        # Display messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"🧑 **You:** {msg['message']}")
            else:
                st.markdown(f"🤖 **Bot:** {msg['message']}")

        # Input
        question = st.text_input("Type your message...")

        if st.button("Send", key="send_btn"):
            if question.strip():
                res = requests.post(
                    f"{API_BASE}/conversations/chat",
                    headers=headers,
                    params={
                        "conversation_id": st.session_state.current_chat,
                        "question": question
                    }
                )

                if res.status_code == 200:
                    answer = res.json()["answer"]

                    st.session_state.messages.append({
                        "role": "user",
                        "message": question
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "message": answer
                    })

                    st.rerun()
                else:
                    st.error(res.text)

    else:
        st.info("Start a new chat from sidebar")

else:
    st.info("Login to continue")