"""HL7 FHIR R4 stubs for DiagnosticReport + ImagingStudy (hospital integration)."""

from datetime import datetime, timezone


def imaging_study_resource(patient_id: int, study_id: int, modality: str, filename: str) -> dict:
    return {
        "resourceType": "ImagingStudy",
        "id": f"study-{study_id}",
        "status": "available",
        "subject": {"reference": f"Patient/{patient_id}"},
        "started": datetime.now(timezone.utc).isoformat(),
        "modality": [{"system": "http://dicom.nema.org/resources/ontology/DCM", "code": modality}],
        "description": filename,
        "numberOfSeries": 1,
        "numberOfInstances": 1,
    }


def diagnostic_report_resource(patient_id: int, study_id: int, prediction) -> dict:
    return {
        "resourceType": "DiagnosticReport",
        "id": f"report-{study_id}",
        "status": "preliminary",
        "code": {"text": "AI-assisted diagnostic imaging report"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "effectiveDateTime": datetime.now(timezone.utc).isoformat(),
        "conclusion": getattr(prediction, "primary_label", str(prediction)),
        "presentedForm": [{"contentType": "application/pdf", "title": "Radiology AI Report"}],
        "extension": [
            {"url": "https://radiology-ai.local/confidence", "valueDecimal": getattr(prediction, "confidence", 0)},
            {"url": "https://radiology-ai.local/cds-disclaimer",
             "valueString": "Decision support only. Radiologist must finalize."},
        ],
    }
