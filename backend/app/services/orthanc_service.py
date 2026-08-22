"""Orthanc PACS integration — upload and retrieve DICOM studies."""

import httpx

from app.config import settings

ORTHANC_URL = settings.orthanc_url


def orthanc_auth() -> tuple[str, str]:
    return settings.orthanc_username, settings.orthanc_password


def orthanc_available() -> bool:
    try:
        r = httpx.get(f"{ORTHANC_URL}/system", auth=orthanc_auth(), timeout=3.0)
        return r.status_code == 200
    except Exception:
        return False


def upload_to_orthanc(file_bytes: bytes, filename: str) -> dict:
    """Upload DICOM instance to Orthanc PACS."""
    r = httpx.post(
        f"{ORTHANC_URL}/instances",
        content=file_bytes,
        headers={"Content-Type": "application/dicom"},
        auth=orthanc_auth(),
        timeout=30.0,
    )
    r.raise_for_status()
    return r.json()


def list_orthanc_patients() -> list:
    try:
        r = httpx.get(f"{ORTHANC_URL}/patients", auth=orthanc_auth(), timeout=5.0)
        if r.status_code != 200:
            return []
        patients = []
        for pid in r.json():
            info = httpx.get(
                f"{ORTHANC_URL}/patients/{pid}",
                auth=orthanc_auth(),
                timeout=5.0,
            ).json()
            patients.append({
                "orthanc_id": pid,
                "studies": info.get("Studies", []),
                "type": "orthanc",
            })
        return patients
    except Exception:
        return []


def get_orthanc_status() -> dict:
    available = orthanc_available()
    return {
        "connected": available,
        "url": ORTHANC_URL,
        "message": "Orthanc PACS connected" if available else "Orthanc not reachable — start with: docker compose --profile pacs up",
    }
