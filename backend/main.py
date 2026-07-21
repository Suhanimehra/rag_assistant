from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from backend.database import engine, Base, get_db , init_db
from backend.models import (
    User,
    Document,
    DocumentChunk,
    Conversation,
    ConversationMessage
)
from backend.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    admin_required
)
from backend.rag import answer_question
from backend.pdf_utils import extract_text_from_pdf, clean_text
from backend.vector_store import chunk_text
from sentence_transformers import SentenceTransformer

app = FastAPI()

init_db()  # ✅ Initialize DB and create tables

# Load model once
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# -------------------- SCHEMAS --------------------

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"


# -------------------- AUTH APIs --------------------

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    email = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.email == email).first()

    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": email, "role": user.role, "id": user.id},  # ✅ added id
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }


# -------------------- DOCUMENT APIs --------------------

@app.post("/upload")
def upload_pdf(
    file: UploadFile = File(...),
    admin=Depends(admin_required),
    db: Session = Depends(get_db)
):

    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Extract text
    with open(file_path, "rb") as pdf_file:
        text_content = extract_text_from_pdf(pdf_file)

    text_content = clean_text(text_content)  # ✅ important

    # Chunking
    chunks = chunk_text(text_content)

    document = Document(
        title=file.filename,
        filename=file.filename
    )

    db.add(document)
    db.commit()
    db.refresh(document)

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
        "message": "PDF processed and stored"
    }


# -------------------- OLD RAG (KEEP) --------------------

'''@app.post("/ask")
def ask_question(
    question: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    query_embedding = model.encode(question).tolist()

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

    answer = answer_question(context, question)

    return {
        "asked_by": user["role"],
        "question": question,
        "answer": answer
    }'''


# -------------------- CONVERSATION APIs --------------------

@app.get("/conversations/start")
def start_conversation(user=Depends(get_current_user), db: Session = Depends(get_db)):

    # Count existing chats of this user
    count = db.query(Conversation).filter(
        Conversation.user_id == user["id"]
    ).count()

    conversation = Conversation(
        user_id=user["id"],
        title=f"Chat {count + 1}"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at
    }


@app.post("/conversations/chat")
def chat(
    conversation_id: int,
    question: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -------------------- 1️⃣ SAVE USER MESSAGE --------------------
    user_msg = ConversationMessage(
        conversation_id=conversation_id,
        role="user",
        message=question
    )
    db.add(user_msg)
    db.commit()

    # -------------------- 2️⃣ FETCH LAST 5 MESSAGES (MEMORY) --------------------
    history = db.query(ConversationMessage)\
        .filter(ConversationMessage.conversation_id == conversation_id)\
        .order_by(ConversationMessage.id.desc())\
        .limit(5)\
        .all()

    history = history[::-1]  # reverse order

    chat_history = ""
    for msg in history:
        chat_history += f"{msg.role}: {msg.message}\n"

    # -------------------- 3️⃣ VECTOR SEARCH --------------------
    query_embedding = model.encode(question).tolist()

    sql = text("""
        SELECT content
        FROM document_chunks
        ORDER BY embedding <-> CAST(:query_embedding AS vector)
        LIMIT 4
    """)

    results = db.execute(sql, {"query_embedding": query_embedding}).fetchall()

    if not results:
        context = ""
        answer = "Context not found in document"
    else:
        context = "\n".join([row[0] for row in results])

        # -------------------- 4️⃣ COMBINE MEMORY + CONTEXT --------------------
        final_prompt = f"""
Previous Conversation:
{chat_history}

Context:
{context}

Question:
{question}
"""

        answer = answer_question(final_prompt, question)

    # -------------------- 5️⃣ SAVE ASSISTANT MESSAGE --------------------
    bot_msg = ConversationMessage(
        conversation_id=conversation_id,
        role="assistant",
        message=answer
    )
    db.add(bot_msg)
    db.commit()

    return {"answer": answer}


@app.get("/conversations/messages/{conversation_id}")
def get_messages(
    conversation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    messages = db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).all()

    return [
        {"role": msg.role, "message": msg.message}
        for msg in messages
    ]


@app.get("/conversations/list")
def list_conversations(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    conversations = db.query(Conversation).filter(
        Conversation.user_id == user["id"]
    ).all()

    return [
        {
            "id": c.id,
            "title": c.title,
            "created_at": c.created_at
        }
        for c in conversations
    ]


@app.delete("/conversations/delete/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    db.query(ConversationMessage).filter(
        ConversationMessage.conversation_id == conversation_id
    ).delete()

    db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).delete()

    db.commit()

    return {"message": "Conversation deleted"}