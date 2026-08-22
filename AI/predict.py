"""DenseNet121 / CheXNet inference via TorchXRayVision — Day 2."""

from pathlib import Path
from typing import Any

import numpy as np

MODEL_VERSION = "DenseNet121-CheXNet (torchxrayvision-densenet121-res224-all)"
DEMO_MODEL_VERSION = "Demo CV engine (DenseNet fallback)"
_model = None
_pathologies = None
_model_failed = False

LABEL_MAP = {
    "Pneumonia": "Pneumonia",
    "Lung Opacity": "Lung Opacity",
    "Infiltration": "Infiltration",
    "Consolidation": "Consolidation",
    "Atelectasis": "Atelectasis",
    "Effusion": "Pleural Effusion",
    "Edema": "Pulmonary Edema",
    "Mass": "Lung Cancer",
    "Nodule": "Pulmonary Nodule",
    "Cardiomegaly": "Cardiomegaly",
    "No Finding": "Normal",
}


def preload_model():
    """Download and cache model weights on startup."""
    try:
        _load_model()
        print("[AI] DenseNet121 model loaded successfully")
        return True
    except Exception as e:
        print(f"[AI] Model preload failed, using demo engine: {e}")
        return False


def _check_torch_available() -> bool:
    try:
        import torch
        import torchxrayvision  # noqa: F401
        return True
    except Exception:
        return False


def _clear_cached_weights() -> None:
    weights_dir = Path.home() / ".torchxrayvision" / "models_data"
    if not weights_dir.exists():
        return
    for weight_file in weights_dir.glob("*.pt"):
        try:
            weight_file.unlink()
        except OSError:
            pass


def _load_model():
    global _model, _pathologies, _model_failed
    if _model_failed:
        raise RuntimeError("DenseNet weights unavailable")
    if _model is not None:
        return _model, _pathologies
    import torchxrayvision as xrv
    try:
        _model = xrv.models.DenseNet(weights="densenet121-res224-all")
        _model.eval()
        _pathologies = list(_model.pathologies)
        return _model, _pathologies
    except Exception:
        _clear_cached_weights()
        _model_failed = True
        raise


def get_model_info() -> dict:
    if not _check_torch_available():
        return {"loaded": False, "model": "demo-engine", "pathologies": 0}
    try:
        _, pathologies = _load_model()
        return {
            "loaded": True,
            "model": MODEL_VERSION,
            "pathologies": len(pathologies),
            "classes": pathologies,
        }
    except Exception as exc:
        return {
            "loaded": False,
            "model": "demo-engine",
            "pathologies": 12,
            "error": str(exc),
        }


def _get_uncertainty_level(confidence: float) -> str:
    if confidence >= 0.85:
        return "high"
    if confidence >= 0.65:
        return "medium"
    return "needs_review"


def _get_severity(score: float) -> str:
    if score < 0.4:
        return "mild"
    if score < 0.7:
        return "moderate"
    return "severe"


def _build_findings(scores: dict[str, float]) -> list[dict[str, Any]]:
    from conditions import CONDITION_INFO, POSITIVE_THRESHOLD
    findings = []
    for condition, prob in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if condition in ("No Finding", "Normal") or prob < 0.15:
            continue
        label = LABEL_MAP.get(condition, condition)
        info = CONDITION_INFO.get(label, {})
        findings.append({
            "condition": label,
            "probability": round(prob, 3),
            "status": "detected" if prob >= POSITIVE_THRESHOLD else "possible",
            "category": info.get("category", "Other"),
            "urgency": info.get("urgency", "medium"),
        })
    return findings[:8]


def predict_chest_xray(
    processed: np.ndarray,
    image_path: str,
    hint_name: str | None = None,
    modality: str = "XR",
) -> dict:
    if _check_torch_available() and not _model_failed:
        try:
            import torch
            model, pathologies = _load_model()
            tensor = torch.from_numpy(processed).unsqueeze(0).float()

            with torch.no_grad():
                logits = model(tensor)
                probs = torch.sigmoid(logits).squeeze().numpy()
                scores = {pathologies[i]: float(probs[i]) for i in range(len(pathologies))}

                abnormal = {LABEL_MAP.get(k, k): v for k, v in scores.items() if k != "No Finding"}
                no_finding = scores.get("No Finding", 0)

                if no_finding > 0.55 and max(abnormal.values(), default=0) < 0.4:
                    primary, confidence = "Normal", no_finding
                else:
                    top_key = max(abnormal, key=abnormal.get)
                    primary, confidence = top_key, abnormal[top_key]

            all_findings = _build_findings(scores)
            differential = [{"condition": f["condition"], "probability": f["probability"]} for f in all_findings]

            return {
                "primary_label": primary,
                "confidence": round(float(confidence), 4),
                "severity": _get_severity(confidence) if primary != "Normal" else None,
                "uncertainty_level": _get_uncertainty_level(confidence),
                "differential_diagnosis": differential,
                "all_findings": all_findings,
                "model_version": MODEL_VERSION,
                "raw_scores": {k: round(v, 3) for k, v in scores.items()},
            }
        except Exception as exc:
            print(f"[AI] DenseNet inference failed, using demo engine: {exc}")

    from demo_engine import demo_predict
    result = demo_predict(image_path, hint_name=hint_name, modality=modality)
    result["model_version"] = DEMO_MODEL_VERSION
    return result
