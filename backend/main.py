from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import admin_required
from backend.api import auth, documents, conversations

app = FastAPI(title="Conversational Document Intelligence Assistant", version="2.0.0")
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(conversations.router)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}

@app.get("/system/status", dependencies=[Depends(admin_required)])
def system_status(db: Session = Depends(get_db)):
    return health(db)
