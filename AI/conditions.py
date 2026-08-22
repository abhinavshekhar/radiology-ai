"""Supported chest X-ray diagnoses and clinical metadata."""

SUPPORTED_DIAGNOSES = [
    "Pneumonia",
    "Tuberculosis",
    "COVID-19",
    "Pulmonary Edema",
    "Lung Cancer",
    "Pulmonary Nodule",
    "Pleural Effusion",
    "Cardiomegaly",
    "Atelectasis",
    "Consolidation",
    "Pneumothorax",
    "Lung Opacity",
    "Normal",
]

DETECTION_THRESHOLD = 0.25  # Show as "possible"
POSITIVE_THRESHOLD = 0.45   # Show as "detected"

CONDITION_INFO = {
    "Pneumonia": {"category": "Infectious", "urgency": "high", "icon": "🫁"},
    "Tuberculosis": {"category": "Infectious", "urgency": "high", "icon": "🔬"},
    "COVID-19": {"category": "Infectious", "urgency": "high", "icon": "🦠"},
    "Pulmonary Edema": {"category": "Cardiovascular", "urgency": "high", "icon": "💧"},
    "Lung Cancer": {"category": "Oncology", "urgency": "critical", "icon": "⚠️"},
    "Pulmonary Nodule": {"category": "Oncology", "urgency": "medium", "icon": "🔴"},
    "Pleural Effusion": {"category": "Pleural", "urgency": "medium", "icon": "💦"},
    "Cardiomegaly": {"category": "Cardiovascular", "urgency": "medium", "icon": "❤️"},
    "Atelectasis": {"category": "Airway", "urgency": "medium", "icon": "📉"},
    "Consolidation": {"category": "Airspace", "urgency": "high", "icon": "🌫️"},
    "Pneumothorax": {"category": "Pleural", "urgency": "critical", "icon": "🚨"},
    "Lung Opacity": {"category": "Airspace", "urgency": "medium", "icon": "🌁"},
    "Normal": {"category": "Normal", "urgency": "none", "icon": "✅"},
}
