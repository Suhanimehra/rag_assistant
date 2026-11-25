"""Durable PostgreSQL-backed ingestion worker; expired leases are recovered."""
import logging
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_, and_
from backend.database import session_factory
from backend.models import IngestionJob
from backend.services.ingestion import ingest

logger = logging.getLogger(__name__)

def process_one() -> bool:
    now = datetime.now(timezone.utc)
    factory = session_factory()
    with factory() as db:
        job = db.query(IngestionJob).filter(
            or_(IngestionJob.status == "pending",
                and_(IngestionJob.status == "processing", IngestionJob.lease_until < now))
        ).order_by(IngestionJob.id).with_for_update(skip_locked=True).first()
        if not job:
            return False
        if job.attempts >= 3:
            job.status, job.payload, job.error = "failed", None, "Retry limit reached"
            db.commit()
            return True
        job.status = "processing"
        job.attempts += 1
        job.lease_until = now + timedelta(minutes=60)
        job_id, attempt, data, filename = job.id, job.attempts, job.payload, job.filename
        db.commit()
    try:
        with factory() as db:
            document_id, count, _ = ingest(db, data, filename)
        with factory() as db:
            job = db.query(IngestionJob).filter_by(id=job_id, attempts=attempt, status="processing").first()
            if job:
                job.status, job.payload, job.document_id, job.chunk_count = "completed", None, document_id, count
                job.lease_until = None
                db.commit()
    except Exception as exc:
        logger.exception("Ingestion job %s failed", job_id)
        with factory() as db:
            job = db.query(IngestionJob).filter_by(id=job_id, attempts=attempt, status="processing").first()
            if job:
                final = isinstance(exc, ValueError) or attempt >= 3
                job.status = "failed" if final else "pending"
                job.error = "Document ingestion failed"
                if final:
                    job.payload = None
                job.lease_until = None
                db.commit()
    return True

def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            if not process_one():
                time.sleep(2)
        except Exception:
            logger.exception("Worker unavailable; retrying")
            time.sleep(5)

if __name__ == "__main__":
    main()
