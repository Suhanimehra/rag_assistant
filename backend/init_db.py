"""Initialize a NEW database. Existing v1 databases need a separate migration/reindex."""
from sqlalchemy import text, inspect
from backend.database import Base, session_factory
from backend import models

def main():
    engine = session_factory().kw["bind"]
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        inspector = inspect(connection)
        if inspector.has_table("document_chunks"):
            columns = {c["name"] for c in inspector.get_columns("document_chunks")}
            if not {"page", "chunk_index"} <= columns:
                raise RuntimeError("Legacy v1 database detected. Use a new database and reindex your documents; see README.")
        Base.metadata.create_all(connection)
        connection.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version INTEGER NOT NULL DEFAULT 0"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_document_chunks_cosine ON document_chunks USING hnsw (embedding vector_cosine_ops)"))
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_document_chunks_fts ON document_chunks USING gin (to_tsvector('simple', content))"))
if __name__ == "__main__":
    main()
