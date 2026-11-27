from time import perf_counter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import Conversation, ConversationMessage
from backend.schemas import ChatRequest, ChatResponse, Source
from backend.services.retrieval import retrieve
from backend.services.generation import rewrite_query, generate, FALLBACK
from backend.security import chat_limiter

router = APIRouter(prefix="/conversations", tags=["conversations"])

def owned_conversation(db, conversation_id, user_id):
    conversation = db.query(Conversation).filter_by(id=conversation_id, user_id=user_id).first()
    if not conversation:
        raise HTTPException(404, "Conversation not found")
    return conversation

@router.post("/start", status_code=201)
def start(user=Depends(get_current_user), db: Session = Depends(get_db)):
    chat = Conversation(user_id=user.id)
    db.add(chat)
    db.commit()
    return {"conversation_id": chat.id, "title": chat.title}

@router.get("/list")
def list_conversations(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": c.id, "title": c.title, "created_at": c.created_at}
            for c in db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.id.desc()).all()]

@router.get("/messages/{conversation_id}")
def messages(conversation_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    owned_conversation(db, conversation_id, user.id)
    return [{"role": m.role, "message": m.message, "sources": m.sources or []}
            for m in db.query(ConversationMessage).filter_by(conversation_id=conversation_id).order_by(ConversationMessage.id).all()]

@router.delete("/delete/{conversation_id}")
def delete(conversation_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(owned_conversation(db, conversation_id, user.id))
    db.commit()
    return {"message": "Conversation deleted"}

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    chat_limiter.check(f"user:{user.id}")
    conversation = owned_conversation(db, request.conversation_id, user.id)
    history = db.query(ConversationMessage).filter_by(conversation_id=conversation.id).order_by(
        ConversationMessage.id.desc()).limit(6).all()
    prior = [{"role": m.role, "message": m.message[:1500]} for m in reversed(history)]
    start = perf_counter()
    query = rewrite_query(request.question, prior)
    candidates = retrieve(db, query, request.document_ids)
    retrieval_ms = (perf_counter() - start) * 1000

    # Persist the question before the slow external LLM call. Committing here
    # also releases the read transaction so it does not hold a DB connection
    # open for the duration of the generation request.
    db.add(ConversationMessage(conversation_id=conversation.id, role="user", message=request.question))
    if conversation.title == "New Chat":
        conversation.title = request.question[:80]
    db.commit()

    start = perf_counter()
    try:
        answer = generate(query, candidates)
    except (httpx.HTTPError, KeyError, IndexError, ValueError, TypeError):
        raise HTTPException(503, "Language model temporarily unavailable")
    generation_ms = (perf_counter() - start) * 1000
    insufficient = answer == FALLBACK or not candidates
    sources = [] if insufficient else [Source(source_id=f"S{i}", document_id=c.document_id,
        filename=c.filename, page=c.page, excerpt=c.content[:500], relevance=c.score)
        for i, c in enumerate(candidates, 1)]
    db.add(ConversationMessage(conversation_id=conversation.id, role="assistant", message=answer,
                               sources=[source.model_dump() for source in sources]))
    db.commit()
    return ChatResponse(answer=answer, sources=sources, retrieval_ms=retrieval_ms,
                        generation_ms=generation_ms, insufficient_evidence=insufficient)
