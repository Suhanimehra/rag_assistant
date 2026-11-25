from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from backend.auth import admin_required, get_current_user
from backend.database import get_db
from backend.config import get_settings
from backend.models import Document, IngestionJob

router = APIRouter(tags=["documents"])

@router.post("/upload", status_code=202)
def upload(file: UploadFile = File(...), admin=Depends(admin_required), db: Session = Depends(get_db)):
    limit = get_settings().max_upload_bytes
    data = file.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, "Document exceeds upload limit")
    name = Path((file.filename or "").replace(chr(92), "/")).name[:255]
    if not name.lower().endswith((".pdf", ".txt", ".md", ".csv")) or not data:
        raise HTTPException(422, "Unsupported or empty document")
    if name.lower().endswith(".pdf") and not data.startswith(b"%PDF-"):
        raise HTTPException(422, "Invalid PDF")
    job = IngestionJob(filename=name, payload=data)
    db.add(job)
    db.commit()
    return {"job_id": job.id, "status": job.status}

@router.get("/ingest/jobs")
def jobs(admin=Depends(admin_required), db: Session = Depends(get_db)):
    return [{"job_id": job.id, "filename": job.filename, "status": job.status,
             "chunks_stored": job.chunk_count, "error": job.error}
            for job in db.query(IngestionJob).order_by(IngestionJob.id.desc()).limit(50).all()]

@router.get("/documents")
def documents(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return [{"id": d.id, "filename": d.filename} for d in db.query(Document).order_by(Document.id.desc()).all()]

@router.delete("/documents/{document_id}")
def delete_document(document_id: int, admin=Depends(admin_required), db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
