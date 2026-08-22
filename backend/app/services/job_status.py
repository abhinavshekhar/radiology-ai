"""Redis job-status helpers. Keys: radiology:job:{task_id}. Never store PHI."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

JOB_KEY_PREFIX = "radiology:job"

_client = None


def job_key(task_id: str) -> str:
    return f"{JOB_KEY_PREFIX}:{task_id}"


def _redis():
    global _client
    if _client is None:
        import redis

        _client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _client


def set_job_status(
    task_id: str,
    status: str,
    *,
    study_id: int | None = None,
    error: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    payload: dict[str, Any] = {"status": status, "task_id": task_id}
    if study_id is not None:
        payload["study_id"] = study_id
    if error:
        payload["error"] = error
    if extra:
        for key, value in extra.items():
            if key.lower() in {"patientname", "patientid", "accessionnumber", "patient_name"}:
                continue
            payload[key] = value
    try:
        client = _redis()
        client.setex(
            job_key(task_id),
            int(settings.job_status_ttl_seconds),
            json.dumps(payload),
        )
    except Exception:
        logger.warning("Job status write failed for task %s", task_id)


def get_job_status(task_id: str) -> dict[str, Any] | None:
    try:
        raw = _redis().get(job_key(task_id))
        if not raw:
            return None
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        logger.warning("Job status read failed for task %s", task_id)
        return None
