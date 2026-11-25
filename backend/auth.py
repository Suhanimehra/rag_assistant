from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.config import get_settings
from backend.database import get_db
from backend.models import User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, stored: str) -> bool:
    try:
        return password_hash.verify(password, stored)
    except Exception:
        return False

def create_access_token(user: User) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    return jwt.encode({"sub": str(user.id), "iat": now, "exp": now + timedelta(minutes=settings.access_token_minutes)},
                      settings.jwt_secret.get_secret_value(), algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        claims = jwt.decode(token, get_settings().jwt_secret.get_secret_value(), algorithms=["HS256"],
                            options={"require": ["sub", "exp", "iat"]})
        user = db.get(User, int(claims["sub"]))
        if user is not None:
            return user
    except (jwt.InvalidTokenError, ValueError, TypeError):
        pass
    raise HTTPException(401, "Invalid or expired credentials", headers={"WWW-Authenticate": "Bearer"})

def admin_required(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin access required")
    return user
