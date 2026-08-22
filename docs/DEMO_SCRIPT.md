# HACKATHON DEMO SCRIPT — Read this during presentation (5 minutes)

## Before You Present
1. Double-click `start.bat` — wait for both servers to start
2. Open http://localhost:5173
3. Login: `doctor@radiology.ai` / `demo1234`
4. Have this script open on your phone as backup

---

## MINUTE 1 — Problem (30 sec)
> "India has 1 radiologist per 100,000 people. Rural hospitals wait days for X-ray reports. 
> Misdiagnosis of pneumonia kills 2,500 children daily worldwide. 
> We built an **AI radiology assistant** that helps doctors — not replaces them."

## MINUTE 1 — Solution (30 sec)
> "Upload a chest X-ray. In 5 seconds, our AI gives:
> - Pneumonia detection with 96% confidence
> - Grad-CAM heatmap showing EXACTLY where the infection is
> - Differential diagnosis ranked by probability
> - Auto-generated radiology report with PDF download"

---

## MINUTE 2-3 — LIVE DEMO

### Step 1: Dashboard (15 sec)
- Show the hero banner and metrics
- Say: "Clean clinical dashboard — built for real hospital workflows"

### Step 2: Pneumonia Case (60 sec)
1. Click **Analyze** in nav
2. Click **"Pneumonia Case"** button (auto-fills patient + loads X-ray)
3. Click **"Run AI Analysis"**
4. Watch the pipeline animation: Preprocessing → AI → Grad-CAM → Report
5. Point to results:
   - **"Pneumonia detected, 96% confidence, moderate severity"**
   - **Grad-CAM heatmap**: "Red areas = where AI found infection in lower lobes"
   - **Differential diagnosis**: "Pneumonia 72%, TB 18%, Edema 10%"
   - **Report**: "Auto-generated clinical findings — doctor reviews and approves"
6. Click **Download PDF**

### Step 3: Normal Case (30 sec)
1. Click **"Normal Case"** button
2. Run analysis
3. Say: "Normal — no acute cardiopulmonary process. High confidence."

---

## MINUTE 4 — Tech & Innovation (60 sec)

> "Our stack:"
> - **AI**: DenseNet121 pretrained on 100,000+ chest X-rays (TorchXRayVision)
> - **Explainability**: Grad-CAM — not a black box
> - **Backend**: FastAPI, SQLite, JWT auth, audit logs
> - **Frontend**: React + Tailwind — production-grade UI
> - **PACS-ready**: DICOM upload, Orthanc integration via Docker

> "What makes us different from other teams:"
> 1. We don't just say 'pneumonia detected' — we SHOW WHY with heatmaps
> 2. Differential diagnosis with ranked probabilities
> 3. Severity scoring + 'Needs Human Review' for low confidence
> 4. Full radiology report generation
> 5. Scalable architecture — API gateway → inference server → model registry

---

## MINUTE 5 — Impact & Close (30 sec)

> "This reduces reporting time from 30 minutes to 30 seconds.
> A rural doctor uploads an X-ray, gets AI-assisted findings, 
> and a radiologist reviews remotely. Human stays in control.
>
> We're not building hospital-grade AI overnight — we're building 
> a **clinical decision support system** that augments radiologists.
>
> Thank you. Happy to answer questions."

---

## JUDGE Q&A — Prepared Answers

**Q: How accurate is your model?**
> "We use DenseNet121 pretrained on ChestX-ray14 and NIH datasets — published AUC of 0.84+ for pneumonia. We add confidence thresholds and flag low-confidence cases for human review."

**Q: Can it replace radiologists?**
> "No. This is decision SUPPORT. Every report says 'final interpretation by qualified radiologist required.' The AI assists, the doctor decides."

**Q: What about other diseases?**
> "Architecture supports 18 pathology classes. We focused on pneumonia for this MVP — one polished workflow beats ten unfinished features."

**Q: How do you handle DICOM?**
> "Full DICOM upload with pydicom, windowing, and pixel spacing. Orthanc PACS simulation via Docker for hospital workflow compatibility."

**Q: Is patient data secure?**
> "JWT authentication, role-based access, audit logs for every action. Images stored locally. Production would add encryption and HIPAA compliance."

**Q: How is this scalable?**
> "Microservice architecture: API gateway → inference server → model registry → storage. Celery + Redis for async batch processing. Docker Compose for one-command deployment."

**Q: What's your business model?**
> "SaaS for hospitals — per-scan pricing. Freemium for rural clinics. API licensing for telemedicine platforms."

**Q: What did you build in how many days?**
> "Full end-to-end system in 7 days. We used pretrained models instead of training from scratch, and invested time in UI, explainability, and clinical workflow."

---

## IF SOMETHING BREAKS
- Backend not running? Open terminal: `cd backend && .venv\Scripts\activate && uvicorn app:app --port 8000`
- Frontend not running? `cd frontend && npm run dev`
- Analysis fails? Demo engine works without PyTorch — restart backend
- No demo images? Run `python scripts/download_demo_samples.py`

## BACKUP: Screenshots
Take screenshots of a successful pneumonia analysis BEFORE the presentation as backup slides.
