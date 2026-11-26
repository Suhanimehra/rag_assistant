from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import get_settings

class Base(DeclarativeBase):
    pass

@lru_cache
def session_factory():
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    with session_factory()() as db:
        yield db
