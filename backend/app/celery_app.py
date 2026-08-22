"""Celery worker: DICOM decrypt/parse, OpenCV preprocess, inference off the API thread."""

from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

from celery import Celery
from celery.exceptions import MaxRetriesExceededError, Retry, SoftTimeLimitExceeded

from app.config import settings

_AI_DIR = Path(__file__).resolve().parent.parent.parent / "AI"
if str(_AI_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_DIR))

logger = logging.getLogger(__name__)

celery_app = Celery(
    "radiology_ai",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    result_expires=settings.job_status_ttl_seconds,
    task_default_retry_delay=15,
)


class NonRetryableProcessingError(Exception):
    """Corrupted/unsupported files or missing studies — do not retry."""


def _filename_hash(name: str | None) -> str:
    raw = (name or "unknown").encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:16]


def _safe_error(exc: BaseException) -> str:
    text = str(exc)
    if any(token in text for token in ("Patient", "Accession", "\\", "/", ".dcm")):
        return f"{type(exc).__name__}: processing failed"
    return f"{type(exc).__name__}: {text[:180]}"


_TASK_OPTS = dict(
    bind=True,
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
    soft_time_limit=540,
    time_limit=600,
)


def _execute_study_pipeline(task, study_id: int) -> dict:
    from app.database import SessionLocal
    from app.services.encryption_service import decrypt_to_temp
    from app.services.job_status import set_job_status
    from app.services.radiology_service import analyze_study
    from app.models.db_models import Study

    set_job_status(task.request.id, "started", study_id=study_id)
    logger.info("Processing study_id=%s task=%s", study_id, task.request.id)

    db = SessionLocal()
    temp_file: Path | None = None
    try:
        study = db.query(Study).filter(Study.id == study_id).first()
        if not study:
            raise NonRetryableProcessingError("Study not found")

        file_hash = _filename_hash(Path(study.file_path).name)
        logger.info("study_id=%s file_hash=%s", study_id, file_hash)

        source = Path(study.file_path)
        readable = str(source)
        if source.suffix == ".enc" or str(source).endswith(".enc"):
            tmp_dir = settings.upload_dir / "tmp"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = decrypt_to_temp(source, tmp_dir)
            readable = str(temp_file)

        is_dicom = study.file_type == "dicom" or Path(readable).suffix.lower() in {".dcm", ".dicom"}
        if is_dicom:
            try:
                from preprocessing import load_image

                pixels = load_image(readable)
                if pixels is None or pixels.size == 0:
                    raise NonRetryableProcessingError("Empty DICOM pixel array")
                logger.info("study_id=%s dicom pixels shape=%s", study_id, tuple(pixels.shape))
            except NonRetryableProcessingError:
                raise
            except Exception as exc:
                raise NonRetryableProcessingError("Unsupported or corrupted DICOM file") from exc

        try:
            result = analyze_study(db, study_id)
        except ValueError as exc:
            raise NonRetryableProcessingError("Analysis failed for unsupported or corrupted file") from exc

        payload = {
            "study_id": study_id,
            "primary_label": result.prediction.primary_label,
            "file_hash": file_hash,
        }
        set_job_status(task.request.id, "success", study_id=study_id, extra={"primary_label": payload["primary_label"]})
        return payload
    except NonRetryableProcessingError as exc:
        set_job_status(task.request.id, "failed", study_id=study_id, error=_safe_error(exc))
        logger.warning("study_id=%s non-retryable: %s", study_id, type(exc).__name__)
        raise
    except SoftTimeLimitExceeded:
        set_job_status(task.request.id, "failed", study_id=study_id, error="Task time limit exceeded")
        logger.warning("study_id=%s hit soft time limit", study_id)
        raise
    except Retry:
        raise
    except Exception as exc:
        logger.warning("study_id=%s retryable error: %s", study_id, type(exc).__name__)
        try:
            set_job_status(task.request.id, "retrying", study_id=study_id, error=_safe_error(exc))
            raise task.retry(exc=exc)
        except MaxRetriesExceededError:
            set_job_status(task.request.id, "failed", study_id=study_id, error=_safe_error(exc))
            raise
    finally:
        if temp_file is not None:
            temp_file.unlink(missing_ok=True)
        db.close()


@celery_app.task(name="process_dicom_upload", **_TASK_OPTS)
def process_dicom_upload(self, study_id: int):
    """Decrypt if needed, parse DICOM with pydicom, OpenCV-preprocess, run inference."""
    return _execute_study_pipeline(self, study_id)


@celery_app.task(name="analyze_study_async", **_TASK_OPTS)
def analyze_study_async(self, study_id: int):
    """Back-compat alias used by POST /predict/{study_id}/async."""
    return _execute_study_pipeline(self, study_id)
