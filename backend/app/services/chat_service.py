"""Radiology AI chat assistant — rule-based clinical knowledge for demo."""

from __future__ import annotations

import re
from typing import Optional

WELCOME = (
    "Hello! I'm your Radiology AI assistant. I can help with:\n"
    "• Understanding AI findings and confidence scores\n"
    "• Grad-CAM explainability\n"
    "• Supported modalities (X-Ray, CT, MRI, Ultrasound)\n"
    "• How to use this platform\n"
    "• General radiology concepts\n\n"
    "What would you like to know?"
)

TOPICS: list[tuple[list[str], str]] = [
    (
        ["grad-cam", "gradcam", "heatmap", "explain", "explainability", "why ai"],
        "Grad-CAM (Gradient-weighted Class Activation Mapping) highlights the image regions "
        "that most influenced the AI's prediction. Warmer colors (red/yellow) indicate areas "
        "the DenseNet121 model focused on when detecting findings like pneumonia or effusion. "
        "This helps radiologists verify whether the AI is looking at clinically relevant anatomy "
        "rather than artifacts. You can generate a Grad-CAM overlay from the Analyze page after running inference.",
    ),
    (
        ["pneumonia", "lung infection", "consolidation"],
        "Pneumonia on chest X-ray typically appears as airspace consolidation — opaque areas "
        "where air in the alveoli is replaced by fluid or pus. Our AI uses DenseNet121 (pretrained "
        "on ChestX-ray14) to screen for pneumonia along with 12+ other chest pathologies. "
        "Always correlate with clinical symptoms, labs, and physical exam. AI output is decision "
        "support, not a final diagnosis.",
    ),
    (
        ["densnet", "densenet", "model", "neural", "deep learning", "ai model", "torch"],
        "We use DenseNet121, a convolutional neural network pretrained on the ChestX-ray14 dataset "
        "via TorchXRayVision. It classifies chest X-rays across multiple pathologies simultaneously. "
        "For CT, MRI, and Ultrasound we use dedicated computer-vision pipelines (nnU-Net, MONAI, "
        "MedSAM paths) as the platform scales to multi-modality imaging.",
    ),
    (
        ["confidence", "score", "threshold", "review"],
        "The confidence score reflects how strongly the model predicts the primary finding (0–100%). "
        "Scores ≥85% are generally high confidence; 65–85% may warrant careful review; below 65% "
        "is flagged as 'Needs Review' on the dashboard. Low confidence can occur with poor image "
        "quality, unusual presentations, or out-of-distribution cases.",
    ),
    (
        ["dicom", "pacs", "orthanc", "dicomweb"],
        "This platform integrates with Orthanc PACS via DICOMweb. Upload studies from the Analyze "
        "page and they sync to PACS when the PACS profile is running. Start PACS with:\n"
        "`docker compose --profile pacs up -d`\n"
        "Orthanc UI: http://localhost:8042 (orthanc / orthanc). DICOM files can be viewed in the "
        "built-in viewer with window/level controls.",
    ),
    (
        ["ct", "computed tomography", "nodule", "lung nodule"],
        "CT Chest analysis targets lung nodule detection (LIDC-style workflow). The pipeline "
        "applies preprocessing, slice analysis, and nodule characterization. Select 'CT Chest' "
        "modality on the Analyze page and upload a CT slice or use the demo case.",
    ),
    (
        ["mri", "mr ", "brain", "tumor", "brats"],
        "MRI Brain analysis focuses on tumor detection and volume estimation (BraTS / MONAI path). "
        "Select 'MRI Brain' on the Analyze page. T1/T2/FLAIR sequences are supported in the "
        "multi-modality roadmap.",
    ),
    (
        ["ultrasound", "us ", "breast", "bi-rads", "birads"],
        "Ultrasound breast analysis provides BI-RADS-style lesion assessment using the BUSI dataset "
        "path. Select 'Ultrasound' modality and upload or use the demo case for breast lesion screening.",
    ),
    (
        ["x-ray", "xray", "chest x", "cxr", "chest ray"],
        "Chest X-Ray is our MVP modality. The AI screens for pneumonia, effusion, cardiomegaly, "
        "atelectasis, pneumothorax, and more. Go to Analyze → select X-Ray → upload an image or "
        "pick a demo case → click Analyze. Results include findings, differential, Grad-CAM, and PDF report.",
    ),
    (
        ["report", "pdf", "download report"],
        "After analysis, click 'Generate PDF Report' to create a structured radiology report with "
        "patient demographics, AI findings, impression, and recommendations. Reports are suitable "
        "for clinical review and can be downloaded from the Analyze results panel.",
    ),
    (
        ["upload", "analyze", "how to", "use app", "how do i", "steps", "workflow"],
        "Quick workflow:\n"
        "1. Go to **Analyze** from the navigation bar\n"
        "2. Enter patient name/age or pick a demo case\n"
        "3. Select modality (X-Ray, CT, MRI, or US)\n"
        "4. Upload an image or DICOM file\n"
        "5. Click **Run Analysis**\n"
        "6. Review findings, Grad-CAM heatmap, and generate a PDF report\n\n"
        "Demo login: doctor@radiology.ai / demo1234",
    ),
    (
        ["patient", "history", "timeline"],
        "The **Patients** page lists registered patients. **History** shows all analyzed studies "
        "with findings and confidence. Patient timelines track study progression over time for "
        "longitudinal follow-up.",
    ),
    (
        ["normal", "negative", "no finding"],
        "A 'Normal' result means the AI did not detect significant pathology above threshold. "
        "This does not rule out all disease — clinical correlation remains essential. Subtle "
        "findings or early-stage disease may be missed.",
    ),
    (
        ["fhir", "hl7", "ehr", "integration"],
        "The platform supports HL7 FHIR for EHR integration (Patient, ImagingStudy, DiagnosticReport "
        "resources). This enables hospital interoperability in production deployments.",
    ),
    (
        ["security", "encrypt", "hipaa", "privacy", "gdpr"],
        "Uploaded images can be encrypted at rest using AES encryption. JWT authentication and "
        "role-based access (doctor, radiologist, admin) protect endpoints. Audit logs track all "
        "actions for compliance. For production, deploy behind hospital VPN and enable full "
        "encryption + audit policies.",
    ),
    (
        ["hello", "hi", "hey", "help", "start"],
        WELCOME,
    ),
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())


