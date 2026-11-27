from fastapi import FastAPI, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import admin_required
from backend.api import auth, documents, conversations

app = FastAPI(title="Conversational Document Intelligence Assistant", version="2.1.0")
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(conversations.router)

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if not request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}

@app.get("/system/status", dependencies=[Depends(admin_required)])
def system_status(db: Session = Depends(get_db)):
    return health(db)
