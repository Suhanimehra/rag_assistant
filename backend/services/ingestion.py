from hashlib import sha256
from backend.config import get_settings
from backend.models import Document, DocumentChunk
from backend.services.chunking import extract_pages, chunk_pages
from backend.services.embeddings import embedding_model, embed

def ingest(db, data: bytes, filename: str):
    settings = get_settings()
    digest = sha256(data).hexdigest()
    existing = db.query(Document).filter_by(sha256=digest).first()
    if existing:
        return existing.id, db.query(DocumentChunk).filter_by(document_id=existing.id).count(), True
    pages = extract_pages(data, filename)
    chunks = chunk_pages(pages, embedding_model().tokenizer, settings.chunk_tokens, settings.overlap_tokens)
    if not chunks:
        raise ValueError("No indexable content")
    if len(chunks) > 20000:
        raise ValueError("Document exceeds chunk limit")
    document = Document(title=filename, filename=filename, sha256=digest)
    db.add(document)
    db.flush()
    for start in range(0, len(chunks), 64):
        batch = chunks[start:start+64]
        vectors = embed([c.content for c in batch])
        if len(vectors) != len(batch):
            raise RuntimeError("Embedding count mismatch")
        db.add_all([DocumentChunk(document_id=document.id, chunk_index=start+i, page=c.page,
                                  content=c.content, embedding=v) for i, (c,v) in enumerate(zip(batch, vectors))])
    db.commit()
    return document.id, len(chunks), False
