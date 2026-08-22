"""Grad-CAM explainability using Captum — Day 3."""

from pathlib import Path

import cv2
import numpy as np

from preprocessing import load_image

_model_cache = None


def _get_model():
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    import torchxrayvision as xrv
    model = xrv.models.DenseNet(weights="densenet121-res224-all")
    model.eval()
    _model_cache = model
    return model


def _captum_gradcam(image_path: str, processed: np.ndarray, study_id: int,
                    output_dir: str, target_label: str) -> str:
    import torch
    from captum.attr import LayerGradCam

    model = _get_model()
    pathologies = list(model.pathologies)
    target_layer = model.features.denseblock4

    tensor = torch.from_numpy(processed).unsqueeze(0).float()

    label_map = {p: i for i, p in enumerate(pathologies)}
    reverse_map = {v: k for k, v in {
        "Pneumonia": "Pneumonia", "Tuberculosis": "Infiltration",
        "COVID-19": "Lung Opacity", "Pulmonary Edema": "Edema",
        "Lung Cancer": "Mass", "Normal": "No Finding",
    }.items()}

    pathology_key = reverse_map.get(target_label, target_label)
    if pathology_key not in label_map:
        pathology_key = pathologies[int(torch.sigmoid(model(tensor)).argmax())]

    grad_cam = LayerGradCam(model, target_layer)

    def forward_func(x):
        return torch.sigmoid(model(x))[:, label_map[pathology_key]]

    attributions = grad_cam.attribute(tensor, target=None, attribute_to_layer_input=False)
    cam = attributions.squeeze().detach().numpy()
    if cam.ndim == 3:
        cam = cam.mean(axis=0)
    cam = np.maximum(cam, 0)
    cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

    original = load_image(image_path)
    h, w = original.shape[:2]
    cam_resized = cv2.resize(cam, (w, h))

    heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
    original_bgr = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    overlay = cv2.addWeighted(original_bgr, 0.55, heatmap, 0.45, 0)
    combined = np.hstack([original_bgr, overlay])

    # Add labels
    cv2.putText(combined, "Original", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(combined, f"Grad-CAM: {target_label}", (w + 10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    out_path = Path(output_dir) / f"gradcam_{study_id}.png"
    cv2.imwrite(str(out_path), combined)
    return str(out_path)


def generate_gradcam(
    image_path: str,
    processed: np.ndarray,
    study_id: int,
    output_dir: str,
    target_label: str = "Pneumonia",
) -> str:
    try:
        import torch
        import captum  # noqa: F401
        import torchxrayvision  # noqa: F401
        return _captum_gradcam(image_path, processed, study_id, output_dir, target_label)
    except Exception as e:
        print(f"[GradCAM] Captum failed ({e}), using demo saliency")
        from demo_engine import demo_gradcam
        return demo_gradcam(image_path, study_id, output_dir, target_label)
