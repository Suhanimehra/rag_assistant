from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import timedelta
from backend.pdf_utils import extract_text_from_pdf
from backend.vector_store import chunk_text, create_vector_store
from backend.rag import answer_question
from backend.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, admin_required, fake_users_db
from pydantic import BaseModel
app = FastAPI()

vector_store = None


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

@app.post("/register")
def register(data: RegisterRequest):

    if data.email in fake_users_db:
        raise HTTPException(400, "User already exists")

    fake_users_db[data.email] = {
        "username": data.username,
        "password": data.password,
        "role": data.role
    }

    return {"message": "User registered successfully"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    email = form_data.username
    password = form_data.password

    user = fake_users_db.get(email)

    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": email, "role": user["role"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "role": user["role"]
}



@app.post("/ask")
def ask_question(question: str, user=Depends(get_current_user)):
    global vector_store

    if vector_store is None:
        raise HTTPException(400, "No PDF uploaded yet")

    answer = answer_question(vector_store, question)

    return {"answer": answer}

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...), admin=Depends(admin_required)):
    global vector_store

    text = extract_text_from_pdf(file.file)
    chunks = chunk_text(text)

    vector_store = create_vector_store(chunks)

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "message": "PDF processed and stored"
    }