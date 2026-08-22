# 7-Day Implementation Roadmap

## Day 1 — Foundation
- [x] GitHub repository setup
- [x] FastAPI backend with SQLite
- [x] React frontend with Tailwind
- [x] Image upload (PNG/JPG/DICOM)
- [x] Patient management

## Day 2 — AI Inference
- [x] TorchXRayVision DenseNet121 integration
- [x] Chest X-ray prediction with confidence
- [x] Display results on frontend

## Day 3 — Explainability
- [x] Grad-CAM implementation with Captum hooks
- [x] Heatmap overlay on original image
- [x] Side-by-side visualization

## Day 4 — Reports & Database
- [x] Template-based report generator
- [x] PDF export
- [x] Patient history and prediction storage
- [x] Dashboard metrics

## Day 5 — DICOM & PACS
- [ ] OHIF Viewer or Cornerstone.js integration
- [x] DICOM upload support (pydicom)
- [x] Orthanc PACS Docker profile

## Day 6 — Polish
- [x] Tailwind UI/UX improvements
- [x] JWT authentication
- [x] Chart.js dashboard charts
- [x] PDF download
- [x] Differential diagnosis ranking
- [x] Confidence meter & severity scoring

## Day 7 — Demo Prep
- [ ] End-to-end testing with sample X-rays
- [ ] Record demo video
- [ ] Prepare presentation slides
- [ ] Architecture diagram for judges
- [ ] Q&A preparation

## Judge Pitch (USP)

> "Our platform is an explainable clinical decision-support system that combines AI prediction, visual evidence (Grad-CAM), structured report generation, confidence estimation, and PACS-compatible workflows. It assists radiologists by reducing reporting time while keeping the human expert in control."

## Innovation Highlights

1. **AI Confidence Meter** — Visual confidence with review thresholds
2. **Grad-CAM Explainability** — Highlighted infection areas
3. **Differential Diagnosis** — Ranked probability list
4. **Severity Scoring** — Mild / Moderate / Severe
5. **Uncertainty Flagging** — "Needs Human Review" for low-confidence cases
6. **Auto Report Generation** — Clinical-grade findings + impression
7. **PDF Export** — Downloadable radiology reports
