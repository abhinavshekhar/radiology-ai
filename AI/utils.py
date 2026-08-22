"""
Math, segmentation, and anatomy-recognition utilities for multi-modal radiology AI.

Separation of concerns:
- preprocessing.py  → I/O, windowing, normalization, CLAHE
- utils.py          → voxel math, masks, anatomy classification, volume/mass integration
- modalities.py     → modality-specific inference orchestration
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence, Tuple

import cv2
import numpy as np

from preprocessing import load_image, normalize_to_uint8

# Declared modality codes → expected anatomy label from image content
MODALITY_TO_ANATOMY: dict[str, str] = {
    "XR": "chest_xray",
    "CT": "ct_chest",
    "MR": "mri_brain",
    "US": "us_breast",
}

ANATOMY_TO_MODALITY: dict[str, str] = {v: k for k, v in MODALITY_TO_ANATOMY.items()}

# Approximate soft-tissue density when HU map unavailable (g/mL)
DEFAULT_NODULE_DENSITY_G_PER_ML = 1.05


def voxel_volume_mm3(spacing_mm: Sequence[float]) -> float:
    """Volume of a single voxel: ΔV = Δx · Δy · Δz."""
    dx, dy, dz = (float(spacing_mm[0]), float(spacing_mm[1]), float(spacing_mm[2]))
    return dx * dy * dz


def hu_to_density_g_per_ml(hu: np.ndarray) -> np.ndarray:
    """
    Convert Hounsfield units to physical density (g/mL) relative to water.
    ρ ≈ 1 + HU/1000  (standard CT calibration).
    """
    return 1.0 + np.asarray(hu, dtype=np.float64) / 1000.0


def compute_region_stats(gray: np.ndarray) -> dict[str, float]:
    """
    Region statistics for lesion candidate detection.
    Reused by modality pipelines — do not duplicate in modalities.py.
    """
    h, w = gray.shape[:2]
    roi = gray[int(h * 0.1) : int(h * 0.9), int(w * 0.1) : int(w * 0.9)]
    blur = cv2.GaussianBlur(roi, (9, 9), 0)
    _, bright = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(bright, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 40]
    max_area = max(areas) if areas else 0.0
    return {
        "mean": float(np.mean(roi)),
        "std": float(np.std(roi)),
        "blob_count": float(len(areas)),
        "max_blob": float(max_area),
        "texture": float(np.std(roi)) / 80.0,
    }


def classify_image_anatomy(gray: np.ndarray) -> dict[str, Any]:
    """
    Content-based anatomy / modality recognition from pixel statistics.
    Prevents routing a brain MRI through the chest X-ray DenseNet pipeline.
    """
    h, w = gray.shape[:2]
    roi = gray[int(h * 0.08) : int(h * 0.92), int(w * 0.08) : int(w * 0.92)]
    mean = float(np.mean(roi))
    std = float(np.std(roi))
    dark_ratio = float(np.mean(roi < 70))
    bright_ratio = float(np.mean(roi > 190))

    # Local speckle (ultrasound characteristic)
    lap = cv2.Laplacian(roi, cv2.CV_64F)
    speckle = float(np.std(lap)) / 40.0

    # Central bright mass (MRI / CT nodule)
    cy, cx = roi.shape[0] // 2, roi.shape[1] // 2
    r = min(cy, cx) // 2
    center = roi[cy - r : cy + r, cx - r : cx + r]
    center_bright = float(np.mean(center)) / 255.0
    periphery = roi.copy()
    periphery[cy - r : cy + r, cx - r : cx + r] = int(mean)
    periphery_contrast = abs(float(np.mean(center)) - float(np.mean(periphery))) / 255.0

    # MRI: predominantly dark background with focal hyperintensity
    mri_brain = 0.0
    if dark_ratio >= 0.28:
        mri_brain = min(
            1.0,
            (dark_ratio - 0.2) * 1.2 + center_bright * 0.55 + (1 - mean / 255) * 0.35,
        )

    scores = {
        "mri_brain": mri_brain,
        "us_breast": min(1.0, speckle * 0.55 + (mean / 255) * 0.45 + bright_ratio * 0.2),
        "ct_chest": min(1.0, (1 - dark_ratio) * 0.35 + periphery_contrast * 0.9 + bright_ratio * 0.35),
        "chest_xray": min(
            1.0,
            (1 - dark_ratio) * 0.3
            + (std / 80.0) * 0.4
            + (0.2 if 95 < mean < 175 else 0.0)
            + (1 - speckle) * 0.2,
        ),
    }

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_anatomy, best_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0

    return {
        "anatomy": best_anatomy,
        "confidence": round(best_score, 4),
        "modality": ANATOMY_TO_MODALITY.get(best_anatomy, "XR"),
        "scores": {k: round(v, 4) for k, v in scores.items()},
        "margin": round(best_score - second_score, 4),
    }


def anatomy_blocks_pipeline(modality: str, anatomy_result: dict[str, Any]) -> str | None:
    """
    Return an error message if the image anatomy clearly conflicts with the selected pipeline.
    Prevents e.g. chest X-ray → Brain Tumor when MRI is selected.
    """
    modality = (modality or "XR").upper()
    expected = MODALITY_TO_ANATOMY.get(modality, "chest_xray")
    detected = anatomy_result.get("anatomy", "chest_xray")
    scores = anatomy_result.get("scores", {})
    chest_score = float(scores.get("chest_xray", 0))

    labels = {
        "chest_xray": "chest X-ray",
        "mri_brain": "MRI brain scan",
        "ct_chest": "CT chest scan",
        "us_breast": "breast ultrasound",
    }
    selected = {"XR": "X-Ray (MVP)", "CT": "CT Chest", "MR": "MRI Brain", "US": "Ultrasound"}

    if detected == expected:
        return None

    # Chest X-ray sent through CT/MRI/US pipeline (user's screenshot case)
    if modality in ("MR", "CT", "US") and chest_score >= 0.38:
        if detected == "chest_xray" or chest_score >= float(scores.get(detected, 0)):
            return (
                f"This image is a {labels['chest_xray']}, but you selected {selected.get(modality, modality)}. "
                f"Please switch to **X-Ray (MVP)** or upload the correct {selected.get(modality, modality)} scan."
            )

    # Wrong organ scan on X-ray pipeline
    if modality == "XR" and detected in ("mri_brain", "ct_chest", "us_breast"):
        det_score = float(scores.get(detected, anatomy_result.get("confidence", 0)))
        if det_score >= 0.5:
            correct = ANATOMY_TO_MODALITY.get(detected, "XR")
            return (
                f"This image appears to be a {labels.get(detected, detected)}, not a chest X-ray. "
                f"Please select **{selected.get(correct, correct)}** and analyze again."
            )

    return None


def validate_modality_match(
    declared_modality: str,
    anatomy_result: dict[str, Any],
    filename_hint: str | None = None,
) -> dict[str, Any]:
    """
    Compare user-declared modality with image-content anatomy detection.
    Filename hints reinforce only when consistent with declared modality.
    """
    declared = (declared_modality or "XR").upper()
    expected_anatomy = MODALITY_TO_ANATOMY.get(declared, "chest_xray")
    detected_anatomy = anatomy_result.get("anatomy", "chest_xray")
    detected_modality = anatomy_result.get("modality", "XR")
    confidence = float(anatomy_result.get("confidence", 0.0))
    margin = float(anatomy_result.get("margin", 0.0))

    mismatch = detected_anatomy != expected_anatomy
    strong_signal = confidence >= 0.55 and margin >= 0.08

    # Filename can boost declared modality when demo sample names are explicit
    name = (filename_hint or "").lower()
    filename_modality = None
    if any(k in name for k in ("ct", "nodule", "lidc")):
        filename_modality = "CT"
    elif any(k in name for k in ("mri", "mr_", "brats", "brain", "tumor")):
        filename_modality = "MR"
    elif any(k in name for k in ("us_", "ultrasound", "breast", "busi", "birads")):
        filename_modality = "US"
    elif any(k in name for k in ("pneumonia", "normal", "chest", "xray", "cxr")):
        filename_modality = "XR"

    effective_modality = declared
    warning = None

    # Demo filenames + user selection are authoritative when they agree
    if filename_modality and filename_modality == declared:
        return {
            "declared_modality": declared,
            "detected_anatomy": detected_anatomy,
            "detected_modality": detected_modality,
            "effective_modality": declared,
            "mismatch": mismatch,
            "warning": None,
            "filename_modality": filename_modality,
        }

    # Filename contradicts selected modality — trust filename for demo/orphan uploads
    if filename_modality and filename_modality != declared:
        return {
            "declared_modality": declared,
            "detected_anatomy": detected_anatomy,
            "detected_modality": detected_modality,
            "effective_modality": filename_modality,
            "mismatch": True,
            "warning": (
                f"File appears to be {filename_modality} ({filename_hint}) but {declared} was selected. "
                f"Auto-routed to {filename_modality} organ pipeline."
            ),
            "filename_modality": filename_modality,
        }

    if mismatch and strong_signal and confidence >= 0.72:
        effective_modality = detected_modality
        warning = (
            f"Image content appears to be {detected_anatomy.replace('_', ' ')} "
            f"(confidence {confidence:.0%}) but {declared} was selected. "
            f"Routed to {effective_modality} pipeline for correct organ analysis."
        )
    elif mismatch and not strong_signal:
        warning = (
            f"Selected modality is {declared}; anatomy classifier is uncertain. "
            "Confirm the correct organ/modality for best results."
        )

    return {
        "declared_modality": declared,
        "detected_anatomy": detected_anatomy,
        "detected_modality": detected_modality,
        "effective_modality": effective_modality,
        "mismatch": mismatch,
        "warning": warning,
        "filename_modality": filename_modality,
    }


def segment_lesion_mask(
    gray: np.ndarray,
    modality: str = "CT",
    min_area: int = 36,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Extract a binary lesion mask (2D) for nodule/tumor/lesion candidates.
    Returns mask uint8 {0,1} and bounding box metadata.
    """
    h, w = gray.shape[:2]
    roi = gray[int(h * 0.1) : int(h * 0.9), int(w * 0.1) : int(w * 0.9)]
    y0, x0 = int(h * 0.1), int(w * 0.1)

    if modality == "MR":
        # Hyperintense central lesion on dark background
        blur = cv2.GaussianBlur(roi, (11, 11), 0)
        _, mask = cv2.threshold(blur, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif modality == "US":
        # Hypoechoic lesion: darker blob on bright parenchyma
        blur = cv2.GaussianBlur(roi, (7, 7), 0)
        _, mask = cv2.threshold(blur, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        # CT / XR nodule: bright focal opacity
        blur = cv2.GaussianBlur(roi, (9, 9), 0)
        _, mask = cv2.threshold(blur, 0, 1, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    mask = mask.astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    full = np.zeros((h, w), dtype=np.uint8)
    best = None
    best_area = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        if area > best_area:
            best_area = area
            best = cnt

    if best is not None:
        shifted = best + np.array([[x0, y0]])
        cv2.drawContours(full, [shifted], -1, 1, thickness=-1)
        x, y, bw, bh = cv2.boundingRect(shifted)
        bbox = {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh), "area_px": int(best_area)}
    else:
        bbox = {"x": 0, "y": 0, "width": 0, "height": 0, "area_px": 0}

    return full, bbox


def promote_slice_to_volume(
    slice_mask: np.ndarray,
    slice_hu: np.ndarray | None = None,
    slice_thickness_mm: float = 1.0,
) -> tuple[np.ndarray, np.ndarray | None]:
    """
    Promote a 2D segmentation to a minimal 3D voxel grid (K=1 slice)
    for discrete volumetric integration when only one slice is available.
    """
    mask_3d = slice_mask[np.newaxis, ...].astype(np.uint8)
    hu_3d = None
    if slice_hu is not None:
        hu_3d = np.asarray(slice_hu, dtype=np.float64)[np.newaxis, ...]
    spacing = (slice_thickness_mm, 1.0, 1.0)  # z, y, x — y/x filled by caller
    return mask_3d, hu_3d if hu_3d is None else (mask_3d, hu_3d, spacing)


def compute_volumetric_mass_from_mask(
    mask: np.ndarray,
    voxel_spacing_mm: Tuple[float, float, float] = (1.0, 1.0, 1.0),
    hu_volume: Optional[np.ndarray] = None,
    default_density_g_per_ml: float = DEFAULT_NODULE_DENSITY_G_PER_ML,
) -> dict[str, Any]:
    """
    Discrete triple integration over segmented voxel space:

        V ≈ Σ_{(i,j,k) ∈ Ω} Δx·Δy·Δz
        M ≈ Σ_{(i,j,k) ∈ Ω} ρ(i,j,k) · Δx·Δy·Δz

    where Ω is the set of voxels with mask > 0, and ρ is derived from HU when available.

    Parameters
    ----------
    mask : 2D or 3D binary/array mask (lesion segmentation)
    voxel_spacing_mm : (dz, dy, dx) in millimetres
    hu_volume : optional Hounsfield unit array aligned with mask
    default_density_g_per_ml : fallback tissue density when HU absent
    """
    mask_arr = np.asarray(mask)
    if mask_arr.ndim == 2:
        mask_arr = mask_arr[np.newaxis, ...]

    binary = mask_arr > 0
    n_voxels = int(np.count_nonzero(binary))
    if n_voxels == 0:
        return {
            "volume_mm3": 0.0,
            "mass_g": 0.0,
            "voxel_count": 0,
            "voxel_spacing_mm": tuple(float(s) for s in voxel_spacing_mm),
            "integration_method": "discrete_voxel_sum",
        }

    dz, dy, dx = (float(voxel_spacing_mm[0]), float(voxel_spacing_mm[1]), float(voxel_spacing_mm[2]))
    dv_mm3 = dz * dy * dx
    volume_mm3 = n_voxels * dv_mm3

    if hu_volume is not None:
        hu_vol = np.asarray(hu_volume, dtype=np.float64)
        if hu_vol.ndim == 2:
            hu_vol = hu_vol[np.newaxis, ...]
        rho = hu_to_density_g_per_ml(hu_vol[binary])
        # mass (g) = Σ ρ(g/mL) * volume(mL); 1 mL = 1000 mm³
        mass_g = float(np.sum(rho * (dv_mm3 / 1000.0)))
    else:
        mass_g = float(volume_mm3 / 1000.0 * default_density_g_per_ml)

    # Equivalent spherical diameter from integrated volume
    diameter_mm = float(2.0 * ((3.0 * volume_mm3) / (4.0 * np.pi)) ** (1.0 / 3.0)) if volume_mm3 > 0 else 0.0

    return {
        "volume_mm3": round(volume_mm3, 2),
        "mass_g": round(mass_g, 3),
        "voxel_count": n_voxels,
        "voxel_spacing_mm": (dz, dy, dx),
        "equivalent_diameter_mm": round(diameter_mm, 2),
        "integration_method": "discrete_voxel_sum",
    }


def compute_nodule_volumetric_mass(
    gray: np.ndarray,
    mask: Optional[np.ndarray] = None,
    pixel_spacing_mm: Tuple[float, float] = (0.7, 0.7),
    slice_thickness_mm: float = 1.0,
    default_hu: float = -100.0,
) -> dict[str, Any]:
    """
    End-to-end lung nodule volumetric mass from a CT slice (or 3D mask).

    Uses discrete 3D integration: segments lesion voxels, assigns slice thickness,
    and integrates mass over the voxel lattice.
    """
    if mask is None:
        mask, bbox = segment_lesion_mask(gray, modality="CT")
    else:
        bbox = {}

    # Pseudo-HU map: rescale grayscale to approximate HU for demo slices
    hu_slice = (gray.astype(np.float64) / 255.0) * 400.0 - 200.0

    dz, dy, dx = slice_thickness_mm, pixel_spacing_mm[0], pixel_spacing_mm[1]
    mask_3d = mask[np.newaxis, ...] if mask.ndim == 2 else mask
    hu_3d = hu_slice[np.newaxis, ...] if hu_slice.ndim == 2 else hu_slice

    metrics = compute_volumetric_mass_from_mask(
        mask_3d,
        voxel_spacing_mm=(dz, dy, dx),
        hu_volume=hu_3d,
    )
    metrics["bounding_box"] = bbox
    return metrics


def filename_hint_modality(filename: str | None) -> str | None:
    """Infer intended modality from demo / original filename."""
    name = (filename or "").lower()
    if any(k in name for k in ("ct", "nodule", "lidc")):
        return "CT"
    if any(k in name for k in ("mri", "mr_", "brats", "brain", "tumor")):
        return "MR"
    if any(k in name for k in ("us_", "ultrasound", "breast", "busi", "birads")):
        return "US"
    if any(k in name for k in ("pneumonia", "normal", "chest", "xray", "cxr")):
        return "XR"
    return None


def load_gray_for_analysis(image_path: str) -> np.ndarray:
    """Thin wrapper — always use preprocessing.load_image for I/O."""
    return load_image(image_path)
