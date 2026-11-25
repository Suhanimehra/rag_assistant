from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.database import get_db
from backend.models import User
from backend.schemas import RegisterRequest
from backend.auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["authentication"])

@router.post("/register", status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = User(username=data.username.strip(), email=str(data.email).lower(),
                password=hash_password(data.password), role="user")
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email is already registered")
    return {"message": "Registered successfully"}

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=form.username.lower()).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role}
