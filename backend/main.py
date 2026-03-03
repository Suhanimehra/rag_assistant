from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import  OAuth2PasswordRequestForm
from datetime import timedelta
from backend.pdf_utils import extract_text_from_pdf
from backend.vector_store import chunk_text, create_vector_store, save_vector_store ,load_vector_store
from backend.rag import answer_question
from backend.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, admin_required
from pydantic import BaseModel
from backend.database import engine, Base
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User , Document
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

@app.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    new_user = User(
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):

    email = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.email == email).first()


    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": email, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "role": user.role
}

@app.post("/ask")
def ask_question(question: str,user=Depends(get_current_user),db: Session = Depends(get_db)):
    
    # Get latest document
    document = db.query(Document).order_by(Document.id.desc()).first()

    if not document:
        raise HTTPException(400, "No PDF uploaded yet")

    # Load vector store from disk
    vector_store = load_vector_store(document.vector_path)

    answer = answer_question(vector_store, question)

    return {"answer": answer}

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...),admin=Depends(admin_required),db: Session = Depends(get_db)):
    
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("vector_db", exist_ok=True)

    # Save PDF permanently
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text
    with open(file_path, "rb") as pdf_file:
        text = extract_text_from_pdf(pdf_file)

    chunks = chunk_text(text)

    # Create vector store
    vector_store = create_vector_store(chunks)

    # Save vector store permanently
    vector_path = f"vector_db/{file.filename}"
    save_vector_store(vector_store, vector_path)

    # Save metadata in DB
    document = Document(
        filename=file.filename,
        file_path=file_path,
        vector_path=vector_path
    )

    db.add(document)
    db.commit()

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "message": "PDF processed and saved permanently"
    }