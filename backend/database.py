from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:suhani@localhost:5432/rag_users"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


# ✅ Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ✅ ADD THIS FUNCTION (DO NOT REMOVE ANYTHING ABOVE)
def init_db():
    from backend import models   # ⚠️ VERY IMPORTANT (lazy import)
    Base.metadata.create_all(bind=engine)