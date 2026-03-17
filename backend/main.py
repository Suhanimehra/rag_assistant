from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from backend.database import engine, Base, get_db
from backend.models import User, Document, DocumentChunk
from backend.auth import (ACCESS_TOKEN_EXPIRE_MINUTES,create_access_token,get_current_user,admin_required)
from backend.rag import answer_question
from backend.pdf_utils import extract_text_from_pdf , clean_text
from backend.vector_store import chunk_text
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

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


@app.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    admin=Depends(admin_required),
    db: Session = Depends(get_db)
):

    # Save file locally
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text from PDF
    with open(file_path, "rb") as pdf_file:
        text_content = extract_text_from_pdf(pdf_file)

    # Create chunks
    chunks = chunk_text(text_content)

    # Save document metadata
    document = Document(
        title=file.filename,
        filename=file.filename
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # Store chunks + embeddings
    for chunk in chunks:

        embedding = model.encode(chunk).tolist()

        db_chunk = DocumentChunk(
            document_id=document.id,
            content=chunk,
            embedding=embedding
        )

        db.add(db_chunk)

    db.commit()

    return {
        "filename": file.filename,
        "chunks_stored": len(chunks),
        "message": "PDF processed and stored with embeddings in database"
    }

@app.post("/ask")
def ask_question(
    question: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Convert question to embedding
    query_embedding = model.encode(question).tolist()

    # Vector similarity search
    sql = text("""
        SELECT content
        FROM document_chunks
        ORDER BY embedding <-> CAST(:query_embedding AS vector)
        LIMIT 4
    """)

    results = db.execute(sql, {"query_embedding": query_embedding}).fetchall()

    if not results:
        raise HTTPException(400, "No documents found")

    context = " ".join([row[0] for row in results])

    # Call Ollama LLM
    answer = answer_question(context, question)

    return {
        "asked_by": user["role"],
        "question": question,
        "answer": answer
    }