def generate_reply(message: str, study_context: Optional[dict] = None) -> str:
    text = _normalize(message)
    if not text:
        return "Please type a question and I'll do my best to help."

    if study_context:
        ctx_reply = _reply_from_study_context(text, study_context)
        if ctx_reply:
            return ctx_reply

    for keywords, answer in TOPICS:
        if any(kw in text for kw in keywords):
            return answer

    if "?" in message or any(w in text for w in ["what", "how", "why", "when", "where", "can", "does", "is"]):
        return (
            "I don't have a specific answer for that yet. Try asking about:\n"
            "• Grad-CAM / AI explainability\n"
            "• Pneumonia or chest X-ray findings\n"
            "• How to upload and analyze scans\n"
            "• CT, MRI, or Ultrasound support\n"
            "• PDF reports or PACS integration\n\n"
            "Or rephrase your question and I'll try again."
        )

    return (
        "I'm here to help with radiology AI questions. You can ask about findings, "
        "how the model works, supported modalities, or how to use this platform. "
        "Type **help** to see what I can answer."
    )


def _reply_from_study_context(text: str, ctx: dict) -> Optional[str]:
    label = ctx.get("primary_label") or ctx.get("label")
    confidence = ctx.get("confidence")
    modality = ctx.get("modality", "XR")

    if any(w in text for w in ["this study", "this result", "my result", "finding", "diagnosis", "what does", "my diagnosis", "patient", "wrong", "mean"]):
        if label and confidence is not None:
            pct = round(float(confidence) * 100, 1)
            return (
                f"For the current study ({modality}): primary finding is {label} "
                f"with {pct}% AI confidence. "
                "Review the Grad-CAM heatmap to see which regions drove this prediction. "
                "Correlate with clinical presentation before finalizing your impression."
            )
    return None
