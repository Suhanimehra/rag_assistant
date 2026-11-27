from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend.models import User
from backend.schemas import RegisterRequest
from backend.auth import create_access_token, get_current_user, hash_password, verify_password
from backend.security import (
    client_key, login_ip_limiter, login_limiter, register_ip_limiter, register_limiter,
)

router = APIRouter(tags=["authentication"])

@router.post("/register", status_code=201)
def register(data: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    email = str(data.email).lower()
    register_ip_limiter.check(f"ip:{client_key(request)}")
    register_limiter.check(f"email:{email}")
    user = User(username=data.username, email=email, password=hash_password(data.password), role="user")
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email is already registered")
    return {"message": "Registered successfully"}

@router.post("/login")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username.strip().lower()
    login_ip_limiter.check(f"ip:{client_key(request)}")
    login_limiter.check(f"email:{email}")
    user = db.query(User).filter_by(email=email).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role}

@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.token_version = int(user.token_version or 0) + 1
    db.commit()
    return {"message": "Signed out"}
