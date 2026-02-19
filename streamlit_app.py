import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="RAG Assistant", layout="centered")

# ---------------- SESSION ----------------

if "token" not in st.session_state:
    st.session_state.token = None

if "role" not in st.session_state:
    st.session_state.role = None


# ---------------- HEADER ----------------

st.title("📄 Role-Based RAG Assistant")


# ---------------- AUTH SECTION ----------------

st.sidebar.title("Authentication")

auth_mode = st.sidebar.radio("Select Mode", ["Login", "Register"])


# ---------- REGISTER ----------

if auth_mode == "Register":

    username = st.sidebar.text_input("Username")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    role = st.sidebar.selectbox("Role", ["user", "admin"])

    if st.sidebar.button("Register"):

        response = requests.post(
            f"{API_BASE}/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "role": role
            }
        )

        if response.status_code == 200:
            st.sidebar.success("Registered successfully")
        else:
            st.sidebar.error(response.text)


# ---------- LOGIN ----------

if auth_mode == "Login":

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):

        response = requests.post(f"{API_BASE}/login",
        data={
            "username": email,
            "password": password
        }
)

        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.role = data["role"]
            st.sidebar.success("Logged in successfully")
        else:
            st.sidebar.error("Invalid credentials")


# ---------------- LOGOUT ----------------

if st.session_state.token:
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.rerun()


# ---------------- MAIN APP ----------------

if st.session_state.token:

    st.success(f"Logged in as **{st.session_state.role}**")

    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # ---------- ADMIN UPLOAD ----------

    if st.session_state.role == "admin":

        st.header("Upload PDF")

        uploaded_file = st.file_uploader("Choose PDF", type=["pdf"])

        if uploaded_file:
            if st.button("Upload PDF"):

                files = {"file": uploaded_file.getvalue()}

                response = requests.post(
                    f"{API_BASE}/upload",
                    headers=headers,
                    files=files
                )

                if response.status_code == 200:
                    st.success("PDF uploaded successfully")
                else:
                    st.error(response.text)


    # ---------- ASK QUESTION ----------

    st.header("Ask Question")

    question = st.text_input("Enter question")

    if st.button("Ask"):

        if question.strip() == "":
            st.warning("Please enter question")
        else:

            response = requests.post(
                f"{API_BASE}/ask",
                headers=headers,
                params={"question": question}
            )

            if response.status_code == 200:
                st.subheader("Answer")
                st.write(response.json()["answer"])
            else:
                st.error(response.text)

else:
    st.info("Please login to continue")
