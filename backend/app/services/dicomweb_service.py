"""DICOMweb QIDO-RS / WADO-RS simulation (Orthanc-compatible)."""

from __future__ import annotations

import httpx

from app.services.orthanc_service import ORTHANC_URL, orthanc_auth

ORTHANC = ORTHANC_URL


def qido_studies(patient_id: str | None = None) -> list[dict]:
    """QIDO-RS: Query studies (DICOMweb)."""
    try:
        params = {}
        if patient_id:
            params["PatientID"] = patient_id
        r = httpx.get(f"{ORTHANC}/dicom-web/studies", params=params, auth=orthanc_auth(), timeout=5.0)
        if r.status_code == 200:
            return r.json() if r.headers.get("content-type", "").startswith("application") else []
        # Fallback Orthanc REST
        r2 = httpx.get(f"{ORTHANC}/studies", auth=orthanc_auth(), timeout=5.0)
        return [{"ID": s} for s in r2.json()] if r2.status_code == 200 else []
    except Exception:
        return []


def wado_study_metadata(study_uid: str) -> dict:
    """WADO-RS: Retrieve study metadata."""
    try:
        r = httpx.get(f"{ORTHANC}/dicom-web/studies/{study_uid}/metadata", auth=orthanc_auth(), timeout=8.0)
        if r.status_code == 200:
            return {"study": study_uid, "metadata": r.json()}
        r2 = httpx.get(f"{ORTHANC}/studies/{study_uid}", auth=orthanc_auth(), timeout=5.0)
        return {"study": study_uid, "metadata": r2.json() if r2.status_code == 200 else {}}
    except Exception as e:
        return {"study": study_uid, "error": str(e), "message": "Start Orthanc: docker compose --profile pacs up -d"}
