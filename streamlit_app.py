import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.title("📄 RAG PDF Assistant")

# ---------------- PDF Upload ----------------

st.header("Upload PDF")

uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

if uploaded_file is not None:
    if st.button("Upload"):
        files = {"file": uploaded_file.getvalue()}

        response = requests.post(f"{API_BASE}/upload", files=files)

        if response.status_code == 200:
            st.success("PDF uploaded successfully!")
        else:
            st.error("Upload failed")

# ---------------- Ask Question ----------------

st.header("Ask Question")

question = st.text_input("Enter your question")

if st.button("Ask"):
    if question.strip() == "":
        st.warning("Please enter a question")
    else:
        response = requests.post(
            f"{API_BASE}/ask",
            params={"question": question}
        )

        if response.status_code == 200:
            answer = response.json()["answer"]
            st.subheader("Answer")
            st.write(answer)
        else:
            st.error("Error getting answer")